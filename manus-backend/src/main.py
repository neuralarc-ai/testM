import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.tasks import tasks_bp
from src.routes.agents import agents_bp
from src.routes.content import content_bp

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'manus-ai-clone-secret-key-2025')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Use in-memory database for testing
        database_url = "sqlite:///:memory:"
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS configuration - allow all origins for development
    CORS(app, origins="*", supports_credentials=True)
    
    # JWT configuration
    jwt = JWTManager(app)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(agents_bp, url_prefix='/api/agents')
    app.register_blueprint(content_bp, url_prefix='/api/content')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'manus-ai-clone-backend',
            'version': '1.0.0'
        })
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        return jsonify({
            'name': 'Manus AI Clone API',
            'version': '1.0.0',
            'description': 'Backend API for Manus AI Clone - Autonomous AI Agent Platform',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'tasks': '/api/tasks',
                'agents': '/api/agents',
                'content': '/api/content'
            }
        })
    
    # Create database tables
    # with app.app_context():
    #     db.create_all()
    
    # Serve frontend static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return jsonify({'message': 'Manus AI Clone Backend API is running'}), 200
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
