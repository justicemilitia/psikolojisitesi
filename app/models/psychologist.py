import json
from app import db
from app.models.review import Review
from sqlalchemy import func

class Psychologist(db.Model):
    """Psychologist model for storing psychologist information"""
    __tablename__ = 'psychologists'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    specialties = db.Column(db.Text)  # Stored as JSON or comma-separated string
    bio = db.Column(db.Text)
    working_hours = db.Column(db.Text)  # Stored as JSON
    languages = db.Column(db.String(255))  # Comma-separated string
    gender = db.Column(db.String(50))  # e.g.,
    profile_image_url = db.Column(db.String(500))
    education = db.Column(db.Text, nullable=True)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='psychologist', lazy=True)
    reviews = db.relationship('Review', backref='psychologist', lazy='dynamic')
    
    def __repr__(self):
        return f"Psychologist('{self.first_name} {self.last_name}')"
    
    @property
    def full_name(self):
        """Return the psychologist's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def average_rating(self):
        """Psikoloğun puan ortalamasını hesaplar."""
        avg = self.reviews.with_entities(func.avg(Review.rating)).scalar()
        return int(round(avg)) if avg else 0

    @property
    def review_count(self):
        """Psikoloğun toplam yorum sayısını döndürür."""
        return self.reviews.count()
    
    def get_specialties(self):
        """Parse and return specialties as a list"""
        if not self.specialties:
            return []
        
        try:
            # Try to parse as JSON
            return json.loads(self.specialties)
        except json.JSONDecodeError:
            # Fall back to comma-separated string
            return [s.strip() for s in self.specialties.split(',')]
    
    def get_education(self):
        """Parse and return specialties as a list"""
        if not self.education:
            return []
        
        try:
            # Try to parse as JSON
            return json.loads(self.education)
        except json.JSONDecodeError:
            # Fall back to comma-separated string
            return [s.strip() for s in self.education.split(',')]
    
    def set_specialties(self, specialties_list):
        """Convert specialties list to JSON and store it"""
        self.specialties = json.dumps(specialties_list)
    
    def get_working_hours(self):
        """Parse and return working hours as a dictionary"""
        if not self.working_hours:
            return {}
        
        try:
            return json.loads(self.working_hours)
        except json.JSONDecodeError:
            return {}
    
    def set_working_hours(self, working_hours_dict):
        """Convert working hours dictionary to JSON and store it"""
        self.working_hours = json.dumps(working_hours_dict)
    
    def is_available(self, date, time):
        """Check if the psychologist is available at the given date and time"""
        from datetime import datetime
        
        # Get working hours for the day of the week
        working_hours = self.get_working_hours()
        day_of_week = date.strftime('%A')  # e.g., 'Monday'
        
        if day_of_week not in working_hours:
            return False
        
        # Parse working hours for the day
        day_hours = working_hours[day_of_week]
        if not day_hours:
            return False
        
        # Check if the time is within working hours
        start_time_str, end_time_str = day_hours.split('-')
        
        # Convert string times to datetime.time objects for comparison
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        # Convert time parameter to datetime.time if it's a string
        if isinstance(time, str):
            time = datetime.strptime(time, '%H:%M').time()
        
        if time < start_time or time > end_time:
            return False
        
        # Check if there's an existing appointment at this time
        from app.models.appointment import Appointment
        existing_appointment = Appointment.query.filter_by(
            psychologist_id=self.id,
            appointment_date=date,
            appointment_time=time,
            status='planned'
        ).first()
        
        return existing_appointment is None