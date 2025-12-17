"""
FastAPI Application Entry Point
Main server file that initializes and configures the API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from api.routes import router

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print(f"\n{'='*60}")
    print(f"🚀 {settings.API_TITLE} v{settings.API_VERSION}")
    print(f"{'='*60}")
    print(f"📍 Server running at: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔧 Paper Trading Mode: {settings.PAPER_TRADING}")
    print(f"{'='*60}\n")
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down gracefully...")

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware - Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )

# Run server directly if executed
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )