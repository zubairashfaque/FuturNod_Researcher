#!/usr/bin/env python
import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger("cache_manager")

class CacheManager:
    """
    Cache manager for optimizing API performance by caching research results.
    """
    
    def __init__(self, cache_dir: str = "cache", ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        
        # Override TTL if specified in environment
        env_ttl = os.getenv("CACHE_TTL")
        if env_ttl:
            try:
                self.ttl = int(env_ttl)
            except ValueError:
                logger.warning(f"Invalid CACHE_TTL value: {env_ttl}, using default: {self.ttl}")
        
        # Create cache directory if it doesn't exist and caching is enabled
        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Cache initialized at {self.cache_dir} with TTL {self.ttl} seconds")
        else:
            logger.info("Caching is disabled")
    
    def _get_cache_key(self, data: Dict[str, Any]) -> str:
        """
        Generate a cache key from the input data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Cache key string
        """
        # Sort keys for consistent hash generation
        serialized = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.md5(serialized).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """
        Get the file path for a cache key.
        
        Args:
            key: Cache key
            
        Returns:
            File path string
        """
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached result for input data if it exists and is not expired.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Cached result dictionary or None if not found or expired
        """
        if not self.enabled:
            return None
        
        key = self._get_cache_key(data)
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            logger.debug(f"Cache miss for {key}")
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check if cache is expired
            timestamp = cached.get("_timestamp", 0)
            current_time = time.time()
            
            if current_time - timestamp > self.ttl:
                logger.debug(f"Cache expired for {key}")
                os.remove(cache_path)
                return None
            
            logger.info(f"Cache hit for {key}")
            return cached.get("data")
            
        except Exception as e:
            logger.error(f"Error reading cache: {str(e)}")
            return None
    
    def set(self, data: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Cache result for input data.
        
        Args:
            data: Input data dictionary
            result: Result dictionary to cache
        """
        if not self.enabled:
            return
        
        key = self._get_cache_key(data)
        cache_path = self._get_cache_path(key)
        
        try:
            cached = {
                "_timestamp": time.time(),
                "_key": key,
                "_input": data,
                "data": result
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cached, f, indent=2)
            
            logger.info(f"Cached result for {key}")
            
        except Exception as e:
            logger.error(f"Error writing cache: {str(e)}")
    
    def invalidate(self, data: Dict[str, Any]) -> bool:
        """
        Invalidate cache for input data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if cache was invalidated, False otherwise
        """
        if not self.enabled:
            return False
        
        key = self._get_cache_key(data)
        cache_path = self._get_cache_path(key)
        
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                logger.info(f"Invalidated cache for {key}")
                return True
            except Exception as e:
                logger.error(f"Error invalidating cache: {str(e)}")
        
        return False
    
    def clear_all(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of cache entries cleared
        """
        if not self.enabled or not os.path.exists(self.cache_dir):
            return 0
        
        count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
                except Exception as e:
                    logger.error(f"Error removing cache file {filename}: {str(e)}")
        
        logger.info(f"Cleared {count} cache entries")
        return count
    
    def clear_expired(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of expired cache entries cleared
        """
        if not self.enabled or not os.path.exists(self.cache_dir):
            return 0
        
        count = 0
        current_time = time.time()
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        cached = json.load(f)
                    
                    timestamp = cached.get("_timestamp", 0)
                    if current_time - timestamp > self.ttl:
                        os.remove(file_path)
                        count += 1
                except Exception as e:
                    logger.error(f"Error checking/removing cache file {filename}: {str(e)}")
        
        logger.info(f"Cleared {count} expired cache entries")
        return count

# Create a singleton instance
cache = CacheManager()
