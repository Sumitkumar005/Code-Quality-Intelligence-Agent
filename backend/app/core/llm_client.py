"""
LLM client for health checks
"""
import requests
import structlog

logger = structlog.get_logger(__name__)

async def check_ollama_health():
    """Check if Ollama is available"""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            logger.info("Ollama health check passed")
            return True
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")
        return False