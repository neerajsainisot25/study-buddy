from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__, 
                static_folder='../static', 
                static_url_path='/static',
                template_folder='../templates')
    app.config.from_object(config_class)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Health check route
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({"ok": True}), 200

    # Register blueprints
    from app.routes import chat_bp, quiz_bp, calendar_bp
    from app.routes.rag import rag_bp
    from app.routes.analytics import analytics_bp
    
    # Main app routes
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(rag_bp, url_prefix='/api/rag')
    
    # Route for chat.html template
    @app.route('/chat')
    def chat_page():
        from flask import render_template
        return render_template('chat.html')
    
    # Route for quiz list page
    @app.route('/quiz/list')
    def quiz_list_page():
        from flask import render_template
        return render_template('quiz_list.html')
    
    # Route for schedule page
    @app.route('/schedule')
    def schedule_page():
        from flask import render_template
        return render_template('schedule.html')
    
    # Route for analytics page
    @app.route('/analytics')
    def analytics_page():
        from flask import render_template
        return render_template('analytics.html')

    # Routes for template components (for modular structure)
    @app.route('/templates/<path:filename>')
    def serve_template(filename):
        from flask import send_from_directory
        import os
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        return send_from_directory(template_dir, filename)

    # Main route - serve index.html from root
    @app.route('/')
    def index():
        from flask import send_from_directory
        import os
        root_dir = os.path.dirname(os.path.dirname(__file__))
        return send_from_directory(root_dir, 'index.html')

    return app
