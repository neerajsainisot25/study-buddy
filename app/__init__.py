from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__, 
                static_folder='../static', 
                static_url_path='/static',
                template_folder='../templates')
    app.config.from_object(config_class)
    CORS(app)

    # Register blueprints
    from app.routes import chat_bp, quiz_bp, calendar_bp
    from app.routes.rag import rag_bp
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
    app.register_blueprint(rag_bp, url_prefix='/api/rag')

    # Main route - serve index.html from root
    @app.route('/')
    def index():
        from flask import send_from_directory
        import os
        root_dir = os.path.dirname(os.path.dirname(__file__))
        return send_from_directory(root_dir, 'index.html')

    return app

