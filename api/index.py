"""
Vercel serverless function handler for Flask app
With comprehensive error handling for import-time errors
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

# Global variables
flask_app = None
import_error = None

# Try to import Flask app with comprehensive error handling
print("=" * 60)
print("STARTING FLASK APP IMPORT")
print("=" * 60)

try:
    print("Step 1: Importing app module...")
    from app import app
    flask_app = app
    print("✓ App imported successfully")
    
    print("Step 2: Initializing database...")
    try:
        from app import init_db, init_scenes_table, init_schedules_table, init_energy_table
        init_db()
        print("✓ init_db() completed")
        init_scenes_table()
        print("✓ init_scenes_table() completed")
        init_schedules_table()
        print("✓ init_schedules_table() completed")
        init_energy_table()
        print("✓ init_energy_table() completed")
        print("✓ Database initialization complete")
    except Exception as db_err:
        print(f"⚠ Database initialization error: {db_err}")
        print(traceback.format_exc())
        # Continue even if DB init fails
    
    print("=" * 60)
    print("FLASK APP READY")
    print("=" * 60)
    
except ImportError as import_err:
    import_error = f"Import Error: {str(import_err)}\n{traceback.format_exc()}"
    print("=" * 60)
    print("IMPORT FAILED")
    print("=" * 60)
    print(import_error)
    print("=" * 60)
    
    # Create minimal error app
    try:
        from flask import Flask
        error_app = Flask(__name__)
        @error_app.route('/<path:path>')
        @error_app.route('/')
        def error_handler(path=''):
            return f"<h1>Import Error</h1><pre>{import_error}</pre>", 500
        flask_app = error_app
        print("✓ Error Flask app created")
    except Exception as flask_err:
        print(f"✗ Could not create error app: {flask_err}")
        import_error += f"\n\nAlso failed to create error app: {flask_err}"

except Exception as e:
    import_error = f"Unexpected Error: {str(e)}\n{traceback.format_exc()}"
    print("=" * 60)
    print("UNEXPECTED ERROR")
    print("=" * 60)
    print(import_error)
    print("=" * 60)
    
    # Create minimal error app
    try:
        from flask import Flask
        error_app = Flask(__name__)
        @error_app.route('/<path:path>')
        @error_app.route('/')
        def error_handler(path=''):
            return f"<h1>Error</h1><pre>{import_error}</pre>", 500
        flask_app = error_app
    except:
        pass

def handler(req, res):
    """Vercel handler function"""
    try:
        if flask_app is None:
            error_msg = "Flask app is None"
            if import_error:
                error_msg += f"\n\n{import_error}"
            res.status(500)
            res.headers['Content-Type'] = 'text/html'
            res.send(f"<h1>Error</h1><pre>{error_msg}</pre>")
            return
        
        # Debug: Print request object info
        print(f"Handler called - Request type: {type(req)}")
        print(f"Request attributes: {[attr for attr in dir(req) if not attr.startswith('_')]}")
        
        # Extract request info safely
        method = 'GET'
        try:
            method = getattr(req, 'method', 'GET') or 'GET'
            print(f"Method: {method}")
        except Exception as e:
            print(f"Error getting method: {e}")
        
        # Try multiple ways to get path
        path = '/'
        try:
            # Try req.path first
            if hasattr(req, 'path'):
                path = req.path
                print(f"Got path from req.path: {path}")
            # Try req.url
            elif hasattr(req, 'url'):
                url = req.url
                path = url.split('?')[0] if '?' in str(url) else str(url)
                print(f"Got path from req.url: {path}")
            # Try accessing as dict
            elif hasattr(req, 'get'):
                path = req.get('path', '/')
                print(f"Got path from req.get: {path}")
            else:
                print("Could not find path attribute, using '/'")
                path = '/'
            
            # Normalize path
            if isinstance(path, str):
                if '?' in path:
                    path = path.split('?')[0]
                if not path.startswith('/'):
                    path = '/' + path
            else:
                path = '/'
            
            print(f"Final path: {path}")
        except Exception as e:
            print(f"Error extracting path: {e}")
            path = '/'
        
        # Get headers
        headers = {}
        try:
            if hasattr(req, 'headers') and req.headers:
                h = req.headers
                headers = dict(h) if isinstance(h, dict) else {}
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
            try:
                status_code[0] = int(str(status).split()[0])
                response_headers[0] = dict(headers_list)
            except:
                pass
        
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
        error = traceback.format_exc()
        print(f"HANDLER ERROR: {error}")
        try:
            res.status(500)
            res.headers['Content-Type'] = 'text/html'
            res.send(f"<h1>Handler Error</h1><pre>{error}</pre>")
        except:
            pass
