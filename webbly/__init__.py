from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///webbly.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        # Import parts of our application
        from .models import User
        from .auth import auth_bp
        from .admin import admin_bp
        from .core import core_bp
        from .themes import themes_bp
        from .plugins import plugins_bp
        
        # Register blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(core_bp)
        app.register_blueprint(themes_bp)
        app.register_blueprint(plugins_bp)
        
        # Create database tables
        db.create_all()
        
        # Check if admin user exists, if not create it
        if not User.query.filter_by(email=os.getenv('ADMIN_EMAIL')).first():
            admin = User(
                email=os.getenv('ADMIN_EMAIL'),
                username=os.getenv('ADMIN_USERNAME'),
                is_admin=True
            )
            admin.set_password(os.getenv('ADMIN_PASSWORD'))
            db.session.add(admin)
            db.session.commit()
    
    return app
