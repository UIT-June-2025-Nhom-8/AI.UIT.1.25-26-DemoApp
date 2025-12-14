"""
Main FastAPI application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api import router
from .services import model_service, llm_service


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting up application...")

    # Load ML models
    try:
        logger.info("Loading ML models...")
        model_service.load_models()
        logger.info(f"Loaded {len(model_service.get_available_models())} models")
    except Exception as e:
        logger.error(f"Failed to load models: {str(e)}")

    # Initialize LLM service (will fail gracefully if token not set)
    try:
        logger.info("Initializing LLM service...")
        llm_service.initialize()
        if llm_service.is_available():
            logger.info("LLM service initialized successfully")
        else:
            logger.warning("LLM service not available (token not set)")
    except Exception as e:
        logger.warning(f"LLM service initialization failed: {str(e)}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for predicting house prices in Vietnam using ML models",
    lifespan=lifespan
)

# Add CORS middleware
# Parse ALLOWED_ORIGINS (can be "*" or comma-separated list)
allowed_origins = ["*"] if settings.ALLOWED_ORIGINS == "*" else [
    origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix=settings.API_V1_PREFIX)


# Root endpoint (without prefix)
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api": settings.API_V1_PREFIX
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
