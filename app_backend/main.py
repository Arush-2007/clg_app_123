from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.logger_config import logger
from routes import api_routes
from contextlib import asynccontextmanager
from utils.prisma import db
from utils.config import DEBUG

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("attempting to connect to db...")
    await db.connect()
    logger.info("connected to db.")
    yield
    logger.info("application stopped.")
    await db.disconnect()
    logger.info("disconnected from db.")

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(api_routes, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "running the server"
    }