"""
Vercel serverless function handler for Flask app
Simplified version for better compatibility
"""
import os
import sys

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
    # Import Flask app
    from app import app, init_db
    flask_app = app
    
    # Initialize database on first import (for Vercel)
    try:
        init_db()
        # Also initialize additional tables
        from app import init_scenes_table, init_schedules_table, init_energy_table
        init_scenes_table()
        init_schedules_table()
        init_energy_table()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization note: {e}")
    
    print("Flask app loaded successfully")
    
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

# Use Werkzeug's WSGI adapter for Vercel
try:
    from werkzeug.serving import WSGIRequestHandler
    from werkzeug.wrappers import Request, Response
except ImportError:
    # Fallback if werkzeug not available
    WSGIRequestHandler = None

def handler(req, res):
    """Vercel serverless function handler"""
    try:
        if flask_app is None:
            res.status(500)
            res.send("<h1>Error: Flask app not initialized</h1>")
            return
        
        # Get request details - Vercel's format
        method = getattr(req, 'method', 'GET') or 'GET'
        
        # Get path from request
        path = '/'
        if hasattr(req, 'path'):
            path = req.path or '/'
        elif hasattr(req, 'url'):
            url = req.url or '/'
            path = url.split('?')[0] if '?' in url else url
        
        if not path.startswith('/'):
            path = '/' + path
        
        # Get headers
        headers = {}
        if hasattr(req, 'headers') and req.headers:
            headers = dict(req.headers)
        
        # Get body
        body = b''
        if hasattr(req, 'body'):
            body_data = req.body
            if isinstance(body_data, str):
                body = body_data.encode('utf-8')
            elif body_data:
                body = bytes(body_data) if not isinstance(body_data, bytes) else body_data
        
        # Get query string
        query_string = ''
        if hasattr(req, 'query') and req.query:
            query_string = '&'.join([f"{k}={v}" for k, v in req.query.items()])
        
        # Create WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'SCRIPT_NAME': '',
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', '') or headers.get('Content-Type', ''),
            'CONTENT_LENGTH': str(len(body)),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': None,  # Will be set below
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add HTTP headers
        for key, value in headers.items():
            key_upper = key.upper().replace('-', '_')
            if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key_upper}'] = str(value)
        
        # Create input stream
        import io
        environ['wsgi.input'] = io.BytesIO(body)
        
        # Response storage
        response_status = [None]
        response_headers = [None]
        response_body = []
        
        def start_response(status, headers_list):
            response_status[0] = status
            response_headers[0] = dict(headers_list)
        
        # Call Flask app
        result = flask_app(environ, start_response)
        
        # Collect response
        for chunk in result:
            if chunk:
                response_body.append(chunk)
        
        # Close result if it has close method
        if hasattr(result, 'close'):
            result.close()
        
        # Set response status
        status_code = 200
        if response_status[0]:
            try:
                status_code = int(str(response_status[0]).split()[0])
            except:
                pass
        
        res.status(status_code)
        
        # Set headers
        if response_headers[0]:
            for key, value in response_headers[0].items():
                try:
                    res.headers[str(key)] = str(value)
                except:
                    pass
        
        # Send body
        body_bytes = b''.join(response_body)
        try:
            body_str = body_bytes.decode('utf-8')
            res.send(body_str)
        except:
            # If decode fails, try to send as is
            res.send(body_bytes)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = f"Handler error: {str(e)}\n{error_trace}"
        print(error_msg)
        
        try:
            res.status(500)
            res.headers['Content-Type'] = 'text/html; charset=utf-8'
            res.send(f"<h1>Internal Server Error</h1><pre>{error_msg}</pre>")
        except:
            print("CRITICAL: Could not send error response")
