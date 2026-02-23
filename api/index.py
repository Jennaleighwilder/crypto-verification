"""
Vercel Flask entry point — single serverless function for all routes
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from backend.app import app
