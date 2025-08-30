import unittest
from app import create_app, db
from app.models.user import User
from app.config import TestingConfig

class UserModelTestCase(unittest.TestCase):
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
    
    def test_password_hashing(self):
        """Test password hashing"""
        u = User(email='test@example.com')
        u.set_password('password123')
        self.assertTrue(u.check_password('password123'))
        self.assertFalse(u.check_password('wrongpassword'))
    
    def test_user_creation(self):
        """Test user creation"""
        u = User(email='test@example.com')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()
        
        # Retrieve user from database
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
    
    def test_email_uniqueness(self):
        """Test email uniqueness constraint"""
        u1 = User(email='test@example.com')
        u1.set_password('password123')
        db.session.add(u1)
        db.session.commit()
        
        # Try to create another user with the same email
        u2 = User(email='test@example.com')
        u2.set_password('password456')
        db.session.add(u2)
        
        # Should raise an exception due to unique constraint
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()