from flask import Blueprint, session, render_template,request, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html', title='Home')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html', title='About')

# DİL SEÇİMİ İÇİN YENİ ROTA
@main_bp.route('/set-language', methods=['POST'])
def set_language():
    """Kullanıcının dil tercihini oturumda günceller."""
    data = request.json
    lang = data.get('lang')
    if lang in ['tr', 'en']:
        session['lang'] = lang
        return jsonify({'success': True, 'lang': lang}), 200
    return jsonify({'success': False, 'message': 'Invalid language'}), 400