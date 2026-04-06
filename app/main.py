from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine
from app.api.orders import router as orders_router
from app.config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AITI Guru test task запущен")
    yield
    logger.info("AITI Guru test task остановлен")


app = FastAPI(
    title="AITI Guru test task API",
    description="REST API сервис для управления заказами",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(orders_router)

@app.get("/")
def root():
    return {"message": "AITI Guru test task API is running"}

@app.get("/health")
def health_check():
    """Проверка работоспособности приложения + БД"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error("БД недоступна: %s", e)
        return {"status": "error", "database": str(e)}