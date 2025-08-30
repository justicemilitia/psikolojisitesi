import unittest
from flask import url_for
from app import create_app, db
from app.config import TestingConfig

class MainRoutesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create routes
        with self.app.test_request_context():
            self.index_url = url_for('main.index')
            self.about_url = url_for('main.about')
    
    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index_page(self):
        """Test index page loads correctly"""
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to PsikologSitesi', response.data)
        self.assertIn(b'Find a Psychologist', response.data)
    
    def test_about_page(self):
        """Test about page loads correctly"""
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About PsikologSitesi', response.data)
        self.assertIn(b'Our Mission', response.data)
    
    def test_error_404(self):
        """Test 404 error page"""
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)
    
    def test_index_page_links(self):
        """Test links on index page"""
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        
        # Check for psychologist link
        with self.app.test_request_context():
            psychologist_url = url_for('psychologist.list_psychologists')
            self.assertIn(psychologist_url.encode(), response.data)
        
        # Check for register link (for non-authenticated users)
        with self.app.test_request_context():
            register_url = url_for('auth.register')
            self.assertIn(register_url.encode(), response.data)

if __name__ == '__main__':
    unittest.main()