"""
Vercel serverless entry point.
Mounts the FastAPI backend at /api so routes like /health become /api/health.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("PLANS_DIR", "/tmp/plans")

from fastapi import FastAPI

from backend.main import app as backend_app  # noqa: E402

app = FastAPI()
app.mount("/api", backend_app)
