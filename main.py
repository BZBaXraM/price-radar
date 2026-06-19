"""Convenience entry point.

The real application lives in ``app/main.py``. This re-export lets you run either
``uvicorn app.main:app`` or ``uvicorn main:app`` and get the full API.
"""
from app.main import app

__all__ = ["app"]
