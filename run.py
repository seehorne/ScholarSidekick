"""
Convenience script to run the Flask application
"""
import os
from dotenv import load_dotenv
from app.main import app

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "5000"))
    
    app.run(
        host=host,
        port=port,
        debug=True
    )
