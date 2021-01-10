import os

import uvicorn

from app import app

if __name__ == "__main__":
    # Setting reload to True forces server to run with single worker
    uvicorn.run("main:app", host = "0.0.0.0", port = 8000, workers = os.cpu_count(), reload = True)
