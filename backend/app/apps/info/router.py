import socket

from fastapi import APIRouter
from services.betterstack_service import betterstack_logger
from settings import settings

from .schemas import BaseBackendInfoSchema, DatabaseInfoSchema

info_router = APIRouter()


@info_router.get("/backend")
async def get_backend_info() -> BaseBackendInfoSchema:
    """Get current backend info"""
    # logging.error(
    #     "some info333",
    #     extra={
    #         "user_id": 123,
    #         "debug_info": {"function": "get_backend_info", "status": "OK"},
    #     },
    # )
    #
    betterstack_logger.info(
        "some info29999",
        extra={
            "user_id": 234,
            "debug_info": {"function": "get_backend_info", "status": "OK"},
        },
    )
    betterstack_logger.error(
        "some info2777",
        extra={
            "user_id": 555,
            "debug_info": {"function": "get_backend_info", "status": "OK"},
        },
    )
    # BaseBackendInfoSchema(**{"backend": socket.gethostname()})
    return {"backend": socket.gethostname(), "another_key": "fake value"}


@info_router.get("/database")
async def get_database_info() -> DatabaseInfoSchema:
    """Get current database info"""
    return DatabaseInfoSchema(database_url=settings.DATABASE_ASYNC_URL)
