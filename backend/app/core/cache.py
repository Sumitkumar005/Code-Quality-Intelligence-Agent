"""
Redis cache configuration and utilities for CQIA.
Provides caching layer for frequently accessed data and session management.
"""

import json
import pickle
from typing import Any, Optional, Union
from redis import Redis
from redis.connection import ConnectionPool
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Redis connection pool
pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
redis_client = Redis(connection_pool=pool)


class Cache:
    """Redis cache wrapper with JSON serialization."""

    def __init__(self, redis_client: Redis, default_ttl: int = None):
        self.redis = redis_client
        self.default_ttl = default_ttl or settings.CACHE_TTL

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL."""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            return self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key."""
        try:
            return bool(self.redis.expire(key, ttl))
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False

    def incr(self, key: str) -> Optional[int]:
        """Increment integer value."""
        try:
            return self.redis.incr(key)
        except Exception as e:
            logger.error(f"Cache incr error for key {key}: {e}")
            return None

    def get_ttl(self, key: str) -> int:
        """Get TTL for key."""
        try:
            return self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1


# Global cache instance
cache = Cache(redis_client)


# Session management
class SessionManager:
    """Redis-based session management."""

    def __init__(self, cache: Cache, session_prefix: str = "session:"):
        self.cache = cache
        self.prefix = session_prefix
        self.session_ttl = 24 * 60 * 60  # 24 hours

    def create_session(self, user_id: str, data: dict = None) -> str:
        """Create a new session for user."""
        session_id = f"{self.prefix}{user_id}:{cache.redis.incr('session_counter')}"
        session_data = {
            "user_id": user_id,
            "created_at": json.dumps({"$date": str(datetime.utcnow())}),
            "data": data or {}
        }
        self.cache.set(session_id, session_data, self.session_ttl)
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        return self.cache.get(session_id)

    def update_session(self, session_id: str, data: dict) -> bool:
        """Update session data."""
        session_data = self.get_session(session_id)
        if not session_data:
            return False

        session_data["data"].update(data)
        return self.cache.set(session_id, session_data, self.session_ttl)

    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        return self.cache.delete(session_id)

    def extend_session(self, session_id: str) -> bool:
        """Extend session TTL."""
        return self.cache.expire(session_id, self.session_ttl)


# Rate limiting
class RateLimiter:
    """Redis-based rate limiting."""

    def __init__(self, cache: Cache, prefix: str = "ratelimit:"):
        self.cache = cache
        self.prefix = prefix

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed under rate limit."""
        cache_key = f"{self.prefix}{key}"
        current = self.cache.get(cache_key) or 0

        if current >= limit:
            return False

        # Increment counter
        new_count = self.cache.incr(cache_key) or 1

        # Set expiry if this is the first request in window
        if new_count == 1:
            self.cache.expire(cache_key, window)

        return new_count <= limit

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for key."""
        cache_key = f"{self.prefix}{key}"
        current = self.cache.get(cache_key) or 0
        return max(0, settings.RATE_LIMIT_PER_MINUTE - current)

    def reset(self, key: str) -> bool:
        """Reset rate limit for key."""
        cache_key = f"{self.prefix}{key}"
        return self.cache.delete(cache_key)


# Global instances
session_manager = SessionManager(cache)
rate_limiter = RateLimiter(cache)


# Cache key generators
def make_cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)


# Cache decorators
def cached(ttl: int = None, key_prefix: str = ""):
    """Cache decorator for functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{make_cache_key(*args, **kwargs)}"
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


def invalidate_cache(key_pattern: str):
    """Invalidate cache keys matching pattern."""
    try:
        # Note: This is a simple implementation
        # In production, you might want to use Redis SCAN
        keys = redis_client.keys(key_pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        logger.error(f"Cache invalidation error for pattern {key_pattern}: {e}")


# Health check
def check_cache_health() -> bool:
    """Check if Redis cache is accessible and healthy."""
    try:
        return redis_client.ping()
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return False


# Convenience functions for backward compatibility
def get_cache(key):
    return cache.get(key)

def set_cache(key, value, ttl=None):
    return cache.set(key, value, ttl)

def delete_cache(key):
    return cache.delete(key)
