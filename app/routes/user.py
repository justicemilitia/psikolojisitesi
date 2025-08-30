from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.user_service import UserService
from app.services.appointment_service import AppointmentService
from app.forms.user_forms import UpdateProfileForm

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = UpdateProfileForm()

    if request.method == 'POST':
        # form.validate_on_submit() yerine manuel kontrol
        # Çünkü şifre alanları boş bırakılabilir
        if form.validate_on_submit():
            # Profil bilgilerini güncellemek için UserService'i kullan
            updated_user = UserService.update_user_profile(
                user=current_user,
                email=form.email.data,
                new_password=form.new_password.data if form.new_password.data else None,
                full_name=current_user.full_name # Varsayılan olarak tam adı değiştirmeyeceğiz.
            )
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('user.profile'))
        else:
            # Doğrulama hatası varsa form hatalarını flash mesajı olarak göster
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {field}: {error}", 'danger')
    
    # GET isteği için veya doğrulama hatası sonrası için form alanlarını doldur
    form.email.data = current_user.email
    form.full_name.data = current_user.full_name

    return render_template('user/profile.html', title='Profile', form=form)

@user_bp.route('/appointments')
@login_required
def appointments():
    """User appointments page"""
    upcoming_appointments = AppointmentService.get_upcoming_appointments(current_user.id)
    past_appointments = AppointmentService.get_past_appointments(current_user.id)
    
    return render_template(
        'user/appointments.html',
        title='My Appointments',
        upcoming_appointments=upcoming_appointments,
        past_appointments=past_appointments
    )

@user_bp.route('/appointments/<int:appointment_id>')
@login_required
def appointment_detail(appointment_id):
    """Appointment detail page"""
    appointment = AppointmentService.get_appointment_by_id(appointment_id)
    
    if not appointment or appointment.user_id != current_user.id:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('user.appointments'))
    
    return render_template(
        'user/appointment_detail.html',
        title='Appointment Detail',
        appointment=appointment
    )

@user_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    success, message = AppointmentService.cancel_appointment(
        appointment_id=appointment_id,
        user_id=current_user.id
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('user.appointments'))