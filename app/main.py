from flask import Flask, jsonify
from flask_cors import CORS
import os
from app.database import db
from app.api.meetings import bp as meetings_bp
from app.api.cards import bp as cards_bp
from app.api.canvas import bp as canvas_bp
from app.api.google import bp as google_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scholarsidekick.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Session configuration for Google OAuth
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize database
    db.init_app(app)
    
    # CORS for frontend integration
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(meetings_bp, url_prefix='/api/meetings')
    app.register_blueprint(cards_bp, url_prefix='/api/cards')
    app.register_blueprint(canvas_bp, url_prefix='/api/canvas')
    app.register_blueprint(google_bp)  # Registers at /api/google
    
    # Root routes
    @app.route('/')
    def root():
        return jsonify({
            "message": "Welcome to ScholarSidekick API",
            "version": "1.0.0"
        })
    
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"})
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

# Create app instance
app = create_app()
