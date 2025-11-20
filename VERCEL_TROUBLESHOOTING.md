# Vercel 404 Troubleshooting Guide

## Fixes Applied

### 1. Improved Path Extraction
- Updated `api/index.py` to handle multiple ways Vercel passes the path
- Added fallback methods: `req.url`, `req.path`, `req.pathname`
- Added debug logging to help diagnose path issues

### 2. Better Error Handling
- Improved import error handling
- Added better exception catching and reporting

### 3. Route Ordering
- Moved catch-all route to the end of `app.py`
- Ensures API routes are matched before the catch-all

### 4. Vercel Configuration
- Added `functions` configuration to `vercel.json`
- Ensured all files are included in the build

## If 404 Persists

### Check Vercel Logs

1. Go to your Vercel project dashboard
2. Click on "Functions" tab
3. Check the logs for errors

### Common Issues

#### Issue 1: Handler Not Found
**Symptom**: 404 on all routes
**Solution**: 
- Verify `api/index.py` exists
- Check that `handler` function is defined
- Ensure `vercel.json` points to `api/index.py`

#### Issue 2: Import Errors
**Symptom**: 500 error or "Error Loading Application"
**Solution**:
- Check Vercel function logs
- Verify `requirements.txt` includes all dependencies
- Ensure `app.py` is in the root directory

#### Issue 3: Path Not Extracted Correctly
**Symptom**: 404 on specific routes
**Solution**:
- Check the debug logs in Vercel (should show "Vercel Handler - Path: ...")
- If path is wrong, the handler needs adjustment

#### Issue 4: Static Files Not Loading
**Symptom**: CSS/JS files return 404
**Solution**:
- Check `vercel.json` routes configuration
- Ensure static files are in `/static` directory
- Verify route: `"/static/(.*)"` → `"/static/$1"`

### Testing Locally with Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Test locally
vercel dev
```

This will help identify issues before deploying.

### Manual Debugging

Add this to `api/index.py` temporarily to see what Vercel is passing:

```python
def handler(req, res):
    # Debug: Print request object attributes
    print("Request attributes:", dir(req))
    print("Request URL:", getattr(req, 'url', 'NOT FOUND'))
    print("Request path:", getattr(req, 'path', 'NOT FOUND'))
    # ... rest of handler
```

### Alternative: Use Vercel's Python Runtime Directly

If the custom handler doesn't work, you can try using Vercel's built-in Flask support:

1. Create `api/index.py` with:
```python
from app import app
handler = app
```

2. Update `vercel.json`:
```json
{
  "functions": {
    "api/index.py": {
      "runtime": "python3.9"
    }
  }
}
```

## Deployment Checklist

- [ ] `api/index.py` exists and has `handler` function
- [ ] `vercel.json` is configured correctly
- [ ] `requirements.txt` includes Flask and flask-cors
- [ ] All files are committed to git
- [ ] Vercel project is connected to GitHub repo
- [ ] Build logs show no errors
- [ ] Function logs show handler is being called

## Still Having Issues?

1. Check Vercel function logs for specific error messages
2. Verify the handler function is being called (check logs)
3. Test with a simple "Hello World" handler first
4. Consider using Vercel's support or community forums

