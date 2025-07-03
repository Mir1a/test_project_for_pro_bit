# region -----External Imports-----
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Tuple
import jwt
import os
# endregion

# region -----Internal Imports-----
from .database import get_async_session
from .api import query

# endregion

# region -----Supporting Variables-----
security = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


# endregion


async def get_current_user_context(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db_session: AsyncSession = Depends(get_async_session)
) -> Tuple[int, str, Optional[str]]:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_id_str = payload.get("sub")
    context = payload.get("context")

    if not user_id_str or not context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

    if context == "core":
        user = await query.get_core_user_by_id(user_id, db_session)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        return user_id, context, None

    elif context == "tenant":
        tenant_slug = payload.get("tenant")
        org_id = payload.get("org_id")

        if not tenant_slug or not org_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid tenant token payload"
            )

        organization = await query.get_organization_by_slug(tenant_slug, db_session)
        if not organization or organization.id != org_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid tenant in token"
            )

        return user_id, context, tenant_slug

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid context in token"
        )


async def get_current_core_user_id(
        context_data: Tuple = Depends(get_current_user_context)
) -> int:
    user_id, context, _ = context_data

    if context != "core":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Core user required"
        )

    return user_id


async def get_current_tenant_user_id(
        context_data: Tuple = Depends(get_current_user_context)
) -> Tuple[int, str]:
    user_id, context, tenant_slug = context_data

    if context != "tenant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Tenant user required"
        )

    if not tenant_slug:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing tenant information"
        )

    return user_id, tenant_slug


async def verify_organization_owner(
        organization_id: int,
        user_id: int = Depends(get_current_core_user_id),
        db_session: AsyncSession = Depends(get_async_session)
) -> bool:
    is_owner = await query.check_organization_owner(user_id, organization_id, db_session)

    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Organization owner required"
        )

    return True
