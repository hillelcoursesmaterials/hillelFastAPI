from fastapi import File, HTTPException, UploadFile, status

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
