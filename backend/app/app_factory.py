from fastapi import FastAPI, Request

from scalar_fastapi import get_scalar_api_reference

from settings import settings

from apps.info.router import info_router
from apps.users.router import router_users
import sentry_sdk

sentry_sdk.init(
    dsn=settings.SENTRY_DNS,
    send_default_pii=True,
)

def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        root_path="/api",
    )
    app.include_router(router_users, prefix="/users", tags=["Users"])

    if settings.DEBUG:
        app.include_router(info_router, prefix="/info", tags=["INFO"])

    @app.get("/scalar", include_in_schema=False)
    async def scalar_html(request: Request):
        return get_scalar_api_reference(
            openapi_url=request.scope.get("root_path", "") + app.openapi_url,
            title=app.title,
        )

    return app
