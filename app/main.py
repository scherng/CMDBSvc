from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.config.settings import settings
from app.api.endpoints import ingest, data
from app.db.db_factory import DatabaseFactory, DatabaseType

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CMDB Service...")
    try:
        # Initialize database based on configuration
        db_type = DatabaseType(settings.database_type.lower())

        if db_type == DatabaseType.MONGODB:
            connection_string = settings.mongodb_url
        else:
            # For in-memory database, connection string is not used
            connection_string = ""

        DatabaseFactory.initialize(db_type, connection_string, settings.database_name)
        logger.info(f"Database connection established with type: {db_type}")

    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    yield
    DatabaseFactory.disconnect()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )