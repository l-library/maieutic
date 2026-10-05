from fastapi import FastAPI

from app.api.v1.router import api_router as v1_router
from app.core.log_setup import setup_log

app = FastAPI()


app.include_router(v1_router, prefix="/api/v1")


setup_log()


@app.get("/")
def check_health():
    return {"status": "ok", "message": "Maieutic 服务已就绪"}
