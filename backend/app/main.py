from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import classify
from app.services.classifier import get_classifier


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application lifespan handler.
    Loads the model on startup, cleans up on shutdown.
    """
    print("Starting EchoCheck API")
    print("Loading model from HuggingFace")

    get_classifier()

    yield

    print("Shutting down EchoCheck API")


app = FastAPI(
    title="EchoCheck API",
    description="Political stance classification API using RoBERTa-based model",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware, replace with frontend URL in production TODO

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(classify.router, prefix="/api", tags=["classification"])


@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "name": "EchoCheck API",
        "version": "1.0.0",
        "description": "Political stance classification API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    classifier = get_classifier()
    return {
        "status": "healthy",
        "model_loaded": classifier is not None,
        "model_name": "alxdev/echocheck-political-stance",
    }
