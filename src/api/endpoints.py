# region -----External Imports-----
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
# endregion

# region -----Internal Imports-----
from . import schemas, services
from ..database import get_async_session
from ..security import get_current_core_user_id, get_current_tenant_user_id

# endregion

router = APIRouter()


# region -----Helper Functions-----
def get_tenant_context(x_tenant: Optional[str] = Header(None)) -> Optional[str]:
    return x_tenant


# endregion


# region -----Registration Endpoints-----
@router.post("/auth/register")
async def register_user(
        user_data: schemas.CoreUserCreate,
        tenant_context: Optional[str] = Depends(get_tenant_context),
        db_session: AsyncSession = Depends(get_async_session)
):
    try:
        if tenant_context:
            tenant_user_data = schemas.TenantUserCreate(**user_data.model_dump())
            user = await services.create_tenant_user(tenant_user_data, tenant_context, db_session)
            return schemas.TenantUserResponse.model_validate(user)
        else:
            user = await services.create_core_user(user_data, db_session)
            return schemas.CoreUserResponse.model_validate(user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


# endregion


# region -----Authentication Endpoints-----
@router.post("/auth/login", response_model=schemas.AuthResponse)
async def login(
        login_data: schemas.LoginRequest,
        tenant_context: Optional[str] = Depends(get_tenant_context),
        db_session: AsyncSession = Depends(get_async_session)
):
    try:
        if tenant_context:
            result = await services.authenticate_tenant_user(
                login_data.email,
                login_data.password,
                tenant_context,
                db_session
            )
        else:
            result = await services.authenticate_core_user(
                login_data.email,
                login_data.password,
                db_session
            )

        return schemas.AuthResponse(**result)

    except ValueError as e:
        if "Invalid credentials" in str(e):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        elif "Account is inactive" in str(e):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        elif "Tenant not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


@router.post("/auth/refresh", response_model=schemas.AccessToken)
async def refresh_token(
        refresh_data: schemas.RefreshTokenRequest,
        db_session: AsyncSession = Depends(get_async_session)
):
    try:
        result = await services.refresh_access_token(refresh_data.refresh_token, db_session)
        return schemas.AccessToken(**result)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh error: {str(e)}")


# endregion


# region -----Organization Endpoints-----
@router.post("/organizations", response_model=schemas.OrganizationResponse)
async def create_organization(
        org_data: schemas.OrganizationCreate,
        user_id: int = Depends(get_current_core_user_id),
        db_session: AsyncSession = Depends(get_async_session)
):
    try:
        organization = await services.create_organization(org_data, user_id, db_session)
        return schemas.OrganizationResponse.model_validate(organization)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Organization creation error: {str(e)}")


# endregion


# region -----User Profile Endpoints-----
@router.get("/users/me")
async def get_user_profile(
        user_context: tuple = Depends(get_current_tenant_user_id),
        tenant_context: Optional[str] = Depends(get_tenant_context),
        db_session: AsyncSession = Depends(get_async_session)
):
    try:
        user_id, token_tenant = user_context

        if not tenant_context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-TENANT header required"
            )

        if token_tenant != tenant_context:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token tenant does not match request tenant"
            )

        user = await services.get_tenant_user_profile(user_id, tenant_context, db_session)
        return schemas.TenantUserResponse.model_validate(user)

    except ValueError as e:
        if "User not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile retrieval error: {str(e)}")


@router.put("/users/me")
async def update_user_profile(
        update_data: schemas.TenantUserUpdate,
        user_context: tuple = Depends(get_current_tenant_user_id),
        tenant_context: Optional[str] = Depends(get_tenant_context),
        db_session: AsyncSession = Depends(get_async_session)
):
    try:
        user_id, token_tenant = user_context

        if not tenant_context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-TENANT header required"
            )

        if token_tenant != tenant_context:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token tenant does not match request tenant"
            )

        user = await services.update_tenant_user_profile(user_id, update_data, tenant_context, db_session)
        return schemas.TenantUserResponse.model_validate(user)

    except ValueError as e:
        if "User not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update error: {str(e)}")
# endregion
