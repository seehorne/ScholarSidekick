#!/usr/bin/env python3
"""
Setup script for Vercel Postgres database
Run this after creating Vercel Postgres and pulling env variables

Usage:
    vercel env pull .env.local
    source .env.local  # or export $(cat .env.local | xargs)
    python setup_vercel_db.py
"""

import os
from app.main import create_app
from app.database import db

def setup_database():
    """Create all database tables"""
    database_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found!")
        print("\nPlease run:")
        print("  1. vercel postgres create")
        print("  2. vercel env pull .env.local")
        print("  3. source .env.local")
        print("  4. python setup_vercel_db.py")
        return False
    
    print(f"✅ Found database URL: {database_url[:30]}...")
    
    # Create app with database URL
    os.environ['DATABASE_URL'] = database_url
    app = create_app()
    
    print("📦 Creating database tables...")
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully!")
            
            # List created tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n📋 Created tables:")
            for table in tables:
                print(f"  - {table}")
            
            print("\n🎉 Database setup complete!")
            print("\nYou can now deploy to Vercel:")
            print("  vercel --prod")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

if __name__ == "__main__":
    setup_database()
