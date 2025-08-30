from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User
from flask_login import current_user

class UpdateProfileForm(FlaskForm):
    """Form for updating user profile"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(min=6, max=120)
    ])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=4, max=100)])
    current_password = PasswordField('Current Password', validators=[
        DataRequired()
    ])
    new_password = PasswordField('New Password', validators=[
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Profile')
    
    def validate_email(self, email):
        """Validate that email is not already in use by another user"""
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already in use. Please choose a different one.')
    
    def validate_current_password(self, current_password):
        """Validate that current password is correct"""
        if not current_user.check_password(current_password.data):
            raise ValidationError('Current password is incorrect.')