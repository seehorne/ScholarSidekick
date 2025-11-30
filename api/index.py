"""
Vercel Serverless Entry Point - Minimal Test
"""

def app(environ, start_response):
    """WSGI application - simplest possible response"""
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b'Python is working on Vercel!\nPath: api/index.py\nRuntime: Python WSGI']

