from apps.auth.dependencies import User, get_current_user
from apps.core.dependencies import get_async_session
from apps.products.crud import Order, Product, order_manager, product_manager
from fastapi import Body, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

ALLOWED_IMAGE_FILE_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def validate_image(image: UploadFile = File(...)) -> UploadFile:
    if image.content_type not in ALLOWED_IMAGE_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file format"
        )

    file_size = len(await image.read())
    await image.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too big (max {MAX_FILE_SIZE // (1024**2)} MB)",
        )

    return image


async def validate_images(
    images: list[UploadFile] = File(default=None, max_length=10),
) -> list[UploadFile]:
    if not images:
        return []

    if len(images) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No more than 10 files"
        )

    for image in images:
        await validate_image(image)

    return images


async def get_order(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Order:
    return await order_manager.get_or_create(
        session=session, user_id=user.id, is_closed=False
    )


async def get_product(
    product_id: int = Body(ge=1),
    session: AsyncSession = Depends(get_async_session),
) -> Product:
    product = await product_manager.get(
        session=session, field=Product.id, field_value=product_id
    )
    if not product:
        raise HTTPException(
            detail="Product with given id not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return product
