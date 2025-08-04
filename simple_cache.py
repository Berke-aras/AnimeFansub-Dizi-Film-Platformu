"""
Simple caching system for Flask application
This provides basic caching functionality without external dependencies
"""

import time
import hashlib
from functools import wraps
from typing import Any, Dict, Optional

class SimpleCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self, default_timeout: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_timeout = default_timeout
    
    def _make_key(self, key: str) -> str:
        """Create a cache key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._make_key(key)
        if cache_key in self.cache:
            item = self.cache[cache_key]
            if time.time() < item['expires']:
                return item['value']
            else:
                del self.cache[cache_key]
        return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set value in cache"""
        cache_key = self._make_key(key)
        timeout = timeout or self.default_timeout
        self.cache[cache_key] = {
            'value': value,
            'expires': time.time() + timeout
        }
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        cache_key = self._make_key(key)
        if cache_key in self.cache:
            del self.cache[cache_key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def cached(self, timeout: Optional[int] = None, key_prefix: str = ''):
        """Decorator for caching function results"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Create cache key from function name, args, and kwargs
                cache_key = f"{key_prefix}{f.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                
                # Try to get from cache
                result = self.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = f(*args, **kwargs)
                self.set(cache_key, result, timeout)
                return result
            return wrapper
        return decorator

# Create global cache instance
simple_cache = SimpleCache()
