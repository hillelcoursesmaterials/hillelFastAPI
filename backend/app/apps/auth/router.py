from apps.core.dependencies import get_async_session
from apps.users.crud import User, user_manager
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

router_auth = APIRouter()


@router_auth.post("/login")
async def user_login(
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_manager.get(
        session=session, field_value=data.username, field=User.email
    )
    if not user:
        raise HTTPException(detail="Not found", status_code=404)

    return {"data": [data.password, data.username]}
