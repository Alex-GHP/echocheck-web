from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import auth, classify
from app.services.classifier import get_classifier
from app.services.database import database
from app.services.users import get_user_service
from app.services.verification import get_verification_service


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application lifespan handler
    Loads the model and connects to database on startup
    Cleans up on shutdown
    """
    settings = get_settings()
    print(f"Starting {settings.api_title}")

    print("Loading model from HuggingFace")
    get_classifier()

    try:
        await database.connect()

        user_service = get_user_service()
        verification_service = get_verification_service()
        await user_service.setup_indexes()
        await verification_service.setup_indexes()

    except Exception as e:
        print(f"Could not connect to MongoDB: {e}. API will run without database")

    yield

    await database.disconnect()
    print(f"Shutting down {settings.api_title}")


settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    description="Political stance classification API using RoBERTa-based model",
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware, replace with frontend URL in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(classify.router, prefix="/api", tags=["classification"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])


@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": "Political stance classification API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    classifier = get_classifier()
    db_connected = database.db is not None

    return {
        "status": "healthy" if classifier and db_connected else "degraded",
        "model_loaded": classifier is not None,
        "model_name": settings.hf_model_name,
        "database_connected": db_connected,
    }
