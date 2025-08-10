from apps.core.base_crud import BaseCRUDManager
from fastapi import HTTPException, status
from .models import User
from .schemas import RegisterUserSchema
from sqlalchemy.ext.asyncio import AsyncSession
from apps.auth.password_handler import PasswordEncrypt


class UserCRUDManager(BaseCRUDManager):
    def __init__(self):
        self.model = User

    async def create_user(self, new_user: RegisterUserSchema, session: AsyncSession) -> User:
        maybe_user = await self.get(session=session, field=self.model.email, field_value=new_user.email)
        if maybe_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {new_user.email} already exists",
            )

        hashed_password = await PasswordEncrypt.get_password_hash(new_user.password)
        user = await self.create(
            session=session,
            email=new_user.email,
            hashed_password=hashed_password,
            name=new_user.name,
        )
        return user

user_manager = UserCRUDManager()
