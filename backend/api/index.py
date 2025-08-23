"""
Vercel-compatible entry point for CuraGenie Backend
"""
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app

# For Vercel
handler = app
