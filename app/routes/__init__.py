from flask import Flask
from app.routes.github import github_bp

def create_app(config_name='default'):
    """Initialize the Flask application."""
    app = Flask(__name__)
    
    # Load configuration based on environment
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Register blueprints
    app.register_blueprint(github_bp)
    # app.register_blueprint(linkedin_bp)
    # app.register_blueprint(coding_bp)
    
    # Any other app setup
    
    return app