from datetime import datetime
from app import db


class Appointment(db.Model):
    """Appointment model for storing appointment information"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('psychologists.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), default='planned', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"Appointment('{self.appointment_date}', '{self.appointment_time}', '{self.status}')"
    
    def cancel(self):
        """Cancel the appointment"""
        if self.status == 'planned':
            self.status = 'cancelled'
            return True
        return False
    
    def complete(self):
        """Mark the appointment as completed"""
        if self.status == 'planned':
            self.status = 'completed'
            return True
        return False
    
    @staticmethod
    def check_conflict(psychologist_id, appointment_date, appointment_time):
        """Check if there's a conflict with an existing appointment"""
        return Appointment.query.filter_by(
            psychologist_id=psychologist_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='planned'
        ).first() is not None