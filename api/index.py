"""
Vercel serverless entry point for ScholarSidekick Flask API
"""
import sys
import os
import traceback

# Add parent directory to path so we can import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment for Vercel
os.environ['VERCEL'] = '1'

# Create a fallback app in case main app fails
from flask import Flask, jsonify

app = Flask(__name__)
error_log = []

try:
    # Try to import the real app
    from app.main import create_app
    app = create_app()
    error_log.append("✅ App created successfully")
    
    # Add debug endpoint
    @app.route('/api/debug')
    def debug_info():
        return jsonify({
            "status": "running",
            "python_version": sys.version,
            "database_url_set": bool(os.getenv('DATABASE_URL')),
            "vercel_env": bool(os.getenv('VERCEL')),
            "import_log": error_log,
        })
    
except Exception as e:
    # If anything fails, log it and create a minimal debugging app
    error_message = str(e)
    error_trace = traceback.format_exc()
    error_log.append(f"❌ Error: {error_message}")
    error_log.append(f"Traceback: {error_trace}")
    
    @app.route('/')
    @app.route('/health')
    @app.route('/api/<path:path>')
    def error_handler(path=''):
        return jsonify({
            "error": "Failed to initialize app",
            "message": error_message,
            "traceback": error_trace,
            "type": type(e).__name__,
            "python_version": sys.version,
            "sys_path": sys.path[:5],
            "env_vars": {
                "DATABASE_URL": "set" if os.getenv('DATABASE_URL') else "not set",
                "VERCEL": os.getenv('VERCEL', 'not set'),
            }
        }), 500

