"""
Caching utility for the Travel AI system.
"""
import json
import pickle
from pathlib import Path
import time
from typing import Any, Optional, Callable, TypeVar, cast
from functools import wraps
import hashlib
import logging
from datetime import datetime, timedelta

from config import CACHE_CONFIG, CACHE_DIR
from utils.logger import get_logger, performance_logger

logger = get_logger(__name__)

T = TypeVar('T')

class Cache:
    """Cache manager for the application."""
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = CACHE_CONFIG["ttl"]
        self.max_size = CACHE_CONFIG["max_size"]
        self._cleanup_old_cache()

    def _get_cache_path(self, key: str) -> Path:
        """Get the cache file path for a given key."""
        # Create a hash of the key to use as filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def _cleanup_old_cache(self):
        """Remove expired cache files."""
        try:
            current_time = time.time()
            for cache_file in self.cache_dir.glob("*.cache"):
                if cache_file.stat().st_mtime < current_time - self.ttl:
                    cache_file.unlink()
                    logger.debug(f"Removed expired cache file: {cache_file}")
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")

    def _enforce_cache_size(self):
        """Ensure cache directory doesn't exceed max_size."""
        try:
            cache_files = list(self.cache_dir.glob("*.cache"))
            if len(cache_files) > self.max_size:
                # Sort by modification time (oldest first)
                cache_files.sort(key=lambda x: x.stat().st_mtime)
                # Remove oldest files
                for cache_file in cache_files[:len(cache_files) - self.max_size]:
                    cache_file.unlink()
                    logger.debug(f"Removed cache file to maintain size limit: {cache_file}")
        except Exception as e:
            logger.error(f"Error enforcing cache size: {e}")

    @performance_logger()
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not CACHE_CONFIG["enabled"]:
            return None

        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None

        try:
            # Check if cache is expired
            if time.time() - cache_path.stat().st_mtime > self.ttl:
                cache_path.unlink()
                return None

            with cache_path.open('rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
            return None

    @performance_logger()
    def set(self, key: str, value: Any):
        """Set a value in cache."""
        if not CACHE_CONFIG["enabled"]:
            return

        try:
            cache_path = self._get_cache_path(key)
            with cache_path.open('wb') as f:
                pickle.dump(value, f)
            self._enforce_cache_size()
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")

    def delete(self, key: str):
        """Delete a value from cache."""
        try:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")

    def clear(self):
        """Clear all cache."""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

# Global cache instance
cache = Cache()

def cached(ttl: Optional[int] = None):
    """Decorator for caching function results."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not CACHE_CONFIG["enabled"]:
                return func(*args, **kwargs)

            # Create cache key from function name and arguments
            key_parts = [func.__module__, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = "|".join(key_parts)

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cast(T, cached_result)

            # If not in cache, call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            logger.debug(f"Cache miss for {func.__name__}, stored result")
            return result

        return wrapper
    return decorator

class CacheContext:
    """Context manager for caching operations."""
    def __init__(self, key: str, ttl: Optional[int] = None):
        self.key = key
        self.ttl = ttl or CACHE_CONFIG["ttl"]
        self.cache = cache

    def __enter__(self):
        return self.cache.get(self.key)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.cache.set(self.key, exc_val)
        return False 