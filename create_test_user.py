#!/usr/bin/env python3
"""
Script to create a test user for testing the chatbot functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def create_test_user():
    """Create a test user account"""
    app = create_app()
    
    with app.app_context():
        # Create all tables first
        try:
            db.create_all()
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"⚠️ Warning creating tables: {e}")
        
        # Check if test user already exists
        try:
            existing_user = User.query.filter_by(email='test@example.com').first()
            if existing_user:
                print("Test user already exists!")
                return
        except Exception as e:
            print(f"⚠️ Warning checking existing user: {e}")
        
        # Create new test user
        test_user = User(email='test@example.com')
        test_user.set_password('password123')
        
        try:
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created successfully!")
            print(f"Email: test@example.com")
            print(f"Password: password123")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating test user: {e}")

if __name__ == '__main__':
    create_test_user()