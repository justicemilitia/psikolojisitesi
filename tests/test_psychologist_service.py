import unittest
from datetime import datetime, date, time
from app import create_app, db
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.services.psychologist_service import PsychologistService
from app.config import TestingConfig

class PsychologistServiceTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test psychologists
        self.psychologist1 = PsychologistService.create_psychologist(
            first_name='John',
            last_name='Doe',
            specialties=['depression', 'anxiety'],
            bio='Experienced therapist specializing in depression and anxiety.',
            working_hours={
                'Monday': '09:00-17:00',
                'Tuesday': '10:00-18:00'
            }
        )
        
        self.psychologist2 = PsychologistService.create_psychologist(
            first_name='Jane',
            last_name='Smith',
            specialties=['trauma', 'relationships'],
            bio='Specializing in trauma and relationship counseling.',
            working_hours={
                'Wednesday': '09:00-17:00',
                'Thursday': '10:00-18:00',
                'Friday': '09:00-15:00'
            }
        )
    
    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_all_psychologists(self):
        """Test getting all psychologists"""
        psychologists = PsychologistService.get_all_psychologists()
        self.assertEqual(len(psychologists), 2)
    
    def test_get_psychologist_by_id(self):
        """Test getting a psychologist by ID"""
        psychologist = PsychologistService.get_psychologist_by_id(self.psychologist1.id)
        self.assertIsNotNone(psychologist)
        self.assertEqual(psychologist.first_name, 'John')
        self.assertEqual(psychologist.last_name, 'Doe')
        
        # Test non-existent ID
        psychologist = PsychologistService.get_psychologist_by_id(999)
        self.assertIsNone(psychologist)
    
    def test_filter_by_specialty(self):
        """Test filtering psychologists by specialty"""
        # Filter by depression (should find psychologist1)
        psychologists = PsychologistService.filter_by_specialty('depression')
        self.assertEqual(len(psychologists), 1)
        self.assertEqual(psychologists[0].id, self.psychologist1.id)
        
        # Filter by trauma (should find psychologist2)
        psychologists = PsychologistService.filter_by_specialty('trauma')
        self.assertEqual(len(psychologists), 1)
        self.assertEqual(psychologists[0].id, self.psychologist2.id)
        
        # Filter by non-existent specialty
        psychologists = PsychologistService.filter_by_specialty('nonexistent')
        self.assertEqual(len(psychologists), 0)
    
    def test_create_psychologist(self):
        """Test creating a psychologist"""
        psychologist = PsychologistService.create_psychologist(
            first_name='Robert',
            last_name='Johnson',
            specialties=['addiction', 'grief'],
            bio='Specializing in addiction and grief counseling.',
            working_hours={
                'Monday': '12:00-20:00',
                'Friday': '09:00-17:00'
            }
        )
        
        self.assertIsNotNone(psychologist)
        self.assertEqual(psychologist.first_name, 'Robert')
        self.assertEqual(psychologist.last_name, 'Johnson')
        self.assertEqual(psychologist.get_specialties(), ['addiction', 'grief'])
        
        # Verify psychologist was saved to database
        psychologist_from_db = Psychologist.query.filter_by(first_name='Robert').first()
        self.assertIsNotNone(psychologist_from_db)
    
    def test_update_psychologist(self):
        """Test updating a psychologist"""
        # Update psychologist1
        updated_psychologist = PsychologistService.update_psychologist(
            psychologist_id=self.psychologist1.id,
            first_name='John',
            last_name='Doe',
            specialties=['depression', 'anxiety', 'stress'],  # Added 'stress'
            bio='Updated bio for John Doe.',
            working_hours={
                'Monday': '09:00-17:00',
                'Tuesday': '10:00-18:00',
                'Wednesday': '09:00-17:00'  # Added Wednesday
            }
        )
        
        self.assertIsNotNone(updated_psychologist)
        self.assertEqual(updated_psychologist.bio, 'Updated bio for John Doe.')
        self.assertEqual(updated_psychologist.get_specialties(), ['depression', 'anxiety', 'stress'])
        self.assertEqual(len(updated_psychologist.get_working_hours()), 3)  # Now has 3 working days
        
        # Test updating non-existent psychologist
        result = PsychologistService.update_psychologist(
            psychologist_id=999,
            first_name='Nonexistent',
            last_name='Person'
        )
        self.assertIsNone(result)
    
    def test_get_available_slots(self):
        """Test getting available time slots"""
        # Monday (psychologist1 is available)
        monday = date(2023, 1, 2)  # A Monday
        slots = PsychologistService.get_available_slots(self.psychologist1.id, monday)
        self.assertTrue(len(slots) > 0)
        
        # Wednesday (psychologist1 is not available)
        wednesday = date(2023, 1, 4)  # A Wednesday
        slots = PsychologistService.get_available_slots(self.psychologist1.id, wednesday)
        self.assertEqual(len(slots), 0)
        
        # Create an appointment to test conflict
        appointment = Appointment(
            user_id=1,  # Dummy user ID
            psychologist_id=self.psychologist1.id,
            appointment_date=monday,
            appointment_time=time(10, 0),  # 10:00 AM
            status='planned'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Get available slots again (should exclude 10:00 AM)
        slots = PsychologistService.get_available_slots(self.psychologist1.id, monday)
        slot_times = [slot.strftime('%H:%M') for slot in slots]
        self.assertNotIn('10:00', slot_times)

if __name__ == '__main__':
    unittest.main()