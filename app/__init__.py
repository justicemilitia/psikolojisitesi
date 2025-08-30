from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import datetime
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail() # Mail nesnesini oluşturun
scheduler = BackgroundScheduler()
app = None # Global app değişkenini burada tanımlayın

def create_app(config_class='app.config.Config'):
    """Create and configure the Flask application"""
    global app # Global app değişkenini kullanacağımızı belirtin
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app) # Mail eklentisini başlatın
    
    # Scheduler'ı başlat
    scheduler.start()
    
    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.user import user_bp
    from app.routes.psychologist import psychologist_bp
    from app.routes.appointment import appointment_bp
    from app.routes.chatbot import chatbot_bp
    from app.routes.matching import matching_bp
    from app.routes.subscription import subscription_bp
    from app.routes.user_profile import user_profile_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(psychologist_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(user_profile_bp)
    
    # Register error handlers
    from app.routes.errors import register_error_handlers
    register_error_handlers(app)
    
    # Add template context processors
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    # Database tables will be created via Flask-Migrate
    # Remove db.create_all() to avoid conflicts with migrations
    
    return app