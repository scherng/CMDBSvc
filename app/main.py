from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.config.settings import settings
from app.api.endpoints import ingest, data

from app.db.session import create_tables

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CMDB Service...")
    create_tables()
    logger.info("Database tables created/verified")
    yield
    logger.info("Shutting down CMDB Service...")

def setupRouter() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(ingest.router, tags=["ingest"])
    api_router.include_router(data.router, tags=["data"])
    return api_router

def create_application() -> FastAPI:
    
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered backend service for data ingestion, extraction, and normalization",
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(setupRouter())
    
    return app


app = create_application()


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs_url": "/docs",
        "endpoints": {
            "ingest": f"POST /ingest - Ingest raw data",
            "fetch": f"GET /ci/{{id}} - Fetch details by ID"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )