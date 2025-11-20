"""
Minimal test handler to verify Vercel Python runtime works
"""
def handler(req, res):
    res.status(200)
    res.headers['Content-Type'] = 'text/html'
    res.send("<h1>Test Handler Works!</h1><p>Vercel Python runtime is functioning.</p>")

