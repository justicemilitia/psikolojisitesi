from datetime import datetime, timedelta
from flask_login import UserMixin
from app import db, bcrypt, login_manager
from app.models.company import Company

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    # ABONELİK ALANLARI
    subscription_plan = db.Column(db.String(50), nullable=True) # 'standard', 'advanced', 'intensive'
    remaining_sessions = db.Column(db.Integer, default=0)
    subscription_expiry_date = db.Column(db.DateTime, nullable=True)
    has_used_free_trial = db.Column(db.Boolean, default=False, nullable=True)
    is_corporate = db.Column(db.Boolean, default=False)
    
    
    # Relationships
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id', name='fk_users_company_id'), nullable=True)
    
    def __repr__(self):
        return f"User('{self.email}')"
    
    def set_password(self, password):
        """Hash password and store it"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        """Check if password matches the hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def has_active_subscription(self):
        """Check if the user has an active subscription."""
        return self.subscription_expiry_date and self.subscription_expiry_date > datetime.utcnow()

    def can_book_appointment(self):
        """
        Check if the user can book an appointment.
        Returns a tuple: (can_book: bool, reason: str)
        """
        if not self.has_used_free_trial:
            return True, "FREE_TRIAL"
        if self.has_active_subscription() and self.remaining_sessions > 0:
            return True, "HAS_SESSIONS"
        return False, "NO_SESSIONS"

    def use_session(self):
        """Decrement remaining sessions or use the free trial."""
        if not self.has_used_free_trial:
            self.has_used_free_trial = True
        elif self.remaining_sessions > 0:
            self.remaining_sessions -= 1
        db.session.commit()

    def subscribe(self, plan_name, phone_number):
        """Subscribes the user to a new plan."""
        plans = {
            'standard': {'sessions': 1},
            'advanced': {'sessions': 2},
            'intensive': {'sessions': 4}
        }
        if plan_name not in plans:
            return False

        self.subscription_plan = plan_name
        self.remaining_sessions = plans[plan_name]['sessions']
        self.subscription_expiry_date = datetime.utcnow() + timedelta(days=30)
        self.phone_number = phone_number # Telefon numarasını kaydet
        db.session.commit()
        return True