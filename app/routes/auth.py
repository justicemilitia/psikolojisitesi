from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import create_access_token
from app.services.user_service import UserService
from app.forms.auth_forms import LoginForm, RegistrationForm
from app.models.company import Company
from wtforms.validators import DataRequired

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    # POST isteği geldiğinde form seçeneklerini ve validator'ları ayarla
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'kurumsal':
            companies = Company.query.order_by(Company.company_name).all()
            form.company_name.choices = [(c.company_id, c.company_name) for c in companies]
            # Kurumsal kullanıcı için şirket adı alanı zorunlu olmalı
            form.company_name.validators = [DataRequired(message='Lütfen şirketinizi seçiniz.')]
        else:
            # Bireysel kullanıcı için choices'ı boş bir liste yap
            form.company_name.choices = []
        
    if form.validate_on_submit():
        user_type = request.form.get('user_type')
        email = form.email.data
        password = form.password.data
        if user_type == 'kurumsal':
            full_name = request.form.get('full_name')
            company_id = form.company_name.data
            user = UserService.create_user(full_name, email=email, password=password, company_id=company_id)
            if user:
                flash('Your account has been created! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Email already exists. Please choose a different one.', 'danger')
        else:
            full_name = request.form.get('full_name')
            user = UserService.create_user(full_name=full_name, email=email, password=password)
            if user:
                flash('Your account has been created! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Email already exists. Please choose a different one.', 'danger')
    
    # GET isteği için veya doğrulama hatası sonrası için choices'ı ayarla
    if request.method == 'GET' and hasattr(form, 'company_name'):
        form.company_name.choices = []
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    # POST isteği geldiğinde form seçeneklerini ve validator'ları ayarla
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'kurumsal':
            companies = Company.query.order_by(Company.company_name).all()
            form.company_name.choices = [(c.company_id, c.company_name) for c in companies]
            # Kurumsal kullanıcı için şirket adı alanı zorunlu olmalı
            form.company_name.validators = [DataRequired(message='Lütfen şirketinizi seçiniz.')]
        else:
            # Bireysel kullanıcı için choices'ı boş bir liste yap
            form.company_name.choices = []

    if form.validate_on_submit():
        user_type = request.form.get('user_type')
        email = form.email.data
        password = form.password.data
        company_id = form.company_name.data if user_type == 'kurumsal' else None
        
        user = UserService.authenticate_user(email=email, password=password, company_id=company_id)
        
        
        if user:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    # GET isteği için veya doğrulama hatası sonrası için choices'ı ayarla
    if request.method == 'GET' and hasattr(form, 'company_name'):
        form.company_name.choices = []
    
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
def logout():
    """User logout route"""
    logout_user()
    # Eşleştirme formuna ait verileri oturumdan manuel olarak temizle
    session.pop('matching_answers', None)
    session.pop('current_step', None)
    return redirect(url_for('main.index'))

@auth_bp.route('/token', methods=['POST'])
def get_token():
    """Get JWT token for API access"""
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    user = UserService.authenticate_user(email, password)
    if not user:
        return {'message': 'Invalid credentials'}, 401
    
    access_token = create_access_token(identity=user.id)
    return {'token': access_token}, 200

@auth_bp.route('/get_companies')
def get_companies():
    """Returns a list of companies as JSON."""
    companies = Company.query.order_by(Company.company_name).all()
    company_list = [{'id': c.company_id, 'name': c.company_name} for c in companies]
    return jsonify(company_list)