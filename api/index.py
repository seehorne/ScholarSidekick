"""
Vercel serverless entry point for ScholarSidekick Flask API
"""
import sys
import os

# Add parent directory to path so we can import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment for Vercel
os.environ['VERCEL'] = '1'

try:
    from app.main import app
    
    # Health check route for debugging
    @app.route('/api/debug')
    def debug_info():
        return {
            "status": "running",
            "python_version": sys.version,
            "database_url_set": bool(os.getenv('DATABASE_URL')),
            "vercel_env": bool(os.getenv('VERCEL')),
        }
    
except Exception as e:
    # If import fails, create a minimal Flask app for debugging
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/api/<path:path>')
    def error_handler(path=''):
        return jsonify({
            "error": "Failed to initialize app",
            "message": str(e),
            "type": type(e).__name__,
            "python_path": sys.path,
        }), 500

# Vercel will use this app object

