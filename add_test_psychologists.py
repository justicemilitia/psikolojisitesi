#!/usr/bin/env python3
"""
Script to add test psychologists for testing the chatbot functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.psychologist import Psychologist
import json

def add_test_psychologists():
    """Add test psychologists to the database"""
    app = create_app()
    
    with app.app_context():
        # Create all tables first
        try:
            db.create_all()
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"⚠️ Warning creating tables: {e}")
        
        # Check if psychologists already exist
        try:
            existing_count = Psychologist.query.count()
            if existing_count > 0:
                print(f"Psychologists already exist: {existing_count}")
                return
        except Exception as e:
            print(f"⚠️ Warning checking existing psychologists: {e}")
        
        # Add test psychologists with anger management specialty
        psychologists = [
            {
                'first_name': 'Dr. Mehmet',
                'last_name': 'Özkan',
                'specialties': json.dumps(['Anger Management', 'Stress Management', 'General Counseling']),
                'bio': 'Öfke yönetimi ve stres kontrolü konularında 10 yıllık deneyime sahip uzman psikolog.',
                'working_hours': json.dumps({
                    'Monday': '09:00-17:00',
                    'Tuesday': '09:00-17:00', 
                    'Wednesday': '09:00-17:00',
                    'Thursday': '09:00-17:00',
                    'Friday': '09:00-17:00',
                    'Saturday': 'Not available',
                    'Sunday': 'Not available'
                })
            },
            {
                'first_name': 'Dr. Ayşe',
                'last_name': 'Demir',
                'specialties': json.dumps(['Anxiety Disorders', 'Depression', 'Anger Management']),
                'bio': 'Anksiyete, depresyon ve öfke kontrolü alanlarında uzman klinik psikolog.',
                'working_hours': json.dumps({
                    'Monday': '10:00-18:00',
                    'Tuesday': '10:00-18:00',
                    'Wednesday': '10:00-18:00', 
                    'Thursday': '10:00-18:00',
                    'Friday': '10:00-16:00',
                    'Saturday': '09:00-13:00',
                    'Sunday': 'Not available'
                })
            },
            {
                'first_name': 'Dr. Fatma',
                'last_name': 'Yılmaz',
                'specialties': json.dumps(['Relationship Issues', 'Family Therapy', 'Anger Management']),
                'bio': 'Aile terapisi ve ilişki sorunları konusunda uzman, öfke yönetimi sertifikalı psikolog.',
                'working_hours': json.dumps({
                    'Monday': '08:00-16:00',
                    'Tuesday': '08:00-16:00',
                    'Wednesday': '08:00-16:00',
                    'Thursday': '08:00-16:00', 
                    'Friday': '08:00-14:00',
                    'Saturday': 'Not available',
                    'Sunday': 'Not available'
                })
            },
            {
                'first_name': 'Dr. Ali',
                'last_name': 'Kaya',
                'specialties': json.dumps(['Trauma & PTSD', 'Anxiety Disorders', 'General Counseling']),
                'bio': 'Travma ve anksiyete bozuklukları konusunda uzman klinik psikolog.',
                'working_hours': json.dumps({
                    'Monday': '09:00-17:00',
                    'Tuesday': '09:00-17:00',
                    'Wednesday': '09:00-17:00',
                    'Thursday': '09:00-17:00',
                    'Friday': '09:00-15:00',
                    'Saturday': 'Not available',
                    'Sunday': 'Not available'
                })
            }
        ]

        try:
            for p_data in psychologists:
                psychologist = Psychologist(**p_data)
                db.session.add(psychologist)
            
            db.session.commit()
            print("✅ Test psychologists added successfully!")
            print(f"Total psychologists: {Psychologist.query.count()}")
            
            # List added psychologists
            for p in Psychologist.query.all():
                print(f"- {p.full_name}: {', '.join(p.get_specialties())}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding psychologists: {e}")

if __name__ == '__main__':
    add_test_psychologists()