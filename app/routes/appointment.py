from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.services.appointment_service import AppointmentService
from app.services.psychologist_service import PsychologistService
from app.forms.appointment_forms import AppointmentForm
from datetime import datetime

appointment_bp = Blueprint('appointment', __name__, url_prefix='/appointments')

@appointment_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_appointment():
    """Create a new appointment"""
    form = AppointmentForm()
    
    # Populate psychologist choices
    psychologists = PsychologistService.get_all_psychologists()
    form.psychologist_id.choices = [(p.id, p.full_name) for p in psychologists]
    
    if form.validate_on_submit():
        # Parse date and time
        try:
            appointment_date = datetime.strptime(form.date.data, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(form.time.data, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return render_template('appointment/create.html', title='Book Appointment', form=form)
        
        # Create appointment
        appointment, message = AppointmentService.create_appointment(
            user_id=current_user.id,
            psychologist_id=form.psychologist_id.data,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        
        
        
        if appointment:
            flash('Appointment created successfully', 'success')
            return redirect(url_for('appointment.appointment_detail', appointment_id=appointment.id))
        else:
            if not appointment:
                flash(message, 'danger')
                # Eğer mesaj seans hakkı ile ilgiliyse abonelik sayfasına yönlendir
                if "abonelik" in message:
                    return redirect(url_for('subscription.list_subscriptions'))
                return redirect(request.referrer or url_for('main.index'))
    
    return render_template('appointment/create.html', title='Book Appointment', form=form)

@appointment_bp.route('/<int:appointment_id>')
@login_required
def appointment_detail(appointment_id):
    """Get details for a specific appointment"""
    appointment = AppointmentService.get_appointment_by_id(appointment_id)
    
    if not appointment or appointment.user_id != current_user.id:
        return render_template('errors/404.html'), 404
    
    return render_template('appointment/detail.html', title='Appointment Detail', appointment=appointment)

@appointment_bp.route('/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    success, message = AppointmentService.cancel_appointment(
        appointment_id=appointment_id,
        user_id=current_user.id
    )
    
    if success:
        flash('Appointment cancelled successfully', 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('user.appointments'))

@appointment_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_appointment():
    """API endpoint for creating an appointment"""
    data = request.json
    
    try:
        appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['time'], '%H:%M').time()
    except (ValueError, KeyError):
        return jsonify({'success': False, 'message': 'Invalid date or time format'}), 400
    
    appointment, message = AppointmentService.create_appointment(
        user_id=current_user.id,
        psychologist_id=data['psychologist_id'],
        appointment_date=appointment_date,
        appointment_time=appointment_time
    )
    
    if appointment:
        return jsonify({
            'success': True,
            'message': 'Appointment created successfully',
            'appointment_id': appointment.id
        })
    else:
        return jsonify({'success': False, 'message': message}), 400