#!/usr/bin/env python3
"""
Script to verify that psychologist records contain English content
"""

from dotenv import load_dotenv
from app import create_app, db
from app.models.psychologist import Psychologist

# Load environment variables
load_dotenv()

def verify_english_records():
    """Verify that the records contain English content"""
    app = create_app()
    
    with app.app_context():
        # Get first 5 psychologists to verify
        psychologists = Psychologist.query.limit(5).all()
        
        print("Verifying English content in psychologist records:")
        print("=" * 60)
        
        for i, psych in enumerate(psychologists, 1):
            print(f"\nPsychologist {i}:")
            print(f"Name: {psych.full_name}")
            print(f"Specialties: {', '.join(psych.get_specialties())}")
            print(f"Bio: {psych.bio}")
            print(f"Working Hours: {psych.get_working_hours()}")
            print("-" * 40)
        
        print(f"\nTotal psychologists in database: {Psychologist.query.count()}")

if __name__ == "__main__":
    verify_english_records()