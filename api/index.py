"""
Vercel serverless function handler for Flask app
Using direct Flask WSGI application
"""
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

os.environ['VERCEL'] = '1'

# Import Flask app directly
try:
    from app import app
    # Initialize database
    try:
        from app import init_db, init_scenes_table, init_schedules_table, init_energy_table
        init_db()
        init_scenes_table()
        init_schedules_table()
        init_energy_table()
    except Exception as e:
        print(f"Database init warning: {e}")
    
    # Export app as handler - Vercel can use Flask app directly
    handler = app
    
except Exception as e:
    import traceback
    error = traceback.format_exc()
    print(f"Failed to load app: {error}")
    
    # Create minimal error handler
    from flask import Flask, jsonify
    error_app = Flask(__name__)
    
    @error_app.route('/<path:path>')
    @error_app.route('/')
    def error_handler(path=''):
        return f"<h1>App Load Error</h1><pre>{error}</pre>", 500
    
    handler = error_app
