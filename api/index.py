"""
Vercel serverless function handler for Flask app
"""
import os
import sys
import io

# Add parent directory to path to import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set Vercel environment variable
os.environ['VERCEL'] = '1'

# Initialize Flask app
flask_app = None
error_msg = None

try:
    # Try importing from parent directory
    try:
        from app import app, init_db
        flask_app = app
    except ImportError:
        # If that fails, try adding the parent directory explicitly
        parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent not in sys.path:
            sys.path.insert(0, parent)
        from app import app, init_db
        flask_app = app
    
    # Initialize database on first import (for Vercel)
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization note: {e}")
    
except Exception as e:
    import traceback
    error_msg = f"Error loading app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg)
    
    # Create a simple error Flask app
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        return f"<h1>Error Loading Application</h1><pre>{error_msg}</pre>", 500
    
    flask_app = error_app

# Vercel Python handler function
# Vercel's @vercel/python automatically wraps Flask apps
# Just export the Flask app directly
handler = flask_app

