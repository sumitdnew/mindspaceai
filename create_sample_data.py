#!/usr/bin/env python3
"""
Sample Data Creation Script for MindSpace ML
Creates sample patients with various statuses to demonstrate the comprehensive provider dashboard
"""

from app_ml_complete import app, db, User, Patient, PHQ9Assessment, MoodEntry, ExerciseSession, ThoughtRecord, CrisisAlert, Exercise
from datetime import datetime, timedelta
import random
import numpy as np

def create_sample_data():
    """Create comprehensive sample data for dashboard testing"""
    print("🎯 Creating sample data for comprehensive provider dashboard...")
    
    with app.app_context():
        # Create a sample exercise first
        print("🏃 Creating sample exercise...")
        exercise = Exercise(
            exercise_id="deep_breathing_001",
            name="Deep Breathing Exercise",
            type="breathing",
            difficulty_level=1,
            estimated_duration=10,
            clinical_focus_areas="anxiety,stress",
            engagement_mechanics="guided",
            data_points_collected="mood,engagement",
            description="A simple breathing exercise to reduce anxiety and stress",
            instructions="Sit comfortably and take slow, deep breaths. Inhale for 4 counts, hold for 4, exhale for 4, hold for 4. Repeat for 10 minutes."
        )
        db.session.add(exercise)
        db.session.flush()
        
        # Create sample users and patients
        patients_data = [
            {
                'username': 'john_doe',
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'age': 35,
                'gender': 'Male',
                'status': 'green',  # Good progress
                'mood_trend': 'improving',
                'engagement': 'high'
            },
            {
                'username': 'jane_smith',
                'email': 'jane.smith@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'age': 28,
                'gender': 'Female',
                'status': 'yellow',  # Concerning patterns
                'mood_trend': 'declining',
                'engagement': 'medium'
            },
            {
                'username': 'mike_wilson',
                'email': 'mike.wilson@example.com',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'age': 42,
                'gender': 'Male',
                'status': 'red',  # Crisis situation
                'mood_trend': 'declining',
                'engagement': 'low'
            },
            {
                'username': 'sarah_jones',
                'email': 'sarah.jones@example.com',
                'first_name': 'Sarah',
                'last_name': 'Jones',
                'age': 31,
                'gender': 'Female',
                'status': 'orange',  # Treatment adjustment needed
                'mood_trend': 'stable',
                'engagement': 'low'
            },
            {
                'username': 'david_brown',
                'email': 'david.brown@example.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'age': 39,
                'gender': 'Male',
                'status': 'green',  # Excellent progress
                'mood_trend': 'improving',
                'engagement': 'high'
            }
        ]
        
        created_patients = []
        
        for i, patient_data in enumerate(patients_data):
            print(f"👤 Creating patient: {patient_data['first_name']} {patient_data['last_name']}")
            
            # Create user
            user = User(
                username=patient_data['username'],
                email=patient_data['email'],
                password_hash='sample_hash',
                role='patient'
            )
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create patient
            patient = Patient(
                user_id=user.id,
                first_name=patient_data['first_name'],
                last_name=patient_data['last_name'],
                age=patient_data['age'],
                gender=patient_data['gender'],
                current_phq9_severity='moderate',
                total_assessments=0
            )
            db.session.add(patient)
            db.session.flush()  # Get patient ID
            
            created_patients.append({
                'patient': patient,
                'status': patient_data['status'],
                'mood_trend': patient_data['mood_trend'],
                'engagement': patient_data['engagement']
            })
            
            # Create PHQ-9 assessments
            create_phq9_assessments(patient, patient_data['status'])
            
            # Create mood entries
            create_mood_entries(patient, patient_data['mood_trend'])
            
            # Create exercise sessions
            create_exercise_sessions(patient, patient_data['engagement'], exercise.id)
            
            # Create thought records
            create_thought_records(patient, patient_data['engagement'])
            
            # Create crisis alerts (for red status patients)
            if patient_data['status'] == 'red':
                create_crisis_alerts(patient)
        
        # Commit all changes
        db.session.commit()
        
        print(f"✅ Created {len(created_patients)} sample patients with comprehensive data")
        print("\n📊 Sample Data Summary:")
        print("- 5 patients with different status levels (Green, Yellow, Red, Orange)")
        print("- PHQ-9 assessments for each patient")
        print("- 30 days of mood tracking data")
        print("- Exercise sessions with varying completion rates")
        print("- Thought records with different engagement levels")
        print("- Crisis alerts for high-risk patients")
        print("\n🚀 You can now access the comprehensive provider dashboard!")
        print("   Login as provider1 / password123")
        print("   Navigate to: http://localhost:5000/provider/comprehensive_dashboard")

def create_phq9_assessments(patient, status):
    """Create PHQ-9 assessments based on patient status"""
    # Base scores based on status
    base_scores = {
        'green': [1, 1, 1, 1, 1, 1, 1, 1, 0],  # Low scores
        'yellow': [2, 2, 2, 2, 2, 2, 2, 2, 0],  # Moderate scores
        'orange': [2, 3, 2, 3, 2, 2, 2, 2, 0],  # Higher scores
        'red': [3, 3, 3, 3, 3, 3, 3, 3, 2]      # High scores with suicidal ideation
    }
    
    base_score = base_scores[status]
    
    # Create 3 assessments over the last 30 days
    for i in range(3):
        assessment_date = datetime.now() - timedelta(days=30 - (i * 10))
        
        # Add some variation to scores
        scores = [max(0, min(3, score + random.randint(-1, 1))) for score in base_score]
        total_score = sum(scores)
        
        assessment = PHQ9Assessment(
            patient_id=patient.id,
            q1_score=scores[0], q2_score=scores[1], q3_score=scores[2],
            q4_score=scores[3], q5_score=scores[4], q6_score=scores[5],
            q7_score=scores[6], q8_score=scores[7], q9_score=scores[8],
            total_score=total_score,
            severity_level=calculate_severity(total_score),
            q9_risk_flag=scores[8] >= 2,
            crisis_alert_triggered=scores[8] >= 2 or total_score >= 20,
            assessment_date=assessment_date,
            notes=f"Sample PHQ-9 assessment - {status} status"
        )
        db.session.add(assessment)
    
    # Update patient's last assessment
    patient.last_assessment_date = datetime.now() - timedelta(days=5)
    patient.total_assessments = 3

def create_mood_entries(patient, trend):
    """Create mood entries based on trend"""
    # Base mood scores based on trend
    if trend == 'improving':
        base_mood = 6
        trend_factor = 0.1
    elif trend == 'declining':
        base_mood = 4
        trend_factor = -0.1
    else:  # stable
        base_mood = 5
        trend_factor = 0
    
    # Create 30 days of mood entries
    for i in range(30):
        entry_date = datetime.now() - timedelta(days=29 - i)
        
        # Calculate mood score with trend
        mood_score = base_mood + (i * trend_factor) + random.uniform(-0.5, 0.5)
        mood_score = max(1, min(10, mood_score))  # Clamp between 1-10
        
        mood_entry = MoodEntry(
            mood_id=f"mood_{patient.id}_{i}",
            patient_id=patient.id,
            timestamp=entry_date,
            mood_emoji="😊" if mood_score > 6 else "😐" if mood_score > 4 else "😢",
            intensity_level=mood_score,
            energy_level=random.randint(3, 8),
            sleep_quality=random.randint(5, 9),
            social_context=random.choice(['alone', 'with_friends', 'family', 'work']),
            weather_mood_metaphor="sunny" if mood_score > 6 else "cloudy" if mood_score > 4 else "stormy",
            color_selection=random.choice(['blue', 'green', 'yellow', 'red', 'purple']),
            notes_brief=f"Sample mood entry - {trend} trend"
        )
        db.session.add(mood_entry)

def create_exercise_sessions(patient, engagement, exercise_id):
    """Create exercise sessions based on engagement level"""
    # Completion rates based on engagement
    completion_rates = {
        'high': 0.9,
        'medium': 0.6,
        'low': 0.3
    }
    
    completion_rate = completion_rates[engagement]
    
    # Create 20 exercise sessions over the last 30 days
    for i in range(20):
        session_date = datetime.now() - timedelta(days=29 - (i * 1.5))
        
        # Determine completion status
        completed = random.random() < completion_rate
        
        session = ExerciseSession(
            session_id=f"session_{patient.id}_{i}",
            patient_id=patient.id,
            exercise_id=exercise_id,
            start_time=session_date,
            completion_time=session_date + timedelta(minutes=30) if completed else None,
            completion_status='completed' if completed else 'abandoned',
            engagement_score=random.randint(6, 9) if completed else random.randint(1, 4),
            effectiveness_rating=random.randint(6, 9) if completed else None,
            collected_data={"mood_before": random.randint(3, 7), "mood_after": random.randint(5, 9)} if completed else None
        )
        db.session.add(session)

def create_thought_records(patient, engagement):
    """Create thought records based on engagement level"""
    # Completion rates based on engagement
    completion_rates = {
        'high': 0.8,
        'medium': 0.5,
        'low': 0.2
    }
    
    completion_rate = completion_rates[engagement]
    
    # Create 15 thought records over the last 30 days
    for i in range(15):
        record_date = datetime.now() - timedelta(days=29 - (i * 2))
        
        # Determine if record was completed
        completed = random.random() < completion_rate
        
        if completed:
            thought_record = ThoughtRecord(
                record_id=f"record_{patient.id}_{i}",
                patient_id=patient.id,
                situation_category=random.choice(['work', 'social', 'health', 'family', 'relationships']),
                situation_description="Sample stressful situation at work",
                primary_emotion="anxiety",
                emotion_intensity=random.randint(4, 8),
                secondary_emotions="sadness,frustration",
                initial_thought="I'm not good enough at my job",
                thought_confidence=random.randint(6, 9),
                distortions_identified="all_or_nothing,catastrophizing",
                supporting_evidence="I made a mistake on the project",
                contradicting_evidence="I've successfully completed many projects before",
                balanced_thought="I'm human and make mistakes, but I also have many successes",
                balanced_confidence=random.randint(5, 8),
                outcome_rating=random.randint(6, 9),
                mood_improvement=random.randint(2, 4),
                timestamp=record_date,
                difficulty_level="beginner",
                completion_time=random.randint(300, 600),
                ai_assisted=False
            )
            db.session.add(thought_record)

def create_crisis_alerts(patient):
    """Create crisis alerts for high-risk patients"""
    # Create 2 crisis alerts in the last week
    for i in range(2):
        alert_date = datetime.now() - timedelta(days=6 - (i * 3))
        
        alert = CrisisAlert(
            patient_id=patient.id,
            alert_type='high_risk_phq9',
            alert_message=f"High-risk PHQ-9 assessment detected for {patient.first_name} {patient.last_name}",
            severity_level='critical' if i == 0 else 'urgent',
            acknowledged=False,
            created_at=alert_date
        )
        db.session.add(alert)

def calculate_severity(total_score):
    """Calculate severity level based on total score"""
    if total_score <= 4:
        return 'minimal'
    elif total_score <= 9:
        return 'mild'
    elif total_score <= 14:
        return 'moderate'
    elif total_score <= 19:
        return 'moderately_severe'
    else:
        return 'severe'

if __name__ == "__main__":
    create_sample_data()
