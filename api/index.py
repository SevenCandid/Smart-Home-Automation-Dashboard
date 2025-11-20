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
    except ImportError as import_err:
        # If that fails, try adding the parent directory explicitly
        parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent not in sys.path:
            sys.path.insert(0, parent)
        try:
            from app import app, init_db
            flask_app = app
        except ImportError:
            raise import_err
    
    # Initialize database on first import (for Vercel)
    try:
        init_db()
        # Also initialize additional tables
        from app import init_scenes_table, init_schedules_table, init_energy_table
        init_scenes_table()
        init_schedules_table()
        init_energy_table()
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
# Vercel's @vercel/python expects a handler function
def handler(req, res):
    """Vercel serverless function handler"""
    try:
        if flask_app is None:
            res.status(500)
            res.send("<h1>Error: Flask app not initialized</h1>")
            return
        
        # Debug: Print request object structure
        print(f"Request type: {type(req)}")
        print(f"Request attributes: {dir(req)}")
        
        # Try to get path from request - Vercel's format
        path = '/'
        try:
            # Try different ways Vercel might pass the path
            if hasattr(req, 'path'):
                path = str(req.path) if req.path else '/'
            elif hasattr(req, 'url'):
                url = str(req.url) if req.url else '/'
                path = url.split('?')[0] if '?' in url else url
            elif hasattr(req, 'pathname'):
                path = str(req.pathname) if req.pathname else '/'
            else:
                # Try accessing as dict-like
                try:
                    path = req.get('path', '/') if hasattr(req, 'get') else '/'
                except:
                    pass
        except Exception as path_err:
            print(f"Error getting path: {path_err}")
            path = '/'
        
        # Ensure path starts with /
        if not path or not path.startswith('/'):
            path = '/' + path
        
        # Get method
        method = 'GET'
        try:
            if hasattr(req, 'method'):
                method = str(req.method) if req.method else 'GET'
            elif hasattr(req, 'get'):
                method = req.get('method', 'GET')
        except:
            pass
        
        # Get headers
        headers = {}
        try:
            if hasattr(req, 'headers'):
                headers = dict(req.headers) if req.headers else {}
            elif hasattr(req, 'get'):
                headers = req.get('headers', {})
        except:
            pass
        
        # Get body
        body = b''
        try:
            if hasattr(req, 'body'):
                body_data = req.body
                if isinstance(body_data, str):
                    body = body_data.encode('utf-8')
                elif body_data:
                    body = bytes(body_data)
        except:
            pass
        
        # Get query
        query = {}
        try:
            if hasattr(req, 'query'):
                query = dict(req.query) if req.query else {}
            elif hasattr(req, 'get'):
                query = req.get('query', {})
        except:
            pass
        
        print(f"Vercel Handler - Path: {path}, Method: {method}")
        
        # Handle string body
        if isinstance(body, str):
            body = body.encode('utf-8')
        
        # Create WSGI environment
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'SCRIPT_NAME': '',
            'QUERY_STRING': '&'.join([f"{k}={v}" for k, v in query.items()]) if query else '',
            'CONTENT_TYPE': headers.get('content-type', '') or headers.get('Content-Type', '') or '',
            'CONTENT_LENGTH': str(len(body)) if body else '0',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': io.BytesIO(body),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add headers to environ
        if headers:
            for key, value in headers.items():
                try:
                    key_upper = str(key).upper().replace('-', '_')
                    if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                        environ[f'HTTP_{key_upper}'] = str(value)
                except:
                    pass
        
        # Response storage
        response_status = [None]
        response_headers = [None]
        response_body = []
        
        def start_response(status, headers):
            response_status[0] = status
            response_headers[0] = dict(headers)
        
        # Call Flask app
        result = flask_app(environ, start_response)
        
        # Collect response body
        for chunk in result:
            if chunk:
                response_body.append(chunk)
        
        # Set response
        status_code = 200
        try:
            if response_status[0]:
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
        
        # Set body
        try:
            body_str = b''.join(response_body).decode('utf-8') if response_body else ''
            res.send(body_str)
        except Exception as send_err:
            print(f"Error sending response: {send_err}")
            res.send("")
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = f"Error in handler: {str(e)}\n{error_trace}"
        print(error_msg)
        try:
            res.status(500)
            res.headers['Content-Type'] = 'text/html'
            res.send(f"<h1>Internal Server Error</h1><pre>{str(e)}\n{error_trace}</pre>")
        except:
            # If we can't even send error response, at least log it
            print("CRITICAL: Could not send error response")

