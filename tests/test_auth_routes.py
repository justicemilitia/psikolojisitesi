import unittest
from flask import url_for
from app import create_app, db
from app.models.user import User
from app.config import TestingConfig

class AuthRoutesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create routes
        with self.app.test_request_context():
            self.register_url = url_for('auth.register')
            self.login_url = url_for('auth.login')
            self.logout_url = url_for('auth.logout')
            self.token_url = url_for('auth.get_token')
    
    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_register_page(self):
        """Test register page loads correctly"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
    
    def test_login_page(self):
        """Test login page loads correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_successful_registration(self):
        """Test successful user registration"""
        response = self.client.post(
            self.register_url,
            data={
                'email': 'test@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            },
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been created', response.data)
        
        # Verify user was created in database
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
    
    def test_registration_with_existing_email(self):
        """Test registration with an existing email"""
        # Create a user
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Try to register with the same email
        response = self.client.post(
            self.register_url,
            data={
                'email': 'test@example.com',
                'password': 'password456',
                'confirm_password': 'password456'
            },
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email already exists', response.data)
    
    def test_successful_login(self):
        """Test successful login"""
        # Create a user
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Login
        response = self.client.post(
            self.login_url,
            data={
                'email': 'test@example.com',
                'password': 'password123',
                'remember': False
            },
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PsikologSitesi', response.data)  # Should redirect to home page
    
    def test_login_with_incorrect_password(self):
        """Test login with incorrect password"""
        # Create a user
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Login with incorrect password
        response = self.client.post(
            self.login_url,
            data={
                'email': 'test@example.com',
                'password': 'wrongpassword',
                'remember': False
            },
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login unsuccessful', response.data)
    
    def test_logout(self):
        """Test logout"""
        # Create a user
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Login
        self.client.post(
            self.login_url,
            data={
                'email': 'test@example.com',
                'password': 'password123',
                'remember': False
            }
        )
        
        # Logout
        response = self.client.get(self.logout_url, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PsikologSitesi', response.data)  # Should redirect to home page
    
    def test_get_token(self):
        """Test getting a JWT token"""
        # Create a user
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Get token
        response = self.client.post(
            self.token_url,
            json={
                'email': 'test@example.com',
                'password': 'password123'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('token', data)
    
    def test_get_token_with_invalid_credentials(self):
        """Test getting a JWT token with invalid credentials"""
        # Create a user
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Get token with incorrect password
        response = self.client.post(
            self.token_url,
            json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }
        )
        
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Invalid credentials')

if __name__ == '__main__':
    unittest.main()