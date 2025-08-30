import unittest
from datetime import datetime, date, time
from app import create_app, db
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
from app.config import TestingConfig

class AppointmentServiceTestCase(unittest.TestCase):
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
        
        # Test date and time
        self.test_date = date(2023, 1, 2)  # A Monday
        self.test_time = time(10, 0)  # 10:00 AM
    
    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_appointment(self):
        """Test creating an appointment"""
        appointment, message = AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        self.assertIsNotNone(appointment)
        self.assertEqual(message, "Appointment created successfully")
        self.assertEqual(appointment.user_id, self.user.id)
        self.assertEqual(appointment.psychologist_id, self.psychologist.id)
        self.assertEqual(appointment.appointment_date, self.test_date)
        self.assertEqual(appointment.appointment_time, self.test_time)
        self.assertEqual(appointment.status, 'planned')
        
        # Verify appointment was saved to database
        appointment_from_db = Appointment.query.first()
        self.assertIsNotNone(appointment_from_db)
    
    def test_create_appointment_with_invalid_user(self):
        """Test creating an appointment with an invalid user"""
        appointment, message = AppointmentService.create_appointment(
            user_id=999,  # Non-existent user ID
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        self.assertIsNone(appointment)
        self.assertEqual(message, "User or psychologist not found")
    
    def test_create_appointment_with_invalid_psychologist(self):
        """Test creating an appointment with an invalid psychologist"""
        appointment, message = AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=999,  # Non-existent psychologist ID
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        self.assertIsNone(appointment)
        self.assertEqual(message, "User or psychologist not found")
    
    def test_create_appointment_with_conflict(self):
        """Test creating an appointment with a time conflict"""
        # Create first appointment
        AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        # Try to create another appointment at the same time
        appointment, message = AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        self.assertIsNone(appointment)
        self.assertEqual(message, "This time slot is already booked")
    
    def test_get_appointment_by_id(self):
        """Test getting an appointment by ID"""
        # Create an appointment
        created_appointment, _ = AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        # Get appointment by ID
        appointment = AppointmentService.get_appointment_by_id(created_appointment.id)
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.id, created_appointment.id)
        
        # Test non-existent ID
        appointment = AppointmentService.get_appointment_by_id(999)
        self.assertIsNone(appointment)
    
    def test_get_appointments_by_user(self):
        """Test getting appointments for a user"""
        # Create an appointment
        AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        # Get appointments for user
        appointments = AppointmentService.get_appointments_by_user(self.user.id)
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0].user_id, self.user.id)
        
        # Test non-existent user
        appointments = AppointmentService.get_appointments_by_user(999)
        self.assertEqual(len(appointments), 0)
    
    def test_cancel_appointment(self):
        """Test cancelling an appointment"""
        # Create an appointment
        created_appointment, _ = AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        # Cancel the appointment
        success, message = AppointmentService.cancel_appointment(
            appointment_id=created_appointment.id,
            user_id=self.user.id
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Appointment cancelled successfully")
        
        # Verify appointment status was updated
        appointment = Appointment.query.get(created_appointment.id)
        self.assertEqual(appointment.status, 'cancelled')
    
    def test_cancel_appointment_unauthorized(self):
        """Test cancelling an appointment by unauthorized user"""
        # Create an appointment
        created_appointment, _ = AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        # Try to cancel the appointment with a different user ID
        success, message = AppointmentService.cancel_appointment(
            appointment_id=created_appointment.id,
            user_id=999  # Different user ID
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Unauthorized")
        
        # Verify appointment status was not updated
        appointment = Appointment.query.get(created_appointment.id)
        self.assertEqual(appointment.status, 'planned')
    
    def test_get_upcoming_appointments(self):
        """Test getting upcoming appointments for a user"""
        # Create an appointment
        AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        # Get upcoming appointments
        appointments = AppointmentService.get_upcoming_appointments(self.user.id)
        self.assertEqual(len(appointments), 1)
        
        # Cancel the appointment
        appointment = appointments[0]
        appointment.cancel()
        db.session.commit()
        
        # Get upcoming appointments again (should be empty now)
        appointments = AppointmentService.get_upcoming_appointments(self.user.id)
        self.assertEqual(len(appointments), 0)
    
    def test_get_past_appointments(self):
        """Test getting past appointments for a user"""
        # Create an appointment
        AppointmentService.create_appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time
        )
        
        # Initially, there should be no past appointments
        appointments = AppointmentService.get_past_appointments(self.user.id)
        self.assertEqual(len(appointments), 0)
        
        # Complete the appointment
        appointment = Appointment.query.first()
        appointment.complete()
        db.session.commit()
        
        # Now there should be one past appointment
        appointments = AppointmentService.get_past_appointments(self.user.id)
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0].status, 'completed')

if __name__ == '__main__':
    unittest.main()