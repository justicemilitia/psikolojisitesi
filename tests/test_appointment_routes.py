import unittest
from flask import url_for
from datetime import date, time
from app import create_app, db
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.config import TestingConfig

class AppointmentRoutesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test user
        self.user = User(email='user@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        
        # Create test psychologist
        self.psychologist = Psychologist(
            first_name='John',
            last_name='Doe',
            bio='Experienced therapist specializing in depression and anxiety.'
        )
        self.psychologist.set_specialties(['depression', 'anxiety'])
        self.psychologist.set_working_hours({
            'Monday': '09:00-17:00',
            'Tuesday': '10:00-18:00'
        })
        db.session.add(self.psychologist)
        
        db.session.commit()
        
        # Test date and time
        self.test_date = date(2023, 1, 2)  # A Monday
        self.test_time = time(10, 0)  # 10:00 AM
        
        # Create routes
        with self.app.test_request_context():
            self.create_url = url_for('appointment.create_appointment')
            self.api_create_url = url_for('appointment.api_create_appointment')
    
    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login(self):
        """Helper method to log in"""
        return self.client.post(
            url_for('auth.login'),
            data={
                'email': 'user@example.com',
                'password': 'password123',
                'remember': False
            },
            follow_redirects=True
        )
    
    def test_create_appointment_page_unauthenticated(self):
        """Test create appointment page when not logged in"""
        response = self.client.get(self.create_url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
    
    def test_create_appointment_page_authenticated(self):
        """Test create appointment page when logged in"""
        # Login
        self.login()
        
        # Access create appointment page
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Book an Appointment', response.data)
        self.assertIn(b'Psychologist', response.data)
        self.assertIn(b'Date', response.data)
        self.assertIn(b'Time', response.data)
    
    def test_create_appointment_success(self):
        """Test successful appointment creation"""
        # Login
        self.login()
        
        # Create appointment
        response = self.client.post(
            self.create_url,
            data={
                'psychologist_id': self.psychologist.id,
                'date': self.test_date.strftime('%Y-%m-%d'),
                'time': self.test_time.strftime('%H:%M'),
                'submit': 'Book Appointment'
            },
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Appointment created successfully', response.data)
        
        # Verify appointment was created in database
        appointment = Appointment.query.first()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.user_id, self.user.id)
        self.assertEqual(appointment.psychologist_id, self.psychologist.id)
        self.assertEqual(appointment.appointment_date, self.test_date)
        self.assertEqual(appointment.appointment_time, self.test_time)
        self.assertEqual(appointment.status, 'planned')
    
    def test_create_appointment_with_invalid_date(self):
        """Test appointment creation with invalid date"""
        # Login
        self.login()
        
        # Create appointment with invalid date format
        response = self.client.post(
            self.create_url,
            data={
                'psychologist_id': self.psychologist.id,
                'date': 'invalid-date',
                'time': self.test_time.strftime('%H:%M'),
                'submit': 'Book Appointment'
            },
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid date', response.data)
        
        # Verify no appointment was created
        appointment = Appointment.query.first()
        self.assertIsNone(appointment)
    
    def test_appointment_detail_page(self):
        """Test appointment detail page"""
        # Login
        self.login()
        
        # Create an appointment
        appointment = Appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time,
            status='planned'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Access appointment detail page
        with self.app.test_request_context():
            detail_url = url_for('appointment.appointment_detail', appointment_id=appointment.id)
        
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Appointment Detail', response.data)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(self.test_date.strftime('%Y-%m-%d').encode(), response.data)
        self.assertIn(self.test_time.strftime('%H:%M').encode(), response.data)
    
    def test_cancel_appointment(self):
        """Test appointment cancellation"""
        # Login
        self.login()
        
        # Create an appointment
        appointment = Appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=self.test_date,
            appointment_time=self.test_time,
            status='planned'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Cancel the appointment
        with self.app.test_request_context():
            cancel_url = url_for('appointment.cancel_appointment', appointment_id=appointment.id)
        
        response = self.client.post(cancel_url, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Appointment cancelled successfully', response.data)
        
        # Verify appointment status was updated
        appointment = Appointment.query.get(appointment.id)
        self.assertEqual(appointment.status, 'cancelled')
    
    def test_api_create_appointment(self):
        """Test API endpoint for creating an appointment"""
        # Login
        self.login()
        
        # Create appointment via API
        response = self.client.post(
            self.api_create_url,
            json={
                'psychologist_id': self.psychologist.id,
                'date': self.test_date.strftime('%Y-%m-%d'),
                'time': self.test_time.strftime('%H:%M')
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Appointment created successfully')
        self.assertIn('appointment_id', data)
        
        # Verify appointment was created in database
        appointment = Appointment.query.get(data['appointment_id'])
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.user_id, self.user.id)
        self.assertEqual(appointment.psychologist_id, self.psychologist.id)
    
    def test_api_create_appointment_with_invalid_data(self):
        """Test API endpoint for creating an appointment with invalid data"""
        # Login
        self.login()
        
        # Create appointment with invalid date format
        response = self.client.post(
            self.api_create_url,
            json={
                'psychologist_id': self.psychologist.id,
                'date': 'invalid-date',
                'time': self.test_time.strftime('%H:%M')
            }
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('Invalid date', data['message'])

if __name__ == '__main__':
    unittest.main()