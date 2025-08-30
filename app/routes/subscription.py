from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.forms.auth_forms import PaymentForm # Yeni ödeme formunu import et
from app.models.user import User # User modelini import et
from app import db

subscription_bp = Blueprint('subscription', __name__)

PLANS = {
    'standard': {'name': 'Standart Plan', 'price': '59€/Ay', 'features': ['Aylık 1 seans (50 dk)', 'AI destekli ön değerlendirme', 'Gelişim analiz raporu', 'Seans sonrası AI terapist notu özeti']},
    'advanced': {'name': 'Gelişmiş Plan', 'price': '89€/Ay', 'features': ['Aylık 2 seans', 'Tüm standart plan özellikleri', 'AI destekli şema analizi ve öneri modülü', 'Ruh hali takibi için mobil senkronizasyon', 'Terapi planı güncelleme algoritması']},
    'intensive': {'name': 'Yoğun Destek Planı', 'price': '149€/Ay', 'features': ['Aylık 4 seans', 'VR destekli modül erişimi (travma, bağımlılık vb.)', 'Haftalık ruh analizi ve bildirimli takip', 'Özel içeriklere ve seans sonrası kişisel önerilere erişim']}
}

PLANS_TRANSLATIONS = {
    'tr': {
        'standard': {
            'name': 'Standart Plan',
            'price': '59€/Ay',
            'features': [
                'Aylık 1 seans (50 dk)',
                'AI destekli ön değerlendirme',
                'Gelişim analiz raporu',
                'Seans sonrası AI terapist notu özeti'
            ]
        },
        'advanced': {
            'name': 'Gelişmiş Plan',
            'price': '89€/Ay',
            'features': [
                'Aylık 2 seans',
                'Tüm standart plan özellikleri',
                'AI destekli şema analizi ve öneri modülü',
                'Ruh hali takibi için mobil senkronizasyon',
                'Terapi planı güncelleme algoritması'
            ]
        },
        'intensive': {
            'name': 'Yoğun Destek Planı',
            'price': '149€/Ay',
            'features': [
                'Aylık 4 seans',
                'VR destekli modül erişimi (travma, bağımlılık vb.)',
                'Haftalık ruh analizi ve bildirimli takip',
                'Özel içeriklere ve seans sonrası kişisel önerilere erişim'
            ]
        }
    },
    'en': {
        'standard': {
            'name': 'Standard Plan',
            'price': '59€/Month',
            'features': [
                '1 session per month (50 min)',
                'AI-powered pre-assessment',
                'Progress analysis report',
                'AI therapist note summary after session'
            ]
        },
        'advanced': {
            'name': 'Advanced Plan',
            'price': '89€/Month',
            'features': [
                '2 sessions per month',
                'All standard plan features',
                'AI-powered schema analysis and suggestion module',
                'Mobile synchronization for mood tracking',
                'Therapy plan update algorithm'
            ]
        },
        'intensive': {
            'name': 'Intensive Support Plan',
            'price': '149€/Month',
            'features': [
                '4 sessions per month',
                'VR-supported module access (trauma, addiction, etc.)',
                'Weekly mood analysis and notified tracking',
                'Access to exclusive content and personalized post-session suggestions'
            ]
        }
    }
}

@subscription_bp.route('/subscriptions')
@login_required
def list_subscriptions():
    """Displays the subscription plans page."""
    return render_template('subscription/plans.html')

@subscription_bp.route('/payment/<plan_name>', methods=['GET', 'POST'])
@login_required
def payment(plan_name):
    """Ödeme sayfasını gösterir ve ödeme işlemini gerçekleştirir."""
    lang = session.get('lang', 'en')
    plans_for_lang = PLANS_TRANSLATIONS.get(lang, PLANS_TRANSLATIONS[lang])
    
    if plan_name not in plans_for_lang:
        flash('Geçersiz abonelik planı.', 'danger')
        return redirect(url_for('subscription.list_subscriptions'))

    form = PaymentForm()
    plan_details = plans_for_lang[plan_name]

    if form.validate_on_submit():
        # Kullanıcının adını ve telefonunu güncelle
        current_user.full_name = form.full_name.data
        current_user.phone_number = form.phone_number.data
        db.session.commit()
        
        # Kullanıcıyı abone yap
        success = current_user.subscribe(plan_name, form.phone_number.data)
        if success:
            return redirect(url_for('subscription.payment_success'))
        else:
            flash('Abonelik oluşturulurken bir hata oluştu.', 'danger')
            return redirect(url_for('subscription.list_subscriptions'))

    # GET isteği için formu kullanıcının mevcut bilgileriyle doldur
    form.full_name.data = current_user.full_name
    form.phone_number.data = current_user.phone_number

    return render_template('subscription/payment.html', form=form, plan_name=plan_name, plan_details=plan_details)

@subscription_bp.route('/payment/success')
@login_required
def payment_success():
    """Ödeme başarı sayfasını gösterir."""
    return render_template('subscription/payment_success.html')