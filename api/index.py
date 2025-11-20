"""
Vercel serverless function handler for Flask app
Proper handler function for @vercel/python runtime
"""
import os
import sys
import io

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

os.environ['VERCEL'] = '1'

# Load Flask app
flask_app = None
try:
    from app import app
    flask_app = app
    
    # Initialize database
    try:
        from app import init_db, init_scenes_table, init_schedules_table, init_energy_table
        init_db()
        init_scenes_table()
        init_schedules_table()
        init_energy_table()
    except Exception as e:
        print(f"DB init: {e}")
except Exception as e:
    import traceback
    print(f"Import error: {traceback.format_exc()}")
    from flask import Flask
    flask_app = Flask(__name__)
    @flask_app.route('/<path:path>')
    @flask_app.route('/')
    def error(path=''):
        return f"<h1>Error</h1><pre>{str(e)}</pre>", 500

def handler(req, res):
    """Vercel handler function"""
    if flask_app is None:
        res.status(500)
        res.send("Flask app not loaded")
        return
    
    try:
        # Extract request info
        method = getattr(req, 'method', 'GET') or 'GET'
        path = getattr(req, 'path', None) or getattr(req, 'url', '/') or '/'
        if '?' in str(path):
            path = str(path).split('?')[0]
        if not str(path).startswith('/'):
            path = '/' + str(path)
        
        # Get headers
        headers = {}
        try:
            if hasattr(req, 'headers'):
                h = req.headers
                headers = dict(h) if h else {}
        except:
            pass
        
        # Get body
        body = b''
        try:
            if hasattr(req, 'body') and req.body:
                b = req.body
                if isinstance(b, str):
                    body = b.encode('utf-8')
                else:
                    body = bytes(b) if not isinstance(b, bytes) else b
        except:
            pass
        
        # Get query
        query_str = ''
        try:
            if hasattr(req, 'query') and req.query:
                q = req.query
                if isinstance(q, dict):
                    query_str = '&'.join([f"{k}={v}" for k, v in q.items()])
        except:
            pass
        
        # Create WSGI environ
        environ = {
            'REQUEST_METHOD': str(method),
            'PATH_INFO': str(path),
            'SCRIPT_NAME': '',
            'QUERY_STRING': query_str,
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
        for k, v in headers.items():
            try:
                k_upper = str(k).upper().replace('-', '_')
                if k_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                    environ[f'HTTP_{k_upper}'] = str(v)
            except:
                pass
        
        # Response storage
        status_code = [200]
        response_headers = [{}]
        response_body = []
        
        def start_response(status, headers_list):
            status_code[0] = int(status.split()[0])
            response_headers[0] = dict(headers_list)
        
        # Call Flask
        result = flask_app(environ, start_response)
        
        # Collect response
        for chunk in result:
            if chunk:
                response_body.append(chunk)
        
        if hasattr(result, 'close'):
            try:
                result.close()
            except:
                pass
        
        # Send response
        res.status(status_code[0])
        for k, v in response_headers[0].items():
            try:
                res.headers[str(k)] = str(v)
            except:
                pass
        
        body_bytes = b''.join(response_body)
        try:
            res.send(body_bytes.decode('utf-8'))
        except:
            res.send(body_bytes)
            
    except Exception as e:
        import traceback
        error = traceback.format_exc()
        print(f"Handler error: {error}")
        try:
            res.status(500)
            res.headers['Content-Type'] = 'text/html'
            res.send(f"<h1>Error</h1><pre>{error}</pre>")
        except:
            pass
