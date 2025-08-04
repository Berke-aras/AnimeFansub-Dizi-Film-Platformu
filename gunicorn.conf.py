# Gunicorn configuration file for production deployment
# Save this as gunicorn.conf.py

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "anime_fansub"

# Daemon mode (set to True for production)
daemon = False

# User and group to run as (uncomment and set for production)
# user = "www-data"
# group = "www-data"

# Directory to store temporary files
tmp_upload_dir = "/tmp"

# Preload application code before forking worker processes
preload_app = True

# Enable stdio inheritance
enable_stdio_inheritance = True
