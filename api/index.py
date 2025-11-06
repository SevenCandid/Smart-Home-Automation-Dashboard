"""
Vercel serverless function handler for Flask app
"""
import os
import sys

# Add parent directory to path to import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Set Vercel environment variable
os.environ['VERCEL'] = '1'

try:
    from app import app, init_db
    
    # Initialize database on first import (for Vercel)
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization note: {e}")
    
    # Export the Flask app for Vercel
    handler = app
except Exception as e:
    # If import fails, create a simple error handler
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/')
    def error():
        return f"Error loading app: {str(e)}", 500
    
    handler = error_app

