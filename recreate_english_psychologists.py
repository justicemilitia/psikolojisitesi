#!/usr/bin/env python3
"""
Script to delete existing psychologist records and recreate 100 new ones with English content
"""

import json
import random
import os
from dotenv import load_dotenv
from app import create_app, db
from app.models.psychologist import Psychologist

# Load environment variables from .env file
load_dotenv()

# English names for psychologists
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen",
    "Charles", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra",
    "Donald", "Donna", "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
    "Kenneth", "Laura", "Kevin", "Sarah", "Brian", "Kimberly", "George", "Deborah", "Edward", "Dorothy"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

SPECIALTIES_LIST = [
    "Depression", "Anxiety", "Trauma", "Addiction", "Relationship Issues", "Stress Management",
    "Grief Counseling", "Self-Esteem", "Couples Therapy", "Family Counseling", "Child Psychology",
    "Adolescent Psychology", "Obsessive Compulsive Disorder", "Panic Attacks", "Social Phobia",
    "Eating Disorders", "Sleep Disorders", "Anger Management", "Career Counseling",
    "Personality Disorders", "Bipolar Disorder", "Schizophrenia", "ADHD", "Autism Spectrum Disorder",
    "Post-Traumatic Stress Disorder"
]

BIO_TEMPLATES = [
    "With {years} years of experience, I specialize in {specialty} and provide empathetic, solution-focused therapy to my clients.",
    "I have been working in psychology for {years} years, with expertise in {specialty}. I conduct both individual and group therapy sessions.",
    "As a psychologist with {years} years of experience in {specialty}, I focus on building a safe and supportive therapeutic relationship with my clients.",
    "I have been serving in clinical psychology for {years} years, specializing in {specialty}. I use evidence-based therapy methods in my practice.",
    "Throughout my {years} years of professional experience, I have worked with many clients in the field of {specialty}. I adopt a holistic and personalized therapy approach."
]

def generate_working_hours():
    """Generate realistic working hours for a psychologist"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    working_hours = {}
    
    for day in days:
        if random.choice([True, True, True, False]):  # 75% chance of working
            start_hour = random.choice(["08:00", "09:00", "10:00"])
            end_hour = random.choice(["17:00", "18:00", "19:00", "20:00"])
            working_hours[day] = f"{start_hour}-{end_hour}"
    
    return working_hours

def delete_all_psychologists():
    """Delete all existing psychologist records"""
    print("Deleting all existing psychologist records...")
    deleted_count = Psychologist.query.delete()
    db.session.commit()
    print(f"Deleted {deleted_count} psychologist records.")
    return deleted_count

def create_english_psychologists():
    """Create 100 new psychologist records with English content"""
    app = create_app()
    
    with app.app_context():
        # First, delete all existing records
        deleted_count = delete_all_psychologists()
        
        print("Creating 100 new psychologist records with English content...")
        
        for i in range(100):
            # Generate random name
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            
            # Generate random specialties (1-4 specialties per psychologist)
            num_specialties = random.randint(1, 4)
            specialties = random.sample(SPECIALTIES_LIST, num_specialties)
            
            # Generate bio
            years_experience = random.randint(2, 25)
            main_specialty = specialties[0]
            bio = random.choice(BIO_TEMPLATES).format(
                years=years_experience,
                specialty=main_specialty
            )
            
            # Generate working hours
            working_hours = generate_working_hours()
            
            # Create psychologist record
            psychologist = Psychologist(
                first_name=first_name,
                last_name=last_name,
                bio=bio
            )
            
            # Set specialties and working hours using the model methods
            psychologist.set_specialties(specialties)
            psychologist.set_working_hours(working_hours)
            
            db.session.add(psychologist)
            
            if (i + 1) % 10 == 0:
                print(f"Created {i + 1} psychologists...")
        
        # Commit all records
        db.session.commit()
        print("Successfully created 100 new psychologist records with English content!")
        
        # Verify the count
        total_psychologists = Psychologist.query.count()
        print(f"Total psychologists in database: {total_psychologists}")
        
        return total_psychologists

if __name__ == "__main__":
    create_english_psychologists()