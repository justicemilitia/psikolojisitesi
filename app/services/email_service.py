from flask import render_template
from flask_mail import Message
from datetime import datetime, timedelta
from app import mail, scheduler

def _send_appointment_approval_email(app, user, appointment):
    """
    Randevu onay mailini gönderen yardımcı fonksiyon.
    Bu fonksiyon, uygulama bağlamı içinde çalışır.
    """
    with app.app_context():
        try:
            msg = Message(
                'Appointment Confirmation',
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user.email]
            )
            
            msg.html = render_template(
                'email/appointment_approval.html',
                user=user,
                appointment=appointment
            )
            
            mail.send(msg)
            app.logger.info(f"Appointment confirmation email has been sent to {user.email}.")
        
        except Exception as e:
            app.logger.error(f"An error occurred while sending the appointment confirmation email: {e}")
            
def send_appointment_confirmation_email(app, user, appointment):
    """
    Kullanıcıya yeni randevusunu onaylayan bir e-posta gönderir.
    """
    with app.app_context(): # `app` parametresi kullanılarak bağlam oluşturulur
        try:
            msg = Message(
                'Your appointment has been made.',
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user.email]
            )
            
            msg.html = render_template(
                'email/appointment_confirmation.html',
                user=user,
                appointment=appointment
            )
            
            mail.send(msg)
            
            scheduler.add_job(
                func=lambda: _send_appointment_approval_email(app, user, appointment),
                trigger='date',
                run_date=datetime.now() + timedelta(minutes=1)
            )
            
        except Exception as e:
            app.logger.error(f"Email could not be sent: {e}")
        
