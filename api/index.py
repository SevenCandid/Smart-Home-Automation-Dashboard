"""
Vercel serverless function handler for Flask app
Minimal version with maximum error visibility
"""
import os
import sys
import io
import traceback

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

os.environ['VERCEL'] = '1'

# Global error tracking
LOAD_ERROR = None
FLASK_APP = None

# Try to load Flask app
try:
    print("=" * 50)
    print("ATTEMPTING TO LOAD FLASK APP")
    print("=" * 50)
    
    from app import app
    FLASK_APP = app
    print("✓ Flask app imported successfully")
    
    # Try to initialize database
    try:
        from app import init_db, init_scenes_table, init_schedules_table, init_energy_table
        init_db()
        init_scenes_table()
        init_schedules_table()
        init_energy_table()
        print("✓ Database initialized")
    except Exception as db_err:
        print(f"⚠ Database init warning: {db_err}")
    
    print("✓ Flask app ready")
    print("=" * 50)
    
except Exception as e:
    LOAD_ERROR = traceback.format_exc()
    print("=" * 50)
    print("FAILED TO LOAD FLASK APP")
    print("=" * 50)
    print(LOAD_ERROR)
    print("=" * 50)
    
    # Create minimal error app
    try:
        from flask import Flask
        error_app = Flask(__name__)
        @error_app.route('/<path:path>')
        @error_app.route('/')
        def error(path=''):
            return f"<h1>App Load Error</h1><pre>{LOAD_ERROR}</pre>", 500
        FLASK_APP = error_app
        print("✓ Error Flask app created")
    except Exception as flask_err:
        print(f"✗ Could not create error app: {flask_err}")

def handler(req, res):
    """Vercel handler"""
    try:
        print("=" * 50)
        print("HANDLER CALLED")
        print(f"Request type: {type(req)}")
        print(f"Response type: {type(res)}")
        print("=" * 50)
        
        if FLASK_APP is None:
            error_msg = "Flask app is None"
            if LOAD_ERROR:
                error_msg += f"\n\nLoad error:\n{LOAD_ERROR}"
            res.status(500)
            res.headers['Content-Type'] = 'text/html'
            res.send(f"<h1>Error</h1><pre>{error_msg}</pre>")
            return
        
        # Extract request info
        method = getattr(req, 'method', 'GET') or 'GET'
        path = getattr(req, 'path', None) or getattr(req, 'url', '/') or '/'
        if isinstance(path, str) and '?' in path:
            path = path.split('?')[0]
        if not path.startswith('/'):
            path = '/' + path
        
        headers = {}
        if hasattr(req, 'headers'):
            try:
                headers = dict(req.headers) if req.headers else {}
            except:
                pass
        
        body = b''
        if hasattr(req, 'body') and req.body:
            try:
                if isinstance(req.body, str):
                    body = req.body.encode('utf-8')
                else:
                    body = bytes(req.body) if not isinstance(req.body, bytes) else req.body
            except:
                pass
        
        query = {}
        if hasattr(req, 'query') and req.query:
            try:
                query = dict(req.query) if isinstance(req.query, dict) else {}
            except:
                pass
        
        query_string = '&'.join([f"{k}={v}" for k, v in query.items()]) if query else ''
        
        print(f"Path: {path}, Method: {method}")
        
        # Create WSGI environ
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
        
        # Add headers
        for key, value in headers.items():
            try:
                key_upper = str(key).upper().replace('-', '_')
                if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                    environ[f'HTTP_{key_upper}'] = str(value)
            except:
                pass
        
        # Response storage
        status = [None]
        headers_list = [None]
        body_chunks = []
        
        def start_response(s, h):
            status[0] = s
            headers_list[0] = dict(h)
        
        # Call Flask
        print("Calling Flask app...")
        try:
            result = FLASK_APP(environ, start_response)
            print("Flask app called successfully")
            
            for chunk in result:
                if chunk:
                    body_chunks.append(chunk)
            
            if hasattr(result, 'close'):
                try:
                    result.close()
                except:
                    pass
        except Exception as flask_err:
            print(f"Flask execution error: {flask_err}")
            raise
        
        # Send response
        status_code = 200
        if status[0]:
            try:
                status_code = int(str(status[0]).split()[0])
            except:
                pass
        
        res.status(status_code)
        
        if headers_list[0]:
            for k, v in headers_list[0].items():
                try:
                    res.headers[str(k)] = str(v)
                except:
                    pass
        
        body_bytes = b''.join(body_chunks)
        try:
            res.send(body_bytes.decode('utf-8'))
        except:
            res.send(body_bytes)
        
        print("Response sent successfully")
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print("=" * 50)
        print("HANDLER ERROR")
        print("=" * 50)
        print(error_trace)
        print("=" * 50)
        
        try:
            res.status(500)
            res.headers['Content-Type'] = 'text/html'
            res.send(f"<h1>Handler Error</h1><pre>{error_trace}</pre>")
        except:
            print("Could not send error response")
