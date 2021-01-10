from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .controllers.browser_router import router as browser
from .controllers.browser_router import openapi_tag as browser_tag
from .controllers.file_input_router import router as file_input
from .controllers.file_input_router import openapi_tag as file_input_tag
from .controllers.google_spell_check_router import router as spell_check
from .controllers.google_spell_check_router import openapi_tag as spell_check_tag
from .settings import get_app_settings


# https://github.com/tiangolo/fastapi/issues/508#issuecomment-532368194
def get_app() -> FastAPI:
    config = get_app_settings()
    openapi_tags = [file_input_tag, browser_tag, spell_check_tag]

    server = FastAPI(
        title = config.FAST_API_TITLE,
        version = config.FAST_API_VERSION,
        description = config.FAST_API_DESCRIPTION,
        openapi_tags = openapi_tags
    )

    # Add controllers
    server.include_router(browser)
    server.include_router(file_input)
    server.include_router(spell_check)

    @server.get("/", include_in_schema = False)
    def redirect_to_docs() -> RedirectResponse:
        return RedirectResponse("/docs")

    # @server.on_event("startup")
    # async def connect_to_database() -> None:
    #     database = get_database()
    #     if not database.is_connected:
    #         await database.connect()

    # @server.on_event("shutdown")
    # async def shutdown() -> None:
    #     database = get_database()
    #     if database.is_connected:
    #         await database.disconnect()

    # To use config.FAST_API_ROOT_PATH = "/api" instead of default "/"
    # app = FastAPI()
    # app.mount(config.FAST_API_ROOT_PATH, server)
    # return app
    return server

app = get_app()
