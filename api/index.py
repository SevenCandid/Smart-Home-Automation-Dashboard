"""
Vercel serverless function handler for Flask app
Simplified version for better compatibility
"""
import os
import sys
import io
import traceback

# Add parent directory to path to import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set Vercel environment variable
os.environ['VERCEL'] = '1'

# Initialize Flask app
flask_app = None
init_error = None

# Try to import and initialize Flask app
try:
    print("Starting Flask app import...")
    from app import app, init_db
    flask_app = app
    print("Flask app imported successfully")
    
    # Initialize database
    try:
        print("Initializing database...")
        init_db()
        from app import init_scenes_table, init_schedules_table, init_energy_table
        init_scenes_table()
        init_schedules_table()
        init_energy_table()
        print("Database initialized successfully")
    except Exception as db_err:
        print(f"Database initialization warning: {db_err}")
        # Don't fail on DB init errors, app might still work
    
    print("Flask app ready")
    
except Exception as e:
    init_error = f"Error loading app: {str(e)}\n{traceback.format_exc()}"
    print(init_error)
    
    # Create minimal error Flask app
    try:
        from flask import Flask
        error_app = Flask(__name__)
        
        @error_app.route('/', defaults={'path': ''})
        @error_app.route('/<path:path>')
        def error_handler(path):
            return f"<h1>Error Loading Application</h1><pre>{init_error}</pre>", 500
        
        flask_app = error_app
        print("Error Flask app created")
    except Exception as flask_err:
        print(f"Could not create error Flask app: {flask_err}")
        flask_app = None

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
        # Check if Flask app is available
        if flask_app is None:
            error_msg = "Flask app not initialized"
            if init_error:
                error_msg += f"\n\nInitialization error:\n{init_error}"
            res.status(500)
            res.headers['Content-Type'] = 'text/html; charset=utf-8'
            res.send(f"<h1>Error: Flask app not initialized</h1><pre>{error_msg}</pre>")
            return
        
        # Extract request information safely
        method = 'GET'
        path = '/'
        headers = {}
        body = b''
        query_string = ''
        
        try:
            method = getattr(req, 'method', 'GET') or 'GET'
        except:
            pass
        
        try:
            if hasattr(req, 'path') and req.path:
                path = str(req.path)
            elif hasattr(req, 'url') and req.url:
                url = str(req.url)
                path = url.split('?')[0] if '?' in url else url
        except:
            pass
        
        if not path.startswith('/'):
            path = '/' + path
        
        try:
            if hasattr(req, 'headers') and req.headers:
                headers = dict(req.headers) if isinstance(req.headers, dict) else {}
        except:
            pass
        
        try:
            if hasattr(req, 'body') and req.body:
                body_data = req.body
                if isinstance(body_data, str):
                    body = body_data.encode('utf-8')
                elif body_data:
                    body = bytes(body_data) if not isinstance(body_data, bytes) else body_data
        except:
            pass
        
        try:
            if hasattr(req, 'query') and req.query:
                if isinstance(req.query, dict):
                    query_string = '&'.join([f"{k}={v}" for k, v in req.query.items()])
        except:
            pass
        
        # Create WSGI environment
        environ = {
            'REQUEST_METHOD': str(method),
            'PATH_INFO': str(path),
            'SCRIPT_NAME': '',
            'QUERY_STRING': str(query_string),
            'CONTENT_TYPE': str(headers.get('content-type', '') or headers.get('Content-Type', '')),
            'CONTENT_LENGTH': str(len(body)),
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
        
        # Add HTTP headers
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
        
        def start_response(status, headers_list):
            response_status[0] = status
            response_headers[0] = dict(headers_list)
        
        # Call Flask app
        try:
            result = flask_app(environ, start_response)
            
            # Collect response
            for chunk in result:
                if chunk:
                    response_body.append(chunk)
            
            # Close result if it has close method
            if hasattr(result, 'close'):
                try:
                    result.close()
                except:
                    pass
        except Exception as flask_err:
            raise Exception(f"Flask app execution error: {flask_err}")
        
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
        except UnicodeDecodeError:
            # If decode fails, try to send as is (might be binary)
            res.send(body_bytes)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        error_msg = f"Handler error: {str(e)}\n\n{error_trace}"
        print(error_msg)
        
        try:
            res.status(500)
            res.headers['Content-Type'] = 'text/html; charset=utf-8'
            res.send(f"<h1>Internal Server Error</h1><pre>{error_msg}</pre>")
        except Exception as send_err:
            print(f"CRITICAL: Could not send error response: {send_err}")
