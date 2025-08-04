"""
Simple performance monitoring middleware for Flask
"""

import time
import logging
from functools import wraps
from flask import request, g

# Setup performance logging
perf_logger = logging.getLogger('performance')
perf_logger.setLevel(logging.INFO)
handler = logging.FileHandler('performance.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
perf_logger.addHandler(handler)

def monitor_performance(app):
    """Add performance monitoring to Flask app"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Log slow requests (over 1 second)
            if duration > 1.0:
                perf_logger.warning(
                    f"SLOW REQUEST: {request.method} {request.path} - "
                    f"{duration:.3f}s - {response.status_code}"
                )
            
            # Log all requests in debug mode
            if app.debug:
                perf_logger.info(
                    f"{request.method} {request.path} - "
                    f"{duration:.3f}s - {response.status_code}"
                )
            
            # Add response header for debugging
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response

def time_function(func):
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        if duration > 0.5:  # Log functions taking over 500ms
            perf_logger.warning(
                f"SLOW FUNCTION: {func.__name__} took {duration:.3f}s"
            )
        
        return result
    return wrapper
