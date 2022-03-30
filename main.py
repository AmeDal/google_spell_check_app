import uvicorn

from app import app
from app.settings import get_app_settings

config = get_app_settings()

if __name__ == "__main__":

    # Setting reload to True forces server to run with single worker
    uvicorn.run("main:app",
                host = config.FAST_API_HOST,
                port = config.FAST_API_PORT,
                workers = config.FAST_API_WORKERS,
                reload = config.FAST_API_RELOAD)
