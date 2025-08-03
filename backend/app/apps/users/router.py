from fastapi import APIRouter, status

from .schemas import RegisterUserSchema, RegisteredUserSchema
from apps.auth.password_handler import PasswordEncrypt

router_users = APIRouter()


@router_users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(new_user: RegisterUserSchema) -> RegisteredUserSchema:
    created_user = RegisteredUserSchema(id=8765776, **new_user.dict())
    return created_user
