from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models.user import User
from app.models.company import Company

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(min=6, max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    company_name = SelectField('Company Name', coerce=int, validators=[Optional()]) 
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        """Validate that email is not already in use"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    company_name = SelectField('Company Name', coerce=int, validators=[Optional()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class UpdateProfileForm(FlaskForm):
    """Form for updating user profile."""
    full_name = StringField('Ad Soyad', validators=[DataRequired(), Length(min=4, max=100)])
    submit = SubmitField('Bilgileri Güncelle')

class PaymentForm(FlaskForm):
    """Form for the payment screen."""
    full_name = StringField('Ad Soyad', validators=[DataRequired(), Length(min=4, max=100)])
    phone_number = StringField('Telefon Numarası', validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Ödeme Yap')
    
class UpdatePasswordForm(FlaskForm):
    """Form for updating user password."""
    old_password = PasswordField('Eski Şifre', validators=[DataRequired()])
    new_password = PasswordField('Yeni Şifre', validators=[
        DataRequired(),
        Length(min=8, message='Şifre en az 8 karakter uzunluğunda olmalıdır.')
    ])
    confirm_new_password = PasswordField('Yeni Şifre (Tekrar)', validators=[
        DataRequired(),
        EqualTo('new_password', message='Şifreler uyuşmuyor.')
    ])
    submit_password = SubmitField('Şifreyi Güncelle')