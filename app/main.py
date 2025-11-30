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
    
    # Use environment variable for database URL (required for Vercel)
    database_url = os.getenv('DATABASE_URL', 'sqlite:///scholarsidekick.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Session configuration for Google OAuth
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize database
    db.init_app(app)
    
    # CORS for frontend integration - allow Vercel domains
    cors_origins = ["*"]  # Allow all origins for now
    if os.getenv('VERCEL_URL'):
        cors_origins.append(f"https://{os.getenv('VERCEL_URL')}")
    
    CORS(app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=True)
    
    # Register blueprints with error handling
    try:
        app.register_blueprint(meetings_bp, url_prefix='/api/meetings')
        app.register_blueprint(cards_bp, url_prefix='/api/cards')
        app.register_blueprint(canvas_bp, url_prefix='/api/canvas')
        app.register_blueprint(google_bp)  # Registers at /api/google
    except Exception as e:
        app.logger.error(f"Error registering blueprints: {e}")
    
    # Root routes
    @app.route('/')
    def root():
        return jsonify({
            "message": "Welcome to ScholarSidekick API",
            "version": "1.0.0",
            "environment": "vercel" if os.getenv('VERCEL') else "local"
        })
    
    @app.route('/health')
    def health_check():
        db_status = "unknown"
        try:
            # Try to ping the database
            db.session.execute(db.text('SELECT 1'))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)[:50]}"
        
        return jsonify({
            "status": "healthy",
            "database": db_status,
            "database_url_configured": bool(os.getenv('DATABASE_URL'))
        })
    
    # Create tables - but only if not on Vercel serverless
    # Vercel has read-only filesystem, so skip table creation
    if not os.getenv('VERCEL'):
        with app.app_context():
            db.create_all()
    
    return app

# Create app instance
app = create_app()
