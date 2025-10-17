from typing import Annotated

from apps.auth.dependencies import require_permissions
from apps.core.dependencies import get_async_session
from apps.core.schemas import SearchParamsSchema
from apps.products.crud import Category, category_manager
from apps.products.schemas import (
    NewCategory,
    PaginatorSavedCategoryResponseSchema,
    SavedCategorySchema,
)
from apps.users.constants import UserPermissionsEnum
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

router_categories = APIRouter()


@router_categories.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_CATEGORY]))
    ],
)
async def create_category(
    new_category: NewCategory,
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategorySchema:
    maybe_category = await category_manager.get(
        field=Category.name, field_value=new_category.name, session=session
    )
    if maybe_category:
        raise HTTPException(
            detail=f"Category with name '{new_category.name}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )

    saved_category = await category_manager.create(
        **new_category.dict(), session=session
    )
    return saved_category


@router_categories.get("/{id}")
async def get_category_by_id(
    category_id: int = Path(..., description="The id of the item", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategorySchema:
    saved_category = await category_manager.get(
        field=Category.id, field_value=category_id, session=session
    )
    if not saved_category:
        raise HTTPException(
            detail=f"Category with id '{category_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return saved_category


@router_categories.get("/")
async def get_categories(
    params: Annotated[SearchParamsSchema, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> PaginatorSavedCategoryResponseSchema:
    result = await category_manager.get_items_paginated(
        session=session,
        search_fields=[Category.name],
        targeted_schema=SavedCategorySchema,
        params=params,
    )
    return result
