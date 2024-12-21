from functools import wraps
from datetime import datetime, timedelta
import hashlib
import json
from typing import Any, Dict, Optional
import logging

class Cache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set a cache value with TTL"""
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
        
    def get(self, key: str) -> Optional[Any]:
        """Get a cache value if not expired"""
        if key not in self._cache:
            return None
            
        cache_data = self._cache[key]
        if datetime.now() > cache_data['expires_at']:
            del self._cache[key]
            return None
            
        return cache_data['value']
        
    def delete(self, key: str):
        """Delete a cache entry"""
        if key in self._cache:
            del self._cache[key]
            
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()

# Initialize global cache
cache = Cache()

def cached(ttl_seconds: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            
            cache_key = hashlib.md5(
                json.dumps(key_parts).encode()
            ).hexdigest()
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logging.debug(f"Cache hit for {func.__name__}")
                return cached_value
                
            # Get fresh value
            value = func(*args, **kwargs)
            cache.set(cache_key, value, ttl_seconds)
            logging.debug(f"Cache miss for {func.__name__}")
            
            return value
        return wrapper
    return decorator