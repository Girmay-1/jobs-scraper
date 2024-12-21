from flask import Flask
from app.database.database_init import db
import os

def create_app():
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///jobs.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Register error handlers
    from .error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app