"""
Vercel serverless function handler for Flask app
"""
import os
import sys

# Add parent directory to path to import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set Vercel environment variable
os.environ['VERCEL'] = '1'

# Initialize error message
error_msg = None

try:
    # Print debug info
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Parent directory: {parent_dir}")
    print(f"Files in parent: {os.listdir(parent_dir) if os.path.exists(parent_dir) else 'NOT FOUND'}")
    
    # Try importing from parent directory
    try:
        from app import app, init_db
        print("Successfully imported app from parent directory")
    except ImportError as e:
        print(f"First import attempt failed: {e}")
        # If that fails, try adding the parent directory explicitly
        parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent not in sys.path:
            sys.path.insert(0, parent)
        try:
            from app import app, init_db
            print("Successfully imported app after adding to path")
        except ImportError as e2:
            print(f"Second import attempt failed: {e2}")
            raise ImportError(f"Failed to import app: {e2}")
    
    # Initialize database on first import (for Vercel)
    try:
        print("Initializing database...")
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization note: {e}")
        import traceback
        traceback.print_exc()
    
    # Vercel's @vercel/python automatically wraps Flask apps
    # Export the app directly - Vercel will handle it
    print("Setting handler to Flask app")
    handler = app
    print("Handler set successfully")
    
except Exception as e:
    import traceback
    error_msg = f"Error loading app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg)
    
    # Create a simple error Flask app that will show the error
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        return f"<h1>Error Loading Application</h1><pre>{error_msg}</pre>", 500
    
    handler = error_app

