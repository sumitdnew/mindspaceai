#!/usr/bin/env python3
"""
Generate Real Data for Provider Feedback System
Creates patients, PHQ-9 assessments, and exercise recommendations
"""

import sys
import os
from datetime import datetime, timedelta
import random
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_ml_complete import app, db, User, Patient, PHQ9Assessment, ExerciseSession, MoodEntry, Exercise
from phq9_exercise_integration import PHQ9ExerciseIntegration
from werkzeug.security import generate_password_hash

def create_provider_feedback_data():
    """Generate comprehensive data for provider feedback system"""
    
    with app.app_context():
        print("🚀 Generating Provider Feedback System Data...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # db.drop_all()
        # db.create_all()
        
        # 1. Create Provider Users
        print("👨‍⚕️ Creating provider users...")
        providers = []
        for i in range(1, 4):
            provider = User.query.filter_by(username=f'provider{i}').first()
            if not provider:
                provider = User(
                    username=f'provider{i}',
                    email=f'provider{i}@mindspace.com',
                    password_hash=generate_password_hash('password123'),
                    role='provider'
                )
                db.session.add(provider)
                providers.append(provider)
            else:
                providers.append(provider)
        
        # 2. Create Patient Users and Patient Records
        print("👥 Creating patient users and records...")
        patients = []
        patient_data = [
            {'name': 'John Doe', 'age': 35, 'gender': 'Male', 'username': 'patient1'},
            {'name': 'Jane Smith', 'age': 28, 'gender': 'Female', 'username': 'patient2'},
            {'name': 'Mike Johnson', 'age': 42, 'gender': 'Male', 'username': 'patient3'},
            {'name': 'Sarah Wilson', 'age': 31, 'gender': 'Female', 'username': 'patient4'},
            {'name': 'David Brown', 'age': 38, 'gender': 'Male', 'username': 'patient5'},
            {'name': 'Lisa Davis', 'age': 26, 'gender': 'Female', 'username': 'patient6'},
            {'name': 'Robert Miller', 'age': 45, 'gender': 'Male', 'username': 'patient7'},
            {'name': 'Emily Garcia', 'age': 33, 'gender': 'Female', 'username': 'patient8'}
        ]
        
        for i, data in enumerate(patient_data):
            # Create user
            user = User.query.filter_by(username=data['username']).first()
            if not user:
                user = User(
                    username=data['username'],
                    email=f"{data['username']}@mindspace.com",
                    password_hash=generate_password_hash('password123'),
                    role='patient'
                )
                db.session.add(user)
                db.session.flush()  # Get the user ID
            
            # Create patient record
            patient = Patient.query.filter_by(user_id=user.id).first()
            if not patient:
                patient = Patient(
                    user_id=user.id,
                    first_name=data['name'].split()[0],
                    last_name=data['name'].split()[1],
                    age=data['age'],
                    gender=data['gender']
                )
                db.session.add(patient)
                patients.append(patient)
            else:
                patients.append(patient)
        
        db.session.commit()
        print(f"✅ Created {len(patients)} patients")
        
        # 3. Generate PHQ-9 Assessments with varying severity levels
        print("📊 Generating PHQ-9 assessments...")
        phq9_scenarios = [
            # Patient 1: Moderate depression
            {'scores': [2, 2, 1, 2, 1, 1, 1, 0, 1], 'total': 11, 'severity': 'moderate'},
            # Patient 2: Mild depression  
            {'scores': [1, 1, 0, 1, 0, 1, 0, 0, 0], 'total': 4, 'severity': 'minimal'},
            # Patient 3: Moderately severe depression
            {'scores': [3, 3, 2, 3, 2, 2, 2, 1, 2], 'total': 20, 'severity': 'moderately_severe'},
            # Patient 4: Severe depression
            {'scores': [3, 3, 3, 3, 3, 3, 3, 2, 3], 'total': 26, 'severity': 'severe'},
            # Patient 5: Mild depression
            {'scores': [1, 2, 1, 1, 1, 1, 0, 0, 1], 'total': 8, 'severity': 'mild'},
            # Patient 6: Moderate depression
            {'scores': [2, 2, 2, 2, 1, 2, 1, 0, 1], 'total': 13, 'severity': 'moderate'},
            # Patient 7: Moderately severe depression
            {'scores': [3, 2, 3, 2, 2, 3, 2, 1, 2], 'total': 20, 'severity': 'moderately_severe'},
            # Patient 8: Mild depression
            {'scores': [1, 1, 1, 1, 1, 1, 1, 0, 0], 'total': 7, 'severity': 'mild'}
        ]
        
        assessments = []
        for i, patient in enumerate(patients):
            if i < len(phq9_scenarios):
                scenario = phq9_scenarios[i]
                
                # Create PHQ-9 assessment
                assessment = PHQ9Assessment(
                    patient_id=patient.id,
                    assessment_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                    q1_score=scenario['scores'][0],
                    q2_score=scenario['scores'][1],
                    q3_score=scenario['scores'][2],
                    q4_score=scenario['scores'][3],
                    q5_score=scenario['scores'][4],
                    q6_score=scenario['scores'][5],
                    q7_score=scenario['scores'][6],
                    q8_score=scenario['scores'][7],
                    q9_score=scenario['scores'][8],
                    total_score=scenario['total'],
                    severity_level=scenario['severity'],
                    q9_risk_flag=scenario['scores'][8] > 0
                )
                db.session.add(assessment)
                assessments.append(assessment)
        
        db.session.commit()
        print(f"✅ Created {len(assessments)} PHQ-9 assessments")
        
        # 4. Generate Exercise Recommendations using PHQ9ExerciseIntegration
        print("🏃‍♂️ Generating exercise recommendations...")
        integration = PHQ9ExerciseIntegration()
        
        for assessment in assessments:
            try:
                # Get patient info
                patient = Patient.query.get(assessment.patient_id)
                
                # Generate recommendations using the integration system
                recommendations = integration.generate_adaptive_recommendations(
                    patient_id=patient.id,
                    assessment_id=assessment.id
                )
                
                print(f"  📋 Patient {patient.user.first_name} {patient.user.last_name}: "
                      f"PHQ-9 Score {assessment.total_score} ({assessment.severity_level})")
                print(f"     Daily: {recommendations.get('daily_exercises', [])}")
                print(f"     Weekly: {recommendations.get('weekly_exercises', [])}")
                
            except Exception as e:
                print(f"  ❌ Error generating recommendations for patient {assessment.patient_id}: {e}")
        
        # 5. Create Exercise records first
        print("🏃‍♂️ Creating exercise records...")
        exercise_data = [
            {'exercise_id': 'mood_check_in', 'name': 'Daily Mood Check-in', 'type': 'mood_tracking', 'difficulty': 1, 'duration': 2, 'description': 'Quick mood assessment and tracking', 'instructions': 'Rate your current mood on a scale of 1-10'},
            {'exercise_id': 'cbt_thought_record', 'name': 'CBT Thought Record', 'type': 'cbt', 'difficulty': 2, 'duration': 10, 'description': 'Cognitive restructuring exercise', 'instructions': 'Identify negative thoughts and challenge them with evidence'},
            {'exercise_id': 'mindfulness_exercise', 'name': 'Mindfulness Meditation', 'type': 'mindfulness', 'difficulty': 2, 'duration': 15, 'description': 'Guided mindfulness practice', 'instructions': 'Follow the guided meditation and focus on your breathing'},
            {'exercise_id': 'behavioral_activation', 'name': 'Activity Planning', 'type': 'behavioral', 'difficulty': 2, 'duration': 20, 'description': 'Structured activity scheduling', 'instructions': 'Plan and schedule enjoyable activities for the week'},
            {'exercise_id': 'sleep_hygiene', 'name': 'Sleep Hygiene Assessment', 'type': 'assessment', 'difficulty': 1, 'duration': 5, 'description': 'Sleep pattern assessment and improvement strategies', 'instructions': 'Answer questions about your sleep habits'},
            {'exercise_id': 'breathing_exercise', 'name': 'Breathing Exercise', 'type': 'breathing', 'difficulty': 1, 'duration': 5, 'description': 'Guided breathing for anxiety management', 'instructions': 'Follow the breathing pattern to reduce anxiety'}
        ]
        
        exercises = {}
        for ex_data in exercise_data:
            exercise = Exercise.query.filter_by(exercise_id=ex_data['exercise_id']).first()
            if not exercise:
                exercise = Exercise(
                    exercise_id=ex_data['exercise_id'],
                    name=ex_data['name'],
                    type=ex_data['type'],
                    difficulty_level=ex_data['difficulty'],
                    estimated_duration=ex_data['duration'],
                    clinical_focus_areas='depression, anxiety',
                    engagement_mechanics='interactive',
                    data_points_collected='mood, engagement',
                    description=ex_data['description'],
                    instructions=ex_data['instructions']
                )
                db.session.add(exercise)
            exercises[ex_data['exercise_id']] = exercise
        
        db.session.commit()
        print(f"✅ Created {len(exercises)} exercise records")
        
        # 6. Generate some exercise session history
        print("📈 Generating exercise session history...")
        exercise_types = list(exercises.keys())
        
        for patient in patients:
            # Generate 3-8 exercise sessions per patient
            num_sessions = random.randint(3, 8)
            for i in range(num_sessions):
                session_date = datetime.now() - timedelta(days=random.randint(1, 30))
                exercise_type = random.choice(exercise_types)
                exercise = exercises[exercise_type]
                
                session = ExerciseSession(
                    session_id=f"session_{patient.id}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    patient_id=patient.id,
                    exercise_id=exercise.id,
                    start_time=session_date,
                    completion_time=session_date + timedelta(minutes=random.randint(5, 30)) if random.random() > 0.2 else None,
                    completion_status='completed' if random.random() > 0.2 else 'abandoned',
                    engagement_score=random.randint(4, 10),
                    effectiveness_rating=random.randint(5, 10)
                )
                db.session.add(session)
        
        db.session.commit()
        print("✅ Generated exercise session history")
        
        # 7. Generate mood entries
        print("😊 Generating mood entries...")
        mood_emojis = ['😊', '😢', '😡', '😴', '😌', '😰', '😤', '😔', '😄', '😟']
        intensity_levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        for patient in patients:
            # Generate 5-15 mood entries per patient
            num_entries = random.randint(5, 15)
            for i in range(num_entries):
                entry_date = datetime.now() - timedelta(days=random.randint(1, 30))
                intensity = random.choice(intensity_levels)
                energy = random.choice(intensity_levels)
                sleep_quality = random.choice(intensity_levels)
                
                mood_entry = MoodEntry(
                    mood_id=f"mood_{patient.id}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    patient_id=patient.id,
                    timestamp=entry_date,
                    mood_emoji=random.choice(mood_emojis),
                    intensity_level=intensity,
                    energy_level=energy,
                    sleep_quality=sleep_quality
                )
                db.session.add(mood_entry)
        
        db.session.commit()
        print("✅ Generated mood entries")
        
        # 7. Print summary
        print("\n🎉 Data Generation Complete!")
        print("=" * 50)
        print(f"👨‍⚕️ Providers: {len(providers)}")
        print(f"👥 Patients: {len(patients)}")
        print(f"📊 PHQ-9 Assessments: {len(assessments)}")
        print(f"🏃‍♂️ Exercise Sessions: {ExerciseSession.query.count()}")
        print(f"😊 Mood Entries: {MoodEntry.query.count()}")
        print("\n🔑 Login Credentials:")
        print("   Providers: provider1/password123, provider2/password123, provider3/password123")
        print("   Patients: patient1/password123, patient2/password123, etc.")
        print("\n🌐 Access the provider feedback system at:")
        print("   http://localhost:5000/provider/exercise_feedback")

if __name__ == '__main__':
    create_provider_feedback_data()
