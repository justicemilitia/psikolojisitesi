from app import db
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from datetime import datetime, timedelta

class PsychologistService:
    """Service for psychologist-related operations"""
    
    @staticmethod
    def get_all_psychologists():
        """Get all psychologists"""
        return Psychologist.query.all()
    
    @staticmethod
    def get_psychologist_by_id(psychologist_id):
        """Get a psychologist by ID"""
        return Psychologist.query.get(psychologist_id)
    
    @staticmethod
    def filter_by_specialty(specialty):
        """Filter psychologists by specialty"""
        # This is a simple implementation that checks if the specialty is in the list
        # A more sophisticated approach would use full-text search or a separate table
        psychologists = Psychologist.query.all()
        filtered = []
        
        for psychologist in psychologists:
            specialties = psychologist.get_specialties()
            if specialty.lower() in [s.lower() for s in specialties]:
                filtered.append(psychologist)
        
        return filtered
    
    @staticmethod
    def create_psychologist(first_name, last_name, specialties, bio, working_hours):
        """Create a new psychologist"""
        psychologist = Psychologist(
            first_name=first_name,
            last_name=last_name,
            bio=bio
        )
        
        # Set specialties and working hours
        psychologist.set_specialties(specialties)
        psychologist.set_working_hours(working_hours)
        
        # Save to database
        db.session.add(psychologist)
        db.session.commit()
        
        return psychologist
    
    @staticmethod
    def update_psychologist(psychologist_id, **kwargs):
        """Update a psychologist's information"""
        psychologist = Psychologist.query.get(psychologist_id)
        if not psychologist:
            return None
        
        # Update fields
        if 'first_name' in kwargs:
            psychologist.first_name = kwargs['first_name']
        if 'last_name' in kwargs:
            psychologist.last_name = kwargs['last_name']
        if 'bio' in kwargs:
            psychologist.bio = kwargs['bio']
        if 'specialties' in kwargs:
            psychologist.set_specialties(kwargs['specialties'])
        if 'working_hours' in kwargs:
            psychologist.set_working_hours(kwargs['working_hours'])
        
        # Save changes
        db.session.commit()
        
        return psychologist
    
    @staticmethod
    def get_available_slots(psychologist_id, date):
        """Get available time slots for a psychologist on a specific date"""
        psychologist = Psychologist.query.get(psychologist_id)
        if not psychologist:
            return []
        
        # Get working hours for the day
        working_hours = psychologist.get_working_hours()
        day_of_week = date.strftime('%A')
        
        if day_of_week not in working_hours:
            return []
        
        day_hours = working_hours[day_of_week]
        if not day_hours:
            return []
        
        # Parse working hours
        start_time_str, end_time_str = day_hours.split('-')
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        # Generate time slots (assuming 1-hour appointments)
        slots = []
        slot_time = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        while slot_time < end_datetime:
            slot = slot_time.time()
            
            # Check if slot is available
            conflict = Appointment.check_conflict(
                psychologist_id=psychologist_id,
                appointment_date=date,
                appointment_time=slot
            )
            
            if not conflict:
                slots.append(slot)
            
            # Move to next slot
            slot_time += timedelta(hours=1)
        
        return slots