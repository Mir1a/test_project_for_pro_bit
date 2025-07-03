# region -----External Imports-----
import bcrypt
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
# endregion

# region -----Internal Imports-----
from . import query
from ..models import CoreUser, TenantUser, Organization
from .jwt import create_access_token, create_refresh_token, decode_token


# endregion


# region -----Password Functions-----
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# endregion


# region -----Core User Services-----
async def create_core_user(user_data, db_session: AsyncSession):
    existing_user = await query.get_core_user_by_email(user_data.email, db_session)
    if existing_user:
        raise ValueError("Email already registered")

    db_user = CoreUser(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )

    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)

    return db_user


async def authenticate_core_user(email: str, password: str, db_session: AsyncSession):
    user = await query.get_core_user_by_email(email, db_session)

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    if not user.is_active:
        raise ValueError("Account is inactive")

    access_token = create_access_token(data={
        "sub": str(user.id),
        "context": "core",
        "email": user.email
    })

    refresh_token = create_refresh_token(data={
        "sub": str(user.id),
        "context": "core"
    })

    return {
        "success": True,
        "message": "Authentication successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "context": "core"
    }


# endregion


# region -----Organization Services-----
async def create_organization(org_data, owner_id: int, db_session: AsyncSession):
    existing_org = await query.get_organization_by_slug(org_data.slug, db_session)
    if existing_org:
        raise ValueError("Organization with this slug already exists")

    owner = await query.get_core_user_by_id(owner_id, db_session)
    if not owner:
        raise ValueError("Owner not found")

    db_name = f"tenant_{org_data.slug}"

    organization = Organization(
        name=org_data.name,
        slug=org_data.slug,
        description=org_data.description,
        database_name=db_name
    )

    organization.owners.append(owner)

    db_session.add(organization)
    await db_session.commit()
    await db_session.refresh(organization)

    return organization


# endregion


# region -----Tenant User Services-----
async def create_tenant_user(user_data, tenant_slug: str, core_db_session: AsyncSession):
    tenant_session, organization = await get_tenant_session(tenant_slug, core_db_session)

    existing_user = await query.get_tenant_user_by_email(user_data.email, tenant_session)
    if existing_user:
        raise ValueError("Email already registered in this tenant")

    db_user = TenantUser(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        organization_id=organization.id
    )

    tenant_session.add(db_user)
    await tenant_session.commit()
    await tenant_session.refresh(db_user)

    return db_user


async def authenticate_tenant_user(email: str, password: str, tenant_slug: str, core_db_session: AsyncSession):
    tenant_session, organization = await get_tenant_session(tenant_slug, core_db_session)

    user = await query.get_tenant_user_by_email(email, tenant_session)

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    if not user.is_active:
        raise ValueError("Account is inactive")

    access_token = create_access_token(data={
        "sub": str(user.id),
        "context": "tenant",
        "tenant": tenant_slug,
        "org_id": organization.id,
        "email": user.email
    })

    refresh_token = create_refresh_token(data={
        "sub": str(user.id),
        "context": "tenant",
        "tenant": tenant_slug,
        "org_id": organization.id
    })

    return {
        "success": True,
        "message": "Authentication successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "context": "tenant"
    }


async def get_tenant_user_profile(user_id: int, tenant_slug: str, core_db_session: AsyncSession):
    tenant_session, _ = await get_tenant_session(tenant_slug, core_db_session)

    user = await query.get_tenant_user_by_id(user_id, tenant_session)
    if not user:
        raise ValueError("User not found")

    return user


async def update_tenant_user_profile(user_id: int, update_data, tenant_slug: str, core_db_session: AsyncSession):
    tenant_session, _ = await get_tenant_session(tenant_slug, core_db_session)

    user = await query.get_tenant_user_by_id(user_id, tenant_session)
    if not user:
        raise ValueError("User not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()

    await tenant_session.commit()
    await tenant_session.refresh(user)

    return user


# endregion


# region -----Helper Functions-----
async def get_tenant_session(tenant_slug: str, core_db_session: AsyncSession):
    organization = await query.get_organization_by_slug(tenant_slug, core_db_session)
    if not organization:
        raise ValueError("Tenant not found")

    return core_db_session, organization


async def refresh_access_token(refresh_token_str: str, db_session: AsyncSession):
    try:
        payload = decode_token(refresh_token_str)
    except ValueError:
        raise ValueError("Invalid or expired refresh token")

    user_id = payload.get("sub")
    context = payload.get("context")

    if not user_id or not context:
        raise ValueError("Invalid token payload")

    if context == "core":
        user = await query.get_core_user_by_id(int(user_id), db_session)
        token_data = {
            "sub": str(user.id),
            "context": "core",
            "email": user.email
        }
    elif context == "tenant":
        tenant_slug = payload.get("tenant")
        org_id = payload.get("org_id")

        if not tenant_slug or not org_id:
            raise ValueError("Invalid tenant token payload")

        tenant_session, _ = await get_tenant_session(tenant_slug, db_session)
        user = await query.get_tenant_user_by_id(int(user_id), tenant_session)

        token_data = {
            "sub": str(user.id),
            "context": "tenant",
            "tenant": tenant_slug,
            "org_id": org_id,
            "email": user.email
        }
    else:
        raise ValueError("Invalid context")

    if not user or not user.is_active:
        raise ValueError("User not found or inactive")

    access_token = create_access_token(data=token_data)

    return {"access_token": access_token}
# endregion
