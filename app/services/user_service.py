from app import db, bcrypt
from app.models.user import User
from app.models.company import Company

class UserService:
    """Service for user-related operations"""
    
    @staticmethod
    def create_user(full_name, email, password,company_id=None):
        """Create a new user"""
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None
        
        # Create new user
        is_corporate = company_id is not None
        
        user = User(
            email=email,
            full_name=full_name, 
            is_corporate=is_corporate, 
            company_id=company_id
        )
        user.set_password(password)
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate_user(email, password, company_id=None):
        """Authenticate a user"""
        user = User.query.filter_by(email=email).first()
        if user.is_corporate:
            if user.company_id != company_id:
                return None
        else:
            if company_id is not None:
                return None
        if user and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get a user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """Get a user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_user_appointments(user_id):
        """Get all appointments for a user"""
        user = User.query.get(user_id)
        if not user:
            return []
        
        return user.appointments
    
    @staticmethod
    def update_user_profile(user_id, email, current_password, new_password):
        """Update a user's profile information, including password."""
        user = User.query.get(user_id)
        if not user:
            return False, "User not found."

        # E-posta değişikliği yapılacaksa, yeni e-postanın kullanılmadığını kontrol et
        if user.email != email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                return False, "This email is already in use by another account."
            user.email = email
            
        # Şifre değiştirme talebi varsa, eski şifreyi doğrula
        if new_password:
            if not user.check_password(current_password):
                return False, "Current password is not correct."
            user.set_password(new_password)
        
        # Değişiklikleri kaydet
        db.session.commit()
        
        return True, "Your profile has been updated successfully!"