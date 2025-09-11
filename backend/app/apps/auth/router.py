from apps.core.dependencies import get_async_session
from apps.users.crud import user_manager
from apps.users.models import User
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import LoginResponseSchema

router_auth = APIRouter()


@router_auth.post("/login")
async def user_login(
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponseSchema:
    user = await user_manager.get(
        field=User.email, field_value=data.username, session=session
    )
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with email {data.username} not found"
        )

    return LoginResponseSchema(
        access_token="token1", refresh_token="token2", expires_at=12
    )
