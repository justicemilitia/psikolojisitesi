import unittest
from app import create_app, db
from app.models.user import User
from app.services.user_service import UserService
from app.config import TestingConfig

class UserServiceTestCase(unittest.TestCase):
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
    
    def test_create_user(self):
        """Test user creation through service"""
        user = UserService.create_user(
            email='test@example.com',
            password='password123'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        
        # Verify user was saved to database
        user_from_db = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user_from_db)
    
    def test_create_duplicate_user(self):
        """Test creating a user with an existing email"""
        # Create first user
        UserService.create_user(
            email='test@example.com',
            password='password123'
        )
        
        # Try to create another user with the same email
        duplicate_user = UserService.create_user(
            email='test@example.com',
            password='password456'
        )
        
        # Should return None for duplicate email
        self.assertIsNone(duplicate_user)
    
    def test_authenticate_user(self):
        """Test user authentication"""
        # Create a user
        UserService.create_user(
            email='test@example.com',
            password='password123'
        )
        
        # Test valid authentication
        user = UserService.authenticate_user(
            email='test@example.com',
            password='password123'
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        
        # Test invalid password
        user = UserService.authenticate_user(
            email='test@example.com',
            password='wrongpassword'
        )
        self.assertIsNone(user)
        
        # Test non-existent user
        user = UserService.authenticate_user(
            email='nonexistent@example.com',
            password='password123'
        )
        self.assertIsNone(user)
    
    def test_get_user_by_id(self):
        """Test getting a user by ID"""
        # Create a user
        created_user = UserService.create_user(
            email='test@example.com',
            password='password123'
        )
        
        # Get user by ID
        user = UserService.get_user_by_id(created_user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        
        # Test non-existent ID
        user = UserService.get_user_by_id(999)
        self.assertIsNone(user)
    
    def test_get_user_by_email(self):
        """Test getting a user by email"""
        # Create a user
        UserService.create_user(
            email='test@example.com',
            password='password123'
        )
        
        # Get user by email
        user = UserService.get_user_by_email('test@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        
        # Test non-existent email
        user = UserService.get_user_by_email('nonexistent@example.com')
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()