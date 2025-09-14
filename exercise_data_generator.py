#!/usr/bin/env python3
"""
Exercise Data Generator for Interactive Mental Health Exercises
Populates the database with comprehensive exercise data for testing and development
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_ml_complete import app, db, Exercise, ExerciseSession, MoodEntry, ThoughtRecord, MindfulnessSession, ExerciseStreak, AchievementUnlocked, PersonalizationData, Patient, User
from datetime import datetime, timedelta
import random
import uuid
import json

class ExerciseDataGenerator:
    """Generates comprehensive exercise data for mental health app"""
    
    def __init__(self):
        self.exercises = []
        self.sample_patients = []
    
    def generate_exercises(self):
        """Generate master list of mental health exercises"""
        
        # Check if exercises already exist
        existing_exercises = Exercise.query.count()
        if existing_exercises > 0:
            print(f"✅ Found {existing_exercises} existing exercises, skipping generation")
            return
        
        # CBT Exercises
        cbt_exercises = [
            {
                'exercise_id': 'cbt_001',
                'name': 'Thought Record Challenge',
                'type': 'cbt',
                'difficulty_level': 2,
                'estimated_duration': 10,
                'clinical_focus_areas': 'depression,anxiety,stress',
                'engagement_mechanics': 'interactive',
                'data_points_collected': 'thoughts,emotions,helpfulness',
                'description': 'Challenge negative thoughts using evidence-based CBT techniques',
                'instructions': 'Identify a distressing situation, record your thoughts, find evidence for and against, create a balanced thought.'
            },
            {
                'exercise_id': 'cbt_002',
                'name': 'Cognitive Distortion Detective',
                'type': 'cbt',
                'difficulty_level': 3,
                'estimated_duration': 15,
                'clinical_focus_areas': 'depression,anxiety',
                'engagement_mechanics': 'guided',
                'data_points_collected': 'cognitive_distortions,thoughts,insights',
                'description': 'Learn to identify and challenge common cognitive distortions',
                'instructions': 'Review common thinking errors and practice identifying them in your own thoughts.'
            },
            {
                'exercise_id': 'cbt_003',
                'name': 'Behavioral Activation Planner',
                'type': 'cbt',
                'difficulty_level': 2,
                'estimated_duration': 12,
                'clinical_focus_areas': 'depression',
                'engagement_mechanics': 'interactive',
                'data_points_collected': 'activities,mood,energy',
                'description': 'Plan enjoyable and meaningful activities to improve mood',
                'instructions': 'Schedule pleasurable activities and track their impact on your mood.'
            }
        ]
        
        # Mindfulness Exercises
        mindfulness_exercises = [
            {
                'exercise_id': 'mind_001',
                'name': '5-Minute Breathing Focus',
                'type': 'mindfulness',
                'difficulty_level': 1,
                'estimated_duration': 5,
                'clinical_focus_areas': 'anxiety,stress',
                'engagement_mechanics': 'guided',
                'data_points_collected': 'breathing_consistency,calm_rating,attention',
                'description': 'Simple breathing exercise to reduce stress and anxiety',
                'instructions': 'Follow guided breathing pattern: inhale for 4 counts, hold for 4, exhale for 6.'
            },
            {
                'exercise_id': 'mind_002',
                'name': 'Body Scan Meditation',
                'type': 'mindfulness',
                'difficulty_level': 2,
                'estimated_duration': 15,
                'clinical_focus_areas': 'stress,anxiety,insomnia',
                'engagement_mechanics': 'guided',
                'data_points_collected': 'body_awareness,relaxation,attention',
                'description': 'Progressive body scan to release tension and improve awareness',
                'instructions': 'Systematically focus attention on each part of your body, releasing tension.'
            },
            {
                'exercise_id': 'mind_003',
                'name': 'Loving-Kindness Meditation',
                'type': 'mindfulness',
                'difficulty_level': 3,
                'estimated_duration': 20,
                'clinical_focus_areas': 'depression,anger,relationships',
                'engagement_mechanics': 'guided',
                'data_points_collected': 'compassion,emotional_state,connection',
                'description': 'Cultivate compassion for yourself and others',
                'instructions': 'Generate feelings of love and kindness, first for yourself, then for others.'
            }
        ]
        
        # Mood Tracking Exercises
        mood_exercises = [
            {
                'exercise_id': 'mood_001',
                'name': 'Daily Mood Check-in',
                'type': 'mood_tracking',
                'difficulty_level': 1,
                'estimated_duration': 3,
                'clinical_focus_areas': 'depression,anxiety,mood_disorders',
                'engagement_mechanics': 'interactive',
                'data_points_collected': 'mood,intensity,energy,context',
                'description': 'Quick daily mood assessment with context tracking',
                'instructions': 'Rate your current mood, energy level, and note any relevant context.'
            },
            {
                'exercise_id': 'mood_002',
                'name': 'Mood Pattern Analysis',
                'type': 'mood_tracking',
                'difficulty_level': 2,
                'estimated_duration': 8,
                'clinical_focus_areas': 'depression,bipolar,mood_disorders',
                'engagement_mechanics': 'interactive',
                'data_points_collected': 'mood_patterns,triggers,insights',
                'description': 'Analyze mood patterns and identify triggers',
                'instructions': 'Review your mood data and identify patterns, triggers, and potential interventions.'
            }
        ]
        
        # Journaling Exercises
        journaling_exercises = [
            {
                'exercise_id': 'journal_001',
                'name': 'Gratitude Journal',
                'type': 'journaling',
                'difficulty_level': 1,
                'estimated_duration': 7,
                'clinical_focus_areas': 'depression,anxiety,wellbeing',
                'engagement_mechanics': 'self-paced',
                'data_points_collected': 'gratitude_items,mood_impact,consistency',
                'description': 'Daily gratitude practice to improve mood and perspective',
                'instructions': 'Write down three things you are grateful for each day.'
            },
            {
                'exercise_id': 'journal_002',
                'name': 'Emotion Processing Journal',
                'type': 'journaling',
                'difficulty_level': 2,
                'estimated_duration': 10,
                'clinical_focus_areas': 'trauma,anxiety,emotional_regulation',
                'engagement_mechanics': 'guided',
                'data_points_collected': 'emotions,processing,insights',
                'description': 'Process difficult emotions through structured journaling',
                'instructions': 'Write about a challenging emotion, exploring its source and potential resolution.'
            }
        ]
        
        all_exercises = cbt_exercises + mindfulness_exercises + mood_exercises + journaling_exercises
        
        for exercise_data in all_exercises:
            exercise = Exercise(**exercise_data)
            self.exercises.append(exercise)
            db.session.add(exercise)
        
        db.session.commit()
        print(f"✅ Generated {len(all_exercises)} exercises")
    
    def generate_sample_sessions(self, patient_id, num_sessions=20):
        """Generate sample exercise sessions for a patient"""
        
        exercises = Exercise.query.all()
        if not exercises:
            print("❌ No exercises found. Run generate_exercises() first.")
            return
        
        for i in range(num_sessions):
            exercise = random.choice(exercises)
            start_time = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            completion_time = start_time + timedelta(minutes=random.randint(5, exercise.estimated_duration + 10))
            
            # 80% completion rate
            if random.random() < 0.8:
                status = 'completed'
                engagement = random.randint(6, 10)
                effectiveness = random.randint(6, 10)
            else:
                status = 'abandoned'
                engagement = random.randint(1, 5)
                effectiveness = None
                completion_time = None
            
            session_data = {
                'session_id': f"session_{uuid.uuid4().hex[:8]}",
                'patient_id': patient_id,
                'exercise_id': exercise.id,
                'start_time': start_time,
                'completion_time': completion_time,
                'completion_status': status,
                'engagement_score': engagement,
                'effectiveness_rating': effectiveness,
                'collected_data': {
                    'exercise_type': exercise.type,
                    'difficulty_felt': random.randint(1, 5),
                    'time_spent': random.randint(3, exercise.estimated_duration + 5)
                }
            }
            
            session = ExerciseSession(**session_data)
            db.session.add(session)
        
        db.session.commit()
        print(f"✅ Generated {num_sessions} exercise sessions for patient {patient_id}")
    
    def generate_mood_entries(self, patient_id, num_entries=30):
        """Generate sample mood entries for a patient"""
        
        mood_emojis = ['😊', '😢', '😡', '😰', '😴', '😌', '😤', '😍', '😔', '😎']
        social_contexts = ['alone', 'with_friends', 'family', 'work', 'other']
        weather_metaphors = ['sunny', 'cloudy', 'stormy', 'calm', 'rainy']
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'gray', 'pink']
        
        for i in range(num_entries):
            timestamp = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            
            mood_data = {
                'mood_id': f"mood_{uuid.uuid4().hex[:8]}",
                'patient_id': patient_id,
                'timestamp': timestamp,
                'mood_emoji': random.choice(mood_emojis),
                'intensity_level': random.randint(1, 10),
                'energy_level': random.randint(1, 10),
                'sleep_quality': random.randint(1, 10) if random.random() < 0.7 else None,
                'social_context': random.choice(social_contexts) if random.random() < 0.8 else None,
                'weather_mood_metaphor': random.choice(weather_metaphors) if random.random() < 0.6 else None,
                'color_selection': random.choice(colors) if random.random() < 0.5 else None,
                'notes_brief': f"Sample mood entry {i+1}" if random.random() < 0.3 else None
            }
            
            mood_entry = MoodEntry(**mood_data)
            db.session.add(mood_entry)
        
        db.session.commit()
        print(f"✅ Generated {num_entries} mood entries for patient {patient_id}")
    
    def generate_thought_records(self, patient_id, num_records=15):
        """Generate sample CBT thought records for a patient"""
        
        situation_categories = ['work', 'social', 'health', 'family', 'other']
        emotions = ['anxiety', 'anger', 'sadness', 'frustration', 'fear', 'guilt', 'shame']
        cognitive_distortions = ['all_or_nothing', 'catastrophizing', 'mind_reading', 'overgeneralization', 'emotional_reasoning']
        
        for i in range(num_records):
            timestamp = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            
            thought_data = {
                'record_id': f"thought_{uuid.uuid4().hex[:8]}",
                'patient_id': patient_id,
                'timestamp': timestamp,
                'situation_category': random.choice(situation_categories),
                'emotions_identified': ','.join(random.sample(emotions, random.randint(1, 3))),
                'thought_content': f"Sample negative thought {i+1}: I'm not good enough at this.",
                'evidence_for': f"Evidence supporting thought {i+1}: I made a mistake recently.",
                'evidence_against': f"Evidence against thought {i+1}: I have succeeded many times before.",
                'balanced_thought': f"Balanced thought {i+1}: I'm learning and improving, mistakes are part of growth.",
                'helpfulness_rating': random.randint(6, 10),
                'cognitive_distortions': ','.join(random.sample(cognitive_distortions, random.randint(1, 2))) if random.random() < 0.7 else None
            }
            
            thought_record = ThoughtRecord(**thought_data)
            db.session.add(thought_record)
        
        db.session.commit()
        print(f"✅ Generated {num_records} thought records for patient {patient_id}")
    
    def generate_mindfulness_sessions(self, patient_id, num_sessions=25):
        """Generate sample mindfulness sessions for a patient"""
        
        exercise_types = ['meditation', 'breathing', 'body_scan', 'loving_kindness']
        
        for i in range(num_sessions):
            exercise_type = random.choice(exercise_types)
            duration_planned = random.choice([5, 10, 15, 20])
            start_time = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            
            # 85% completion rate
            if random.random() < 0.85:
                status = 'completed'
                duration_actual = random.randint(duration_planned - 2, duration_planned + 5)
                end_time = start_time + timedelta(minutes=duration_actual)
                attention_checks = random.randint(2, 5)
                breathing_consistency = random.randint(6, 10)
                calm_rating = random.randint(6, 10)
                technique_effectiveness = random.randint(6, 10)
            else:
                status = 'interrupted'
                duration_actual = random.randint(1, duration_planned - 1)
                end_time = start_time + timedelta(minutes=duration_actual)
                attention_checks = random.randint(0, 2)
                breathing_consistency = random.randint(1, 5)
                calm_rating = random.randint(1, 5)
                technique_effectiveness = random.randint(1, 5)
            
            session_data = {
                'session_id': f"mind_{uuid.uuid4().hex[:8]}",
                'patient_id': patient_id,
                'exercise_type': exercise_type,
                'duration_planned': duration_planned,
                'duration_actual': duration_actual,
                'attention_checks_passed': attention_checks,
                'breathing_consistency': breathing_consistency,
                'post_session_calm_rating': calm_rating,
                'interruption_count': random.randint(0, 3),
                'technique_effectiveness': technique_effectiveness,
                'start_time': start_time,
                'end_time': end_time,
                'completion_status': status
            }
            
            session = MindfulnessSession(**session_data)
            db.session.add(session)
        
        db.session.commit()
        print(f"✅ Generated {num_sessions} mindfulness sessions for patient {patient_id}")
    
    def generate_engagement_data(self, patient_id):
        """Generate engagement and gamification data for a patient"""
        
        # Exercise streaks
        exercise_types = ['cbt', 'mindfulness', 'mood_tracking', 'journaling']
        for exercise_type in exercise_types:
            current_streak = random.randint(0, 14)
            longest_streak = max(current_streak, random.randint(0, 30))
            
            streak_data = {
                'patient_id': patient_id,
                'exercise_type': exercise_type,
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'last_completion_date': datetime.now().date() - timedelta(days=random.randint(0, 7)) if current_streak > 0 else None,
                'streak_start_date': datetime.now().date() - timedelta(days=current_streak) if current_streak > 0 else None
            }
            
            streak = ExerciseStreak(**streak_data)
            db.session.add(streak)
        
        # Achievements
        achievements = [
            {'name': 'First Steps', 'description': 'Completed your first exercise', 'criteria': 'first_exercise'},
            {'name': 'Week Warrior', 'description': '7-day exercise streak', 'criteria': '7_day_streak'},
            {'name': 'Mindful Master', 'description': 'Completed 10 mindfulness sessions', 'criteria': '10_mindfulness_sessions'},
            {'name': 'Thought Challenger', 'description': 'Completed 5 CBT exercises', 'criteria': '5_cbt_exercises'},
            {'name': 'Mood Tracker', 'description': 'Logged mood for 7 consecutive days', 'criteria': '7_day_mood_streak'}
        ]
        
        for achievement in random.sample(achievements, random.randint(2, 4)):
            achievement_data = {
                'patient_id': patient_id,
                'achievement_type': random.choice(['streak', 'completion', 'improvement']),
                'achievement_name': achievement['name'],
                'achievement_description': achievement['description'],
                'criteria_met': achievement['criteria'],
                'unlocked_at': datetime.now() - timedelta(days=random.randint(1, 30))
            }
            
            achievement_obj = AchievementUnlocked(**achievement_data)
            db.session.add(achievement_obj)
        
        # Personalization data
        personalization_data = {
            'patient_id': patient_id,
            'preferred_exercise_types': ','.join(random.sample(['cbt', 'mindfulness', 'mood_tracking'], random.randint(1, 3))),
            'preferred_duration_range': random.choice(['5-10_minutes', '10-15_minutes', '15-20_minutes']),
            'preferred_difficulty_level': random.randint(1, 4),
            'best_time_of_day': random.choice(['morning', 'afternoon', 'evening', 'night']),
            'engagement_patterns': {
                'most_engaged_day': random.choice(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']),
                'preferred_session_length': random.randint(5, 20),
                'completion_rate': random.uniform(0.6, 0.95)
            },
            'effectiveness_insights': {
                'most_effective_exercise': random.choice(['cbt', 'mindfulness', 'mood_tracking']),
                'best_duration': random.randint(8, 15),
                'optimal_time': random.choice(['morning', 'afternoon', 'evening'])
            }
        }
        
        personalization = PersonalizationData(**personalization_data)
        db.session.add(personalization)
        
        db.session.commit()
        print(f"✅ Generated engagement data for patient {patient_id}")

def main():
    """Main function to generate all exercise data"""
    generator = ExerciseDataGenerator()
    
    with app.app_context():
        print("🚀 Starting Exercise Data Generation...")
        
        # Generate master exercise list
        print("\n📋 Generating master exercise list...")
        generator.generate_exercises()
        
        # Get existing patients
        patients = Patient.query.all()
        if not patients:
            print("❌ No patients found. Please run integrate_phq9_data.py first to create patients.")
            return
        
        print(f"\n👥 Found {len(patients)} patients. Generating exercise data...")
        
        # Generate exercise data for each patient
        for i, patient in enumerate(patients[:5]):  # Limit to first 5 patients for testing
            print(f"\n📊 Generating data for patient {patient.first_name} {patient.last_name}...")
            
            # Generate different types of data
            generator.generate_sample_sessions(patient.id, num_sessions=random.randint(15, 30))
            generator.generate_mood_entries(patient.id, num_entries=random.randint(25, 40))
            generator.generate_thought_records(patient.id, num_records=random.randint(10, 20))
            generator.generate_mindfulness_sessions(patient.id, num_sessions=random.randint(20, 35))
            generator.generate_engagement_data(patient.id)
        
        print(f"\n✅ Exercise data generation complete!")
        print(f"📊 Generated data for {min(5, len(patients))} patients")
        print(f"🎯 Database now contains comprehensive exercise data for testing")

if __name__ == "__main__":
    main()
