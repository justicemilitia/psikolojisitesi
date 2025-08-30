import unittest
from datetime import datetime, date, time
from app import create_app, db
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.config import TestingConfig

class AppointmentModelTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(email='user@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        
        # Create test psychologist
        self.psychologist = Psychologist(
            first_name='John',
            last_name='Doe'
        )
        working_hours = {
            'Monday': '09:00-17:00',
            'Tuesday': '10:00-18:00'
        }
        self.psychologist.set_working_hours(working_hours)
        db.session.add(self.psychologist)
        
        db.session.commit()
    
    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_appointment_creation(self):
        """Test appointment creation"""
        appointment_date = date(2023, 1, 2)  # A Monday
        appointment_time = time(10, 0)  # 10:00 AM
        
        appointment = Appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='planned'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Retrieve appointment from database
        retrieved_appointment = Appointment.query.first()
        self.assertIsNotNone(retrieved_appointment)
        self.assertEqual(retrieved_appointment.user_id, self.user.id)
        self.assertEqual(retrieved_appointment.psychologist_id, self.psychologist.id)
        self.assertEqual(retrieved_appointment.appointment_date, appointment_date)
        self.assertEqual(retrieved_appointment.appointment_time, appointment_time)
        self.assertEqual(retrieved_appointment.status, 'planned')
    
    def test_appointment_status_management(self):
        """Test appointment status management"""
        appointment = Appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=date(2023, 1, 2),
            appointment_time=time(10, 0),
            status='planned'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Test cancellation
        self.assertTrue(appointment.cancel())
        self.assertEqual(appointment.status, 'cancelled')
        
        # Test completion
        appointment.status = 'planned'  # Reset status
        self.assertTrue(appointment.complete())
        self.assertEqual(appointment.status, 'completed')
        
        # Test cancellation of completed appointment (should fail)
        self.assertFalse(appointment.cancel())
        self.assertEqual(appointment.status, 'completed')
    
    def test_appointment_conflict_detection(self):
        """Test appointment conflict detection"""
        # Create an appointment
        appointment_date = date(2023, 1, 2)  # A Monday
        appointment_time = time(10, 0)  # 10:00 AM
        
        appointment = Appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='planned'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Check for conflict (should find one)
        conflict = Appointment.check_conflict(
            psychologist_id=self.psychologist.id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        self.assertTrue(conflict)
        
        # Check for conflict at different time (should not find one)
        conflict = Appointment.check_conflict(
            psychologist_id=self.psychologist.id,
            appointment_date=appointment_date,
            appointment_time=time(11, 0)  # 11:00 AM
        )
        self.assertFalse(conflict)
        
        # Check for conflict with cancelled appointment (should not find one)
        appointment.cancel()
        db.session.commit()
        
        conflict = Appointment.check_conflict(
            psychologist_id=self.psychologist.id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        self.assertFalse(conflict)

if __name__ == '__main__':
    unittest.main()