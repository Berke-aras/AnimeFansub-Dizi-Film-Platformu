#!/usr/bin/env python3
"""
Production WSGI entry point for the Anime Fansub Platform
Use this with Gunicorn or uWSGI for production deployment
"""

import os
import sys
from app import app as application

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

if __name__ == "__main__":
    # This won't be called when using WSGI servers
    # But useful for direct execution
    application.run(host='0.0.0.0', port=5000, debug=False)
