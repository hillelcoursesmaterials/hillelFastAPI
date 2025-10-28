import uuid
from typing import Annotated

from apps.auth.dependencies import require_permissions
from apps.core.dependencies import get_async_session
from apps.core.schemas import SearchParamsSchema
from apps.products.crud import (
    Category,
    Order,
    Product,
    category_manager,
    order_manager,
    order_product_manager,
    product_manager,
)
from apps.products.dependencies import (
    get_order,
    get_product,
    validate_image,
    validate_images,
)
from apps.products.schemas import (
    ModeChangeOrderProductQuantityEnum,
    NewCategory,
    OrderSchema,
    PaginatorSavedCategoryResponseSchema,
    PaginatorSavedProductResponseSchema,
    PatchCategorySchema,
    SavedCategorySchema,
    SavedProductSchema,
)
from apps.users.constants import UserPermissionsEnum
from fastapi import (
    APIRouter,
    Body,
    Depends,
    Form,
    HTTPException,
    Path,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from storage.s3 import s3_storage

router_categories = APIRouter()
router_products = APIRouter()
router_orders = APIRouter()


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


@router_categories.patch(
    "/{id}",
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_CATEGORY]))
    ],
)
async def update_category(
    patch_data: PatchCategorySchema,
    category_id: int = Path(..., description="The id of the item", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategorySchema:
    updated_category = await category_manager.patch(
        instance_id=category_id, data_to_patch=patch_data, session=session
    )
    return updated_category


@router_categories.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_CATEGORY]))
    ],
)
async def delete_category(
    category_id: int = Path(..., description="The id of the item", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
):
    await category_manager.delete_item(instance_id=category_id, session=session)


@router_products.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_PRODUCT]))
    ],
)
async def create_product(
    title: str = Form(min_length=3, max_length=200),
    description: str = Form(min_length=3, max_length=2048),
    price: float = Form(ge=0.01),
    category_id: int = Form(gt=0),
    main_image: UploadFile = Depends(validate_image),
    images: list[UploadFile] = Depends(validate_images),
    session: AsyncSession = Depends(get_async_session),
) -> SavedProductSchema:
    is_category_exists = await category_manager.item_exists(
        field=Category.id, field_value=category_id, session=session
    )
    if not is_category_exists:
        raise HTTPException(
            detail=f"Category with id '{category_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    is_product_exists = await product_manager.item_exists(
        field=Product.title, field_value=title.strip(), session=session
    )
    if is_product_exists:
        raise HTTPException(
            detail=f"Product with title '{title}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )

    product_uuid = uuid.uuid4()
    try:
        main_image_url, *images_urls = await s3_storage.upload_files(
            files=[main_image, *images], uuid_obj=product_uuid
        )
    except Exception:
        # todo: log error here
        raise HTTPException(
            detail="Failed to save files. Call support",
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
        )

    created_product = await product_manager.create(
        title=title.strip(),
        description=description.strip(),
        price=price,
        images=images_urls,
        main_image=main_image_url,
        category_id=category_id,
        session=session,
    )
    return SavedProductSchema.from_orm(created_product)


@router_products.get("/{id}")
async def get_product_by_id(
    product_id: int = Path(..., description="The id of the item", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedProductSchema:
    saved_product = await product_manager.get(
        field=Product.id, field_value=product_id, session=session
    )
    if not saved_product:
        raise HTTPException(
            detail=f"Product with id '{product_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return saved_product


@router_products.get("/")
async def get_products(
    params: Annotated[SearchParamsSchema, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> PaginatorSavedProductResponseSchema:
    result = await product_manager.get_items_paginated(
        session=session,
        search_fields=[Product.title, Product.description],
        targeted_schema=SavedProductSchema,
        params=params,
    )
    return result


@router_orders.get("/")
async def get_current_order(
    order: Order = Depends(get_order),
) -> OrderSchema:
    response = OrderSchema.from_orm(order)
    return response


@router_orders.patch("/change-order-product-quantity")
async def change_order_product_quantity(
    order: Order = Depends(get_order),
    quantity: int = Body(ge=0, default=1),
    mode: ModeChangeOrderProductQuantityEnum = Body(
        default=ModeChangeOrderProductQuantityEnum.INCREASE
    ),
    product: Product = Depends(get_product),
    session: AsyncSession = Depends(get_async_session),
) -> OrderSchema:
    if (
        mode == ModeChangeOrderProductQuantityEnum.DECREASE
        and mode != ModeChangeOrderProductQuantityEnum.SET
    ):
        quantity = -quantity

    is_set_quantity_mode = mode == ModeChangeOrderProductQuantityEnum.SET
    await order_product_manager.change_quantity_and_set_current_price(
        product=product,
        order=order,
        quantity=quantity,
        is_set_quantity_mode=is_set_quantity_mode,
        session=session,
    )

    updated_order = await order_manager.get_order_with_products(
        order_id=order.id, session=session
    )
    return updated_order
