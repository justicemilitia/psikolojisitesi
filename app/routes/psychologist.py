from flask import Blueprint, render_template, request, jsonify, flash, url_for, redirect
from flask_login import login_required, current_user
from app.services.psychologist_service import PsychologistService
from datetime import datetime
from datetime import timedelta 
from app.models.review import Review
from app.forms.review_form import ReviewForm
from app import db

psychologist_bp = Blueprint('psychologist', __name__, url_prefix='/psychologists')

@psychologist_bp.route('/')
@login_required
def list_psychologists():
    """List all psychologists, optionally filtered by specialty"""
    specialty = request.args.get('specialty')
    
    if specialty:
        psychologists = PsychologistService.filter_by_specialty(specialty)
    else:
        psychologists = PsychologistService.get_all_psychologists()
    
    return render_template('psychologist/list.html', title='Psychologists', psychologists=psychologists)

@psychologist_bp.route('/<int:psychologist_id>')
@login_required
def psychologist_detail(psychologist_id):
    """Get details for a specific psychologist"""
    psychologist = PsychologistService.get_psychologist_by_id(psychologist_id)
    
    if not psychologist:
        return render_template('errors/404.html'), 404
    
    # Yorum formunu oluştur
    form = ReviewForm()
    # Psikoloğa ait yorumları en yeniden eskiye doğru çek
    # Modeldeki 'reviews' ilişkisini kullanıyoruz
    reviews = psychologist.reviews.order_by(Review.created_at.desc()).all()
    
    # Formu ve yorumları şablona gönder
    return render_template(
        'psychologist/detail.html', 
        title=psychologist.full_name, 
        psychologist=psychologist,
        reviews=reviews,
        form=form
    )
    
# YENİ EKLENEN ROUTE
@psychologist_bp.route('/<int:psychologist_id>/review', methods=['POST'])
@login_required
def add_review(psychologist_id):
    """Handle the submission of a new review for a psychologist."""
    form = ReviewForm()
    psychologist = PsychologistService.get_psychologist_by_id(psychologist_id)

    if not psychologist:
        flash('Psikolog bulunamadı.', 'danger')
        return redirect(url_for('psychologist.list_psychologists'))

    # Kullanıcının bu psikolog için daha önce yorum yapıp yapmadığını kontrol et
    existing_review = Review.query.filter_by(user_id=current_user.id, psychologist_id=psychologist.id).first()
    if existing_review:
        flash('Bu psikolog için zaten bir değerlendirme yaptınız.', 'info')
        return redirect(url_for('psychologist.psychologist_detail', psychologist_id=psychologist.id))

    if form.validate_on_submit():
        new_review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=current_user.id,
            psychologist_id=psychologist.id
        )
        db.session.add(new_review)
        db.session.commit()
        flash('Değerlendirmeniz için teşekkür ederiz!', 'success')
    else:
        # Form validasyonu başarısız olursa hataları flash mesaj olarak göster
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')

    return redirect(url_for('psychologist.psychologist_detail', psychologist_id=psychologist.id))

@psychologist_bp.route('/<int:psychologist_id>/availability')
@login_required
def psychologist_availability(psychologist_id):
    """Get availability for a specific psychologist"""
    date_str = request.args.get('date')
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date = datetime.today().date()
    else:
        date = datetime.today().date()
    psychologist = PsychologistService.get_psychologist_by_id(psychologist_id)
    if not psychologist:
        return render_template('errors/404.html'), 404
    all_slots = PsychologistService.get_available_slots(psychologist_id, date)
 
    # --- YENİ EKLENEN ZAMAN AYARLAMA VE FİLTRELEME KODU ---
    now_utc = datetime.utcnow()
    now_adjusted = now_utc + timedelta(hours=3)  # Türkiye saati için +3 saat
 
    filtered_slots = []
    today = now_adjusted.date()
    current_time = now_adjusted.time()
 
    for slot in all_slots:
        # Koşul: Seçilen tarih gelecekteyse VEYA seçilen tarih bugünse ve slot saati şimdiki saatten ilerideyse
        if date > today or (date == today and slot > current_time):
            filtered_slots.append(slot)
    # --- YENİ KODUN SONU ---
 
    # Eğer AJAX isteği ise, filtrelenmiş saatleri JSON olarak döndür
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'date': date.isoformat(),
            'slots': [slot.strftime('%H:%M') for slot in filtered_slots] # Değiştirildi
        })
    # Aksi halde, filtrelenmiş saatlerle şablonu render et
    return render_template(
        'psychologist/availability.html',
        title=f'{psychologist.full_name} - Availability',
        psychologist=psychologist,
        date=date,
        available_slots=filtered_slots, # Değiştirildi
        now=now_adjusted # Şablona güncel 'now' değişkenini gönder
    )

@psychologist_bp.route('/search')
def search_psychologists():
    """Search for psychologists by specialty"""
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('psychologist.list_psychologists'))
    
    psychologists = PsychologistService.filter_by_specialty(query)
    
    return render_template(
        'psychologist/search_results.html',
        title='Search Results',
        query=query,
        psychologists=psychologists
    )