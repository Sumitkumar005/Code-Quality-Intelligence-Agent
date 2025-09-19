"""
CQIA-Tool: Code Quality Intelligence Agent
FastAPI main application entry point
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog
import uvicorn
from contextlib import asynccontextmanager

from app.api.v1 import analyze, report, qa, pr
from app.core.config import get_settings
from app.utils.logger import setup_logging
from app.db.sqlite_session import init_db

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting CQIA-Tool backend...")
    
    # Initialize database
    await init_db()
    
    # Check Ollama availability
    try:
        from app.core.llm_client import check_ollama_health
        await check_ollama_health()
        logger.info("Ollama connection verified")
    except Exception as e:
        logger.warning(f"Ollama not available: {e}")
    
    yield
    
    logger.info("Shutting down CQIA-Tool backend...")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="CQIA-Tool API",
        description="Code Quality Intelligence Agent - Analyze, Report, and Improve Code Quality",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )
    
    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # API Routes
    app.include_router(analyze.router, prefix="/api/v1", tags=["analysis"])
    app.include_router(report.router, prefix="/api/v1", tags=["reports"])
    app.include_router(qa.router, prefix="/api/v1", tags=["qa"])
    app.include_router(pr.router, prefix="/api/v1", tags=["pr-review"])
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "version": "1.0.0"}
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception: {exc}", exc_info=True)
        return HTTPException(status_code=500, detail="Internal server error")
    
    return app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None  # Use structlog instead
    )
