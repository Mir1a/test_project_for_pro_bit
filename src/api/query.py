# region -----External Imports-----
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
# endregion

# region -----Internal Imports-----
from ..models import CoreUser, Organization, TenantUser
# endregion


# region -----Core Database Queries-----
async def get_core_user_by_id(user_id: int, db_session: AsyncSession):
    query = select(CoreUser).filter(CoreUser.id == user_id)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_core_user_by_email(email: str, db_session: AsyncSession):
    query = select(CoreUser).filter(CoreUser.email == email)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_organization_by_slug(slug: str, db_session: AsyncSession):
    query = select(Organization).filter(Organization.slug == slug, Organization.is_active == True)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_organization_by_id(org_id: int, db_session: AsyncSession):
    query = select(Organization).filter(Organization.id == org_id, Organization.is_active == True)
    result = await db_session.execute(query)
    return result.scalars().first()


async def check_organization_owner(user_id: int, org_id: int, db_session: AsyncSession):
    query = select(Organization).filter(
        Organization.id == org_id,
        Organization.owners.any(CoreUser.id == user_id)
    )
    result = await db_session.execute(query)
    return result.scalars().first() is not None


async def get_user_organizations(user_id: int, db_session: AsyncSession):
    query = select(Organization).filter(
        Organization.owners.any(CoreUser.id == user_id),
        Organization.is_active == True
    )
    result = await db_session.execute(query)
    return result.scalars().all()
# endregion


# region -----Tenant Database Queries-----
async def get_tenant_user_by_id(user_id: int, db_session: AsyncSession):
    query = select(TenantUser).filter(TenantUser.id == user_id)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_tenant_user_by_email(email: str, db_session: AsyncSession):
    query = select(TenantUser).filter(TenantUser.email == email)
    result = await db_session.execute(query)
    return result.scalars().first()


async def check_tenant_user_email_exists(email: str, user_id: int, db_session: AsyncSession):
    query = select(TenantUser).filter(
        TenantUser.email == email,
        TenantUser.id != user_id
    )
    result = await db_session.execute(query)
    return result.scalars().first() is not None
# endregion
