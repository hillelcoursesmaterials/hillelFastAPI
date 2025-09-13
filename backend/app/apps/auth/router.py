from apps.core.dependencies import get_async_session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .auth_handler import auth_handler
from .schemas import LoginResponseSchema

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
