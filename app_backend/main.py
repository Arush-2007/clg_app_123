# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from utils.logger_config import logger
# from routes import api_routes
# from contextlib import asynccontextmanager
# from utils.prisma import db
# from utils.config import DEBUG
# import sys
# from pathlib import Path

# # Ensure project root is in Python path
# project_root = Path(__file__).parent
# if str(project_root) not in sys.path:
#     sys.path.insert(0, str(project_root))

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("attempting to connect to db...")
#     await db.connect()
#     logger.info("connected to db.")
#     yield
#     logger.info("application stopped.")
#     await db.disconnect()
#     logger.info("disconnected from db.")

# app = FastAPI(lifespan=lifespan)
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# app.include_router(api_routes, prefix="/api")

# @app.get("/")
# async def root():
#     return {
#         "message": "running the server"
#     }

import sys
import os
from pathlib import Path

# Add project root to Python path to ensure modules are found
current_file = Path(__file__).resolve()
project_root = current_file.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.logger_config import logger
from routes import api_routes
# from routes.api_routes import router as api_routes
from routes import router as api_routes
from contextlib import asynccontextmanager
from utils.prisma import db
from utils.config import DEBUG

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Attempting to connect to db...")
    await db.connect()
    logger.info("Connected to db.")
    yield
    logger.info("Application stopping...")
    await db.disconnect()
    logger.info("Disconnected from db.")

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Include API routes
app.include_router(api_routes, prefix="/api")

@app.get("/")
async def root():
    return {"message": "running the server"}
