from app import db, app
from app.models.appointment import Appointment
from app.models.psychologist import Psychologist
from app.models.user import User
#from flask import current_app # current_app'i içe aktarın
from .email_service import send_appointment_confirmation_email
from datetime import datetime

class AppointmentService:
    """Service for appointment-related operations"""
    
    @staticmethod
    def create_appointment(user_id, psychologist_id, appointment_date, appointment_time):
        """Create a new appointment"""
        # Check if user and psychologist exist
        user = User.query.get(user_id)
        psychologist = Psychologist.query.get(psychologist_id)
        
        if not user or not psychologist:
            return None, "User or psychologist not found"
        
        # ▼▼▼ ABONELİK KONTROL MANTIĞI ▼▼▼
        can_book, reason = user.can_book_appointment()
        if not can_book:
            if reason == "NO_SESSIONS":
                return None, "You do not have an active subscription or enough session credits to create an appointment. Please select a subscription plan."
            else:
                return None, "You are not authorized to create an appointment."
        # ▲▲▲ ABONELİK KONTROL MANTIĞI ▲▲▲
        
        # Check for conflicts
        conflict = Appointment.check_conflict(
            psychologist_id=psychologist_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        
        if conflict:
            return None, "This time slot is already booked"
        
        # Check if psychologist is available at this time
        if not psychologist.is_available(appointment_date, appointment_time):
            return None, "Psychologist is not available at this time"
        
        # Create appointment
        appointment = Appointment(
            user_id=user_id,
            psychologist_id=psychologist_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='planned'
        )
        
        # Save to database
        db.session.add(appointment)
        # ▼▼▼ SEANS HAKKINI DÜŞÜRME ▼▼▼
        user.use_session()
        # ▲▲▲ SEANS HAKKINI DÜŞÜRME ▲▲▲
        db.session.commit()
        
        # ▼▼▼ E-POSTA GÖNDERME İŞLEMİNİ ÇAĞIRIN ▼▼▼
        # Randevu başarıyla oluşturulduktan sonra e-posta gönder.
        # `user` nesnesi zaten elimizde var. Model'e eklediğimiz ilişki sayesinde
        # `appointment.psychologist` şablonda otomatik olarak çalışacaktır.
        send_appointment_confirmation_email(app, user, appointment)
        # ▲▲▲ E-POSTA GÖNDERME İŞLEMİ BİTTİ ▲▲▲
        
        return appointment, "Appointment created successfully"
    
    @staticmethod
    def get_appointment_by_id(appointment_id):
        """Get an appointment by ID"""
        return Appointment.query.get(appointment_id)
    
    @staticmethod
    def get_appointments_by_user(user_id):
        """Get all appointments for a user"""
        return Appointment.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_appointments_by_psychologist(psychologist_id):
        """Get all appointments for a psychologist"""
        return Appointment.query.filter_by(psychologist_id=psychologist_id).all()
    
    @staticmethod
    def cancel_appointment(appointment_id, user_id):
        """Cancel an appointment"""
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return False, "Appointment not found"
        
        # Check if the appointment belongs to the user
        if appointment.user_id != user_id:
            return False, "Unauthorized"
        
        user = User.query.get(user_id)
        if not user:
            return False, "User associated with the appointment not found."
        
        # Cancel the appointment
        success = appointment.cancel()
        if success:
            # ▼▼▼ SEANS İADE MANTIĞI ▼▼▼
            # Restore a session if the user has a subscription and has used their free trial.
            if hasattr(user, 'has_used_free_trial') and user.has_used_free_trial == 1 and \
               hasattr(user, 'subscription_plan') and user.subscription_plan is not None:
                
                if hasattr(user, 'remaining_sessions'):
                    user.remaining_sessions += 1
            # ▲▲▲ SEANS İADE MANTIĞI ▲▲▲
            db.session.commit()
            return True, "Appointment cancelled successfully"
        
        return False, "Cannot cancel this appointment"
    
    @staticmethod
    def complete_appointment(appointment_id, psychologist_id):
        """Mark an appointment as completed"""
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return False, "Appointment not found"
        
        # Check if the appointment belongs to the psychologist
        if appointment.psychologist_id != psychologist_id:
            return False, "Unauthorized"
        
        # Complete the appointment
        success = appointment.complete()
        if success:
            db.session.commit()
            return True, "Appointment marked as completed"
        
        return False, "Cannot complete this appointment"
    
    @staticmethod
    def get_upcoming_appointments(user_id):
        """Get upcoming appointments for a user"""
        now = datetime.now()
        return Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.status == 'planned',
            (Appointment.appointment_date > now.date()) |
            ((Appointment.appointment_date == now.date()) & (Appointment.appointment_time > now.time()))
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    @staticmethod
    def get_past_appointments(user_id):
        """Get past appointments for a user"""
        now = datetime.now()

        # Önce geçmiş 'planned' randevuların status'unu completed yap
        past_planned = Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.status == 'planned',
            (Appointment.appointment_date < now.date()) |
            ((Appointment.appointment_date == now.date()) & (Appointment.appointment_time <= now.time()))
        ).all()

        for appt in past_planned:
            appt.status = 'completed'
        if past_planned:
            db.session.commit()

        # Ardından tüm geçmiş randevuları getir
        return Appointment.query.filter(
            Appointment.user_id == user_id,
            (
                (Appointment.status.in_(['completed', 'cancelled'])) |
                (Appointment.status == 'planned') &
                (
                    (Appointment.appointment_date < now.date()) |
                    ((Appointment.appointment_date == now.date()) & (Appointment.appointment_time <= now.time()))
                )
            )
        ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()