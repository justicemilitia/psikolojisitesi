import unittest
from flask import url_for
from datetime import date
from app import create_app, db
from app.models.user import User
from app.models.psychologist import Psychologist
from app.config import TestingConfig

class PsychologistRoutesTestCase(unittest.TestCase):
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
        
        # Create test psychologists
        self.psychologist1 = Psychologist(
            first_name='John',
            last_name='Doe',
            bio='Experienced therapist specializing in depression and anxiety.'
        )
        self.psychologist1.set_specialties(['depression', 'anxiety'])
        self.psychologist1.set_working_hours({
            'Monday': '09:00-17:00',
            'Tuesday': '10:00-18:00'
        })
        db.session.add(self.psychologist1)
        
        self.psychologist2 = Psychologist(
            first_name='Jane',
            last_name='Smith',
            bio='Specializing in trauma and relationship counseling.'
        )
        self.psychologist2.set_specialties(['trauma', 'relationships'])
        self.psychologist2.set_working_hours({
            'Wednesday': '09:00-17:00',
            'Thursday': '10:00-18:00',
            'Friday': '09:00-15:00'
        })
        db.session.add(self.psychologist2)
        
        db.session.commit()
        
        # Create routes
        with self.app.test_request_context():
            self.list_url = url_for('psychologist.list_psychologists')
            self.detail_url = url_for('psychologist.psychologist_detail', psychologist_id=self.psychologist1.id)
            self.availability_url = url_for('psychologist.psychologist_availability', psychologist_id=self.psychologist1.id)
            self.search_url = url_for('psychologist.search_psychologists')
    
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
    
    def test_list_psychologists(self):
        """Test psychologist listing page"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Psychologists', response.data)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'Jane Smith', response.data)
    
    def test_filter_psychologists_by_specialty(self):
        """Test filtering psychologists by specialty"""
        response = self.client.get(self.list_url + '?specialty=depression')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
        self.assertNotIn(b'Jane Smith', response.data)
        
        response = self.client.get(self.list_url + '?specialty=trauma')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jane Smith', response.data)
        self.assertNotIn(b'John Doe', response.data)
    
    def test_psychologist_detail(self):
        """Test psychologist detail page"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'depression', response.data)
        self.assertIn(b'anxiety', response.data)
        self.assertIn(b'Experienced therapist', response.data)
    
    def test_psychologist_availability_unauthenticated(self):
        """Test psychologist availability page when not logged in"""
        response = self.client.get(self.availability_url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
    
    def test_psychologist_availability_authenticated(self):
        """Test psychologist availability page when logged in"""
        # Login
        self.login()
        
        # Access availability page
        response = self.client.get(self.availability_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe - Availability', response.data)
        self.assertIn(b'Available Time Slots', response.data)
    
    def test_psychologist_availability_with_date(self):
        """Test psychologist availability page with specific date"""
        # Login
        self.login()
        
        # Access availability page with date parameter
        today = date.today().strftime('%Y-%m-%d')
        response = self.client.get(self.availability_url + f'?date={today}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe - Availability', response.data)
        self.assertIn(today.encode(), response.data)
    
    def test_search_psychologists(self):
        """Test psychologist search"""
        response = self.client.get(self.search_url + '?q=depression')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Search Results', response.data)
        self.assertIn(b'depression', response.data)
        self.assertIn(b'John Doe', response.data)
        self.assertNotIn(b'Jane Smith', response.data)
    
    def test_nonexistent_psychologist(self):
        """Test accessing a non-existent psychologist"""
        with self.app.test_request_context():
            nonexistent_url = url_for('psychologist.psychologist_detail', psychologist_id=999)
        
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)

if __name__ == '__main__':
    unittest.main()