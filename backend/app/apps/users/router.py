from apps.auth.dependencies import get_current_user, require_permissions
from apps.core.dependencies import get_async_session
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from .constants import UserPermissionsEnum
from .crud import User, user_manager
from .schemas import RegisteredUserSchema, RegisterUserSchema

router_users = APIRouter()


@router_users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(
    new_user: RegisterUserSchema,
    session: AsyncSession = Depends(get_async_session),
) -> RegisteredUserSchema:
    created_user = await user_manager.create_user(new_user=new_user, session=session)
    return created_user


@router_users.get("/user-info")
async def get_my_info(user: User = Depends(get_current_user)) -> RegisteredUserSchema:
    return RegisteredUserSchema.from_orm(user)


@router_users.get(
    "/{id}",
    dependencies=[Depends(require_permissions([UserPermissionsEnum.CAN_SEE_USERS]))],
)
async def get_user(
    user_id: int = Path(..., description="The id of the user", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> RegisteredUserSchema:
    user: User | None = await user_manager.get(
        session=session, field_value=user_id, field=User.id
    )
    if not user:
        raise HTTPException(
            detail="User with given email not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return RegisteredUserSchema.from_orm(user)
