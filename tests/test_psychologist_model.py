import unittest
import json
from datetime import datetime, date
from app import create_app, db
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.config import TestingConfig

class PsychologistModelTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_specialties_handling(self):
        """Test specialties JSON handling"""
        specialties = ['depression', 'anxiety', 'trauma']
        p = Psychologist(
            first_name='John',
            last_name='Doe'
        )
        p.set_specialties(specialties)
        db.session.add(p)
        db.session.commit()
        
        # Retrieve psychologist from database
        psychologist = Psychologist.query.first()
        self.assertEqual(psychologist.get_specialties(), specialties)
    
    def test_working_hours_handling(self):
        """Test working hours JSON handling"""
        working_hours = {
            'Monday': '09:00-17:00',
            'Tuesday': '10:00-18:00',
            'Wednesday': '09:00-17:00',
            'Thursday': '10:00-18:00',
            'Friday': '09:00-17:00'
        }
        p = Psychologist(
            first_name='John',
            last_name='Doe'
        )
        p.set_working_hours(working_hours)
        db.session.add(p)
        db.session.commit()
        
        # Retrieve psychologist from database
        psychologist = Psychologist.query.first()
        self.assertEqual(psychologist.get_working_hours(), working_hours)
    
    def test_full_name_property(self):
        """Test full_name property"""
        p = Psychologist(
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(p.full_name, 'John Doe')
    
    def test_availability_checking(self):
        """Test availability checking"""
        # Create a psychologist with working hours
        working_hours = {
            'Monday': '09:00-17:00',
            'Tuesday': '10:00-18:00'
        }
        p = Psychologist(
            first_name='John',
            last_name='Doe'
        )
        p.set_working_hours(working_hours)
        db.session.add(p)
        db.session.commit()
        
        # Create a test date (Monday)
        monday = date(2023, 1, 2)  # A Monday
        
        # Test time within working hours
        time_within = datetime.strptime('10:00', '%H:%M').time()
        self.assertTrue(p.is_available(monday, time_within))
        
        # Test time outside working hours
        time_outside = datetime.strptime('08:00', '%H:%M').time()
        self.assertFalse(p.is_available(monday, time_outside))
        
        # Test day without working hours (Sunday)
        sunday = date(2023, 1, 1)  # A Sunday
        self.assertFalse(p.is_available(sunday, time_within))

if __name__ == '__main__':
    unittest.main()