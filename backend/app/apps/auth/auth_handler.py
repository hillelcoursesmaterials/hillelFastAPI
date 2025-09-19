import datetime as dt
from uuid import uuid4

import jwt
from apps.users.crud import User, user_manager
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from services.redis_service import redis_service
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

        tokens_response = await self.generate_tokens(user)
        return tokens_response

    async def generate_tokens(self, user: User) -> LoginResponseSchema:
        access_token_payload = {
            "sub": str(user.id),
            "email": user.email,
        }
        access_token = await self.generate_token(
            access_token_payload, self.access_token_lifetime
        )

        refresh_token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "key": uuid4().hex,
        }
        refresh_token = await self.generate_token(
            refresh_token_payload, self.refresh_token_lifetime
        )
        await redis_service.set_cache(
            key=refresh_token_payload["key"],
            value=user.id,
            ttl=self.refresh_token_lifetime * 60,
        )

        return LoginResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            expired_at=self.access_token_lifetime * 60,
        )

    async def generate_token(self, payload: dict, expire_minutes: int) -> str:
        now = dt.datetime.now()
        token_expires_at = dt.timedelta(minutes=expire_minutes)
        time_payload = {"exp": now + token_expires_at, "iat": now}
        payload.update(time_payload)
        print(payload)
        token_ = jwt.encode(payload, self.jwt_secret, self.jwt_algorithm)
        print(token_)
        return token_

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.jwt_secret, [self.jwt_algorithm])
            payload["iat"] = dt.datetime.fromtimestamp(payload.get("iat") or 0)
            return payload
        except jwt.InvalidTokenError:
            raise HTTPException(
                detail="Invalid token", status_code=status.HTTP_400_BAD_REQUEST
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                detail="Time is out", status_code=status.HTTP_401_UNAUTHORIZED
            )

    async def get_refresh_token_pair(
        self, refresh_token: str, session: AsyncSession
    ) -> LoginResponseSchema:
        payload = await self.decode_token(refresh_token)

        stored_refresh = await redis_service.get_cache(payload["key"])
        if not stored_refresh:
            raise HTTPException(
                detail="Token was used already", status_code=status.HTTP_404_NOT_FOUND
            )

        await redis_service.delete_cache(payload["key"])
        user = await user_manager.get(
            session=session, field_value=int(payload["sub"]), field=User.id
        )
        if not user:
            raise HTTPException(
                detail="User not found", status_code=status.HTTP_404_NOT_FOUND
            )

        token_pair = await self.generate_tokens(user)
        return token_pair


auth_handler = AuthHandler()
