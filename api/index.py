"""
Vercel Serverless Entry Point - ScholarSidekick
"""
from flask import Flask, jsonify
import sys
import os
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['VERCEL'] = '1'

# Start with a working Flask app
app = Flask(__name__)
loading_error = None

@app.route('/')
def root():
    return jsonify({
        "message": "ScholarSidekick API",
        "status": "full app loaded" if loading_error is None else "basic flask only",
        "error_endpoint": "/api/error" if loading_error else None
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

# Try to load the full app
try:
    from app.main import create_app
    app = create_app()
    print("✅ Full app loaded successfully")
except Exception as e:
    loading_error = {
        "error": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc()
    }
    print(f"❌ Error loading full app: {e}")
    
    @app.route('/api/error')
    def show_error():
        return jsonify(loading_error), 500

