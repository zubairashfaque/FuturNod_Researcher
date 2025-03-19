# API caching module
import json
import hashlib
import logging
from typing import Any, Dict, Optional, Callable, Awaitable
from functools import wraps
import redis
from api.config import CACHE_CONFIG

logger = logging.getLogger(__name__)

# Memory cache dictionary
_memory_cache: Dict[str, Dict[str, Any]] = {}


class CacheManager:
    """
    Cache manager for handling different types of caching mechanisms
    """

    @staticmethod
    def _hash_key(key: str) -> str:
        """Generate a hash for the cache key"""
        return hashlib.md5(key.encode()).hexdigest()

    @staticmethod
    def _is_redis_available() -> bool:
        """Check if Redis is available"""
        if CACHE_CONFIG["type"] != "redis":
            return False

        try:
            r = redis.Redis.from_url(CACHE_CONFIG["redis_url"])
            r.ping()
            return True
        except (redis.exceptions.ConnectionError, redis.exceptions.ResponseError):
            logger.warning("Redis connection failed, falling back to memory cache")
            return False

    @staticmethod
    def get_cache(key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not CACHE_CONFIG["enabled"]:
            return None

        hashed_key = CacheManager._hash_key(key)

        if CacheManager._is_redis_available():
            try:
                r = redis.Redis.from_url(CACHE_CONFIG["redis_url"])
                cached_data = r.get(hashed_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.error(f"Redis cache retrieval error: {str(e)}")
                # Fall back to memory cache

        # Use memory cache
        return _memory_cache.get(hashed_key)

    @staticmethod
    def set_cache(key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for default TTL)

        Returns:
            True if successfully cached, False otherwise
        """
        if not CACHE_CONFIG["enabled"]:
            return False

        ttl = ttl or CACHE_CONFIG["ttl"]
        hashed_key = CacheManager._hash_key(key)

        if CacheManager._is_redis_available():
            try:
                r = redis.Redis.from_url(CACHE_CONFIG["redis_url"])
                r.setex(
                    hashed_key,
                    ttl,
                    json.dumps(value)
                )
                return True
            except Exception as e:
                logger.error(f"Redis cache setting error: {str(e)}")
                # Fall back to memory cache

        # Use memory cache
        _memory_cache[hashed_key] = value
        return True

    @staticmethod
    def invalidate_cache(key: str) -> bool:
        """
        Invalidate a cache entry

        Args:
            key: Cache key to invalidate

        Returns:
            True if successfully invalidated, False otherwise
        """
        if not CACHE_CONFIG["enabled"]:
            return False

        hashed_key = CacheManager._hash_key(key)

        if CacheManager._is_redis_available():
            try:
                r = redis.Redis.from_url(CACHE_CONFIG["redis_url"])
                r.delete(hashed_key)
            except Exception as e:
                logger.error(f"Redis cache invalidation error: {str(e)}")

        # Also remove from memory cache
        if hashed_key in _memory_cache:
            del _memory_cache[hashed_key]

        return True


def cached(ttl: Optional[int] = None):
    """
    Decorator for caching function results

    Args:
        ttl: Time to live in seconds (None for default TTL)
    """

    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not CACHE_CONFIG["enabled"]:
                return await func(*args, **kwargs)

            # Generate a cache key from function name and arguments
            key_parts = [func.__name__]
            for arg in args:
                if isinstance(arg, dict):
                    key_parts.append(json.dumps(arg, sort_keys=True))
                else:
                    key_parts.append(str(arg))

            for k, v in sorted(kwargs.items()):
                if isinstance(v, dict):
                    key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
                else:
                    key_parts.append(f"{k}:{v}")

            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_result = CacheManager.get_cache(cache_key)
            if cached_result:
                logger.info(f"Cache hit for '{cache_key}'")
                return cached_result

            # Execute function if not cached
            logger.info(f"Cache miss for '{cache_key}'")
            result = await func(*args, **kwargs)

            # Cache the result
            CacheManager.set_cache(cache_key, result, ttl)

            return result

        return wrapper

    return decorator