"""Main entry point for the Flask application"""
from app import create_app
from app.config import Config
import socket

def find_free_port(start_port=5000, max_attempts=10):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return start_port  # Fallback to default

app = create_app(Config)

if __name__ == '__main__':
    # Try to use configured port, or find a free one
    port = Config.PORT
    try:
        # Test if port is available
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
    except OSError:
        # Port is in use, find a free one
        port = find_free_port(Config.PORT)
        print(f"⚠️  Port {Config.PORT} is in use. Using port {port} instead.")
        print(f"🌐 Access the app at: http://localhost:{port}")
    
    app.run(debug=Config.DEBUG, port=port, host='0.0.0.0')
