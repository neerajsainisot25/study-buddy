"""Main entry point for the Flask application"""
from app import create_app
from app.config import Config
import os

app = create_app(Config)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🌐 Starting Flask app on port {port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(debug=debug, port=port, host='0.0.0.0', use_reloader=False)
