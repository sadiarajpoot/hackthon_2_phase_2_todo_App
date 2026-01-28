from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api.auth_router import auth_router
from .api.task_router import task_router
from .database import engine
from .models.user import User
from .models.task import Task
from .utils.logging import get_logger
from sqlmodel import SQLModel
from .config import settings


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up the application...")
    try:
        # Create database tables
        logger.info("Creating database tables...")
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    yield
    # Shutdown
    logger.info("Shutting down the application...")


def create_app():
    app = FastAPI(
        title="Todo Full-Stack Web Application API",
        description="API for the Todo Full-Stack Web Application with JWT authentication and user data isolation",
        version="1.0.0",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(task_router, prefix="/api/tasks", tags=["Tasks"])

    @app.get("/")
    def read_root():
        return {"message": "Todo Full-Stack Web Application API"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "message": "API is running"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.db_echo else False
    )