from apps.users.crud import User, user_manager
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession

from .password_handler import PasswordEncrypt
from .schemas import LoginResponseSchema


class AuthHandler:
    def __init__(self):
        self.access_token_lifetime = settings.ACCESS_TOKEN_TIME_MINUTES
        self.refresh_token_lifetime = settings.REFRESH_TOKEN_TIME_MINUTES
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.jwt_secret = settings.JWT_SECRET

    async def get_login_token_pairs(
        self, session: AsyncSession, data: OAuth2PasswordRequestForm
    ) -> LoginResponseSchema:
        user: User | None = await user_manager.get(
            session=session, field_value=data.username, field=User.email
        )
        if not user:
            raise HTTPException(
                detail="User with given email not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        is_valid_password = await PasswordEncrypt.verify_password(
            plain_password=data.password, hashed_password=user.hashed_password
        )
        if not is_valid_password:
            raise HTTPException(
                detail="Incorrect password", status_code=status.HTTP_403_FORBIDDEN
            )

        return LoginResponseSchema(
            access_token="access_token", refresh_token="refresh_token", expired_at=123
        )


auth_handler = AuthHandler()
