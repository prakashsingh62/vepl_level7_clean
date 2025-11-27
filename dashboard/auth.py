# dashboard/auth.py
from functools import wraps
from flask import session, redirect, current_app

_CONFIG = None

def init_auth(config: dict):
    """Initialize auth module with config (call from main)."""
    global _CONFIG
    _CONFIG = config

def get_config():
    return _CONFIG

def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper
