import unittest
from flask import url_for
from datetime import date, time
from app import create_app, db
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.config import TestingConfig

class UserRoutesTestCase(unittest.TestCase):
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
        
        # Create test appointments
        self.appointment1 = Appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=date(2023, 1, 2),  # A Monday
            appointment_time=time(10, 0),  # 10:00 AM
            status='planned'
        )
        db.session.add(self.appointment1)
        
        self.appointment2 = Appointment(
            user_id=self.user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=date(2023, 1, 3),  # A Tuesday
            appointment_time=time(11, 0),  # 11:00 AM
            status='cancelled'
        )
        db.session.add(self.appointment2)
        
        db.session.commit()
        
        # Create routes
        with self.app.test_request_context():
            self.profile_url = url_for('user.profile')
            self.appointments_url = url_for('user.appointments')
            self.appointment_detail_url = url_for('user.appointment_detail', appointment_id=self.appointment1.id)
            self.cancel_appointment_url = url_for('user.cancel_appointment', appointment_id=self.appointment1.id)
    
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
    
    def test_profile_page_unauthenticated(self):
        """Test profile page when not logged in"""
        response = self.client.get(self.profile_url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
    
    def test_profile_page_authenticated(self):
        """Test profile page when logged in"""
        # Login
        self.login()
        
        # Access profile page
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User Profile', response.data)
        self.assertIn(b'user@example.com', response.data)
    
    def test_update_profile(self):
        """Test updating user profile"""
        # Login
        self.login()
        
        # Update profile
        response = self.client.post(
            self.profile_url,
            data={
                'email': 'updated@example.com',
                'current_password': 'password123',
                'new_password': 'newpassword123',
                'confirm_new_password': 'newpassword123',
                'submit': 'Update Profile'
            },
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your profile has been updated', response.data)
        
        # Verify user was updated in database
        user = User.query.get(self.user.id)
        self.assertEqual(user.email, 'updated@example.com')
        self.assertTrue(user.check_password('newpassword123'))
    
    def test_update_profile_with_incorrect_password(self):
        """Test updating profile with incorrect current password"""
        # Login
        self.login()
        
        # Update profile with incorrect password
        response = self.client.post(
            self.profile_url,
            data={
                'email': 'updated@example.com',
                'current_password': 'wrongpassword',
                'new_password': 'newpassword123',
                'confirm_new_password': 'newpassword123',
                'submit': 'Update Profile'
            },
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Current password is incorrect', response.data)
        
        # Verify user was not updated in database
        user = User.query.get(self.user.id)
        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.check_password('password123'))
    
    def test_appointments_page_unauthenticated(self):
        """Test appointments page when not logged in"""
        response = self.client.get(self.appointments_url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
    
    def test_appointments_page_authenticated(self):
        """Test appointments page when logged in"""
        # Login
        self.login()
        
        # Access appointments page
        response = self.client.get(self.appointments_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Appointments', response.data)
        self.assertIn(b'Upcoming Appointments', response.data)
        self.assertIn(b'Past Appointments', response.data)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'2023-01-02', response.data)  # Appointment1 date
        self.assertIn(b'2023-01-03', response.data)  # Appointment2 date
    
    def test_appointment_detail_page(self):
        """Test appointment detail page"""
        # Login
        self.login()
        
        # Access appointment detail page
        response = self.client.get(self.appointment_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Appointment Detail', response.data)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'2023-01-02', response.data)  # Appointment date
        self.assertIn(b'10:00', response.data)  # Appointment time
    
    def test_appointment_detail_page_unauthorized(self):
        """Test appointment detail page for another user's appointment"""
        # Create another user
        other_user = User(email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        
        # Create appointment for other user
        other_appointment = Appointment(
            user_id=other_user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=date(2023, 1, 4),  # A Wednesday
            appointment_time=time(10, 0),  # 10:00 AM
            status='planned'
        )
        db.session.add(other_appointment)
        db.session.commit()
        
        # Login as original user
        self.login()
        
        # Try to access other user's appointment
        with self.app.test_request_context():
            other_detail_url = url_for('user.appointment_detail', appointment_id=other_appointment.id)
        
        response = self.client.get(other_detail_url)
        self.assertEqual(response.status_code, 404)
    
    def test_cancel_appointment(self):
        """Test appointment cancellation"""
        # Login
        self.login()
        
        # Cancel appointment
        response = self.client.post(self.cancel_appointment_url, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Appointment cancelled successfully', response.data)
        
        # Verify appointment status was updated
        appointment = Appointment.query.get(self.appointment1.id)
        self.assertEqual(appointment.status, 'cancelled')
    
    def test_cancel_appointment_unauthorized(self):
        """Test cancelling another user's appointment"""
        # Create another user
        other_user = User(email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        
        # Create appointment for other user
        other_appointment = Appointment(
            user_id=other_user.id,
            psychologist_id=self.psychologist.id,
            appointment_date=date(2023, 1, 4),  # A Wednesday
            appointment_time=time(10, 0),  # 10:00 AM
            status='planned'
        )
        db.session.add(other_appointment)
        db.session.commit()
        
        # Login as original user
        self.login()
        
        # Try to cancel other user's appointment
        with self.app.test_request_context():
            other_cancel_url = url_for('user.cancel_appointment', appointment_id=other_appointment.id)
        
        response = self.client.post(other_cancel_url, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Appointment not found', response.data)
        
        # Verify appointment status was not updated
        other_appointment = Appointment.query.get(other_appointment.id)
        self.assertEqual(other_appointment.status, 'planned')

if __name__ == '__main__':
    unittest.main()