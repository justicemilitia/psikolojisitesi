# Import routes to make them available when importing from the routes package
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.psychologist import psychologist_bp
from app.routes.appointment import appointment_bp
from app.routes.chatbot import chatbot_bp
from app.routes.matching import matching_bp
from app.routes.errors import register_error_handlers