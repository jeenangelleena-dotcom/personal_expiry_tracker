import os
import sys

# Ensure repository root and backend directory are in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Import Flask WSGI application instance
try:
    from backend.app import app
except ImportError:
    # pyrefly: ignore[missing-import]
    from app import app

# Explicitly expose app and application for Vercel serverless runtime
application = app

__all__ = ["app", "application"]
