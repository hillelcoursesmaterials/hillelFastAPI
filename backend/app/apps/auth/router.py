from apps.core.dependencies import get_async_session
from apps.users.crud import User, user_manager
from fastapi import APIRouter, Depends, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .auth_handler import auth_handler
from .dependencies import get_current_user
from .schemas import ForceLogoutSchema, LoginResponseSchema

router_auth = APIRouter()


@router_auth.post("/login")
async def user_login(
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponseSchema:
    login_response: LoginResponseSchema = await auth_handler.get_login_token_pairs(
        session=session, data=data
    )
    return login_response


@router_auth.post("/refresh")
async def refresh_user_token(
    refresh_token: str = Header(alias="X-Refresh-Token"),
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponseSchema:
    token_pair = await auth_handler.get_refresh_token_pair(refresh_token, session)
    return token_pair


@router_auth.post("/force-logout", status_code=status.HTTP_204_NO_CONTENT)
async def force_logout(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    await user_manager.patch(
        user.id, data_to_patch=ForceLogoutSchema(), session=session, exclude_unset=False
    )
