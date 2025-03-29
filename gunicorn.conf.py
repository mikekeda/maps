"""
Gunicorn config.
"""

bind = "unix:/uwsgi/maps.sock"
workers = 2
timeout = 30
max_requests = 100
daemon = False
umask = "91"
user = "www-data"
loglevel = "info"
