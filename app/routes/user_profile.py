from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.forms.auth_forms import UpdateProfileForm, UpdatePasswordForm 
from app import db

user_profile_bp = Blueprint('user_profile', __name__)

@user_profile_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """Kullanıcı hesap bilgilerini gösterir ve günceller."""
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        db.session.commit()
        flash('Hesap bilgileriniz başarıyla güncellendi.', 'success')
        return redirect(url_for('user_profile.account'))
    
    form.full_name.data = current_user.full_name
    return render_template('user/account.html', form=form)

@user_profile_bp.route('/my-subscription')
@login_required
def my_subscription():
    """Kullanıcının mevcut abonelik bilgilerini gösterir."""
    # Plan detaylarını subscription rotasından alabiliriz.
    from app.routes.subscription import PLANS
    plan_details = PLANS.get(current_user.subscription_plan)
    return render_template('user/my_subscription.html', plan_details=plan_details)

@user_profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Kullanıcının şifre güncelleme sayfasını gösterir ve şifre günceller."""
    form = UpdatePasswordForm()
    
    if form.validate_on_submit():
        old_password = form.old_password.data
        new_password = form.new_password.data
        
        # Eski şifrenin doğruluğunu kontrol et
        if current_user.check_password(old_password):
            current_user.set_password(new_password)
            db.session.commit()
            flash('Şifreniz başarıyla güncellendi.', 'success')
            return redirect(url_for('user_profile.profile')) # Başarılı olursa aynı sayfada kal
        else:
            flash('Eski şifreniz yanlış.', 'danger')
            
    return render_template('user/profile.html', form=form)