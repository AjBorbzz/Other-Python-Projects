from fastapi import FastAPI
from app.core.config import settings
from app.routes import health, summarize


app = FastAPI(title=settings.APP_NAME, version="0.1.0")


app.include_router(health.router, prefix="/health")
app.include_router(summarize.router, prefix="/summarize")