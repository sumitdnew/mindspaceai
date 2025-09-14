#!/usr/bin/env python3
"""
Integration script to populate Flask app database with realistic PHQ-9 data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phq9_data_generator import PHQ9DataGenerator
from app_ml_complete import app, db, User, Patient, PHQ9Assessment, RecommendationResult, CrisisAlert
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_users():
    """Create test users for the generated data"""
    users = []
    
    # Create users for each patient persona
    test_users = [
        {'username': 'sarah_chen', 'email': 'sarah.chen@test.com', 'password': 'password123', 'role': 'patient'},
        {'username': 'emily_rodriguez', 'email': 'emily.rodriguez@test.com', 'password': 'password123', 'role': 'patient'},
        {'username': 'robert_thompson', 'email': 'robert.thompson@test.com', 'password': 'password123', 'role': 'patient'},
        {'username': 'alex_johnson', 'email': 'alex.johnson@test.com', 'password': 'password123', 'role': 'patient'},
        {'username': 'maria_garcia', 'email': 'maria.garcia@test.com', 'password': 'password123', 'role': 'patient'},
        {'username': 'david_wilson', 'email': 'david.wilson@test.com', 'password': 'password123', 'role': 'patient'},
        {'username': 'jordan_smith', 'email': 'jordan.smith@test.com', 'password': 'password123', 'role': 'patient'},
    ]
    
    for user_data in test_users:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            from werkzeug.security import generate_password_hash
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                role=user_data['role']
            )
            db.session.add(user)
            users.append(user)
            logger.info(f"Created user: {user_data['username']}")
        else:
            users.append(existing_user)
            logger.info(f"User already exists: {user_data['username']}")
    
    db.session.commit()
    return users

def create_patients(users):
    """Create patient records for the generated data"""
    patients = []
    
    patient_data = [
        {'name': 'Sarah Chen', 'age': 20, 'gender': 'Female', 'scenario': 'College student with seasonal depression'},
        {'name': 'Emily Rodriguez', 'age': 28, 'gender': 'Female', 'scenario': 'New mother with postpartum depression'},
        {'name': 'Robert Thompson', 'age': 72, 'gender': 'Male', 'scenario': 'Elderly patient with chronic depression'},
        {'name': 'Alex Johnson', 'age': 16, 'gender': 'Non-binary', 'scenario': 'Adolescent with acute depressive episode'},
        {'name': 'Maria Garcia', 'age': 35, 'gender': 'Female', 'scenario': 'Patient responding well to treatment'},
        {'name': 'David Wilson', 'age': 45, 'gender': 'Male', 'scenario': 'Treatment-resistant patient'},
        {'name': 'Jordan Smith', 'age': 22, 'gender': 'Male', 'scenario': 'Patient in crisis'},
    ]
    
    for i, data in enumerate(patient_data):
        user = users[i]
        
        # Check if patient already exists
        existing_patient = Patient.query.filter_by(user_id=user.id).first()
        if not existing_patient:
            patient = Patient(
                user_id=user.id,
                first_name=data['name'].split()[0],
                last_name=data['name'].split()[1],
                age=data['age'],
                gender=data['gender'],
                current_phq9_severity='minimal',
                total_assessments=0
            )
            db.session.add(patient)
            patients.append(patient)
            logger.info(f"Created patient: {data['name']}")
        else:
            patients.append(existing_patient)
            logger.info(f"Patient already exists: {data['name']}")
    
    db.session.commit()
    return patients

def populate_phq9_data(patients):
    """Populate database with realistic PHQ-9 assessment data"""
    generator = PHQ9DataGenerator()
    
    # Generate data for each patient
    for i, patient in enumerate(patients):
        persona_names = list(generator.personas.keys())
        persona_name = persona_names[i]
        persona = generator.personas[persona_name]
        
        logger.info(f"Generating PHQ-9 data for {persona.name} ({persona.scenario})")
        
        # Generate 24 weeks of assessments
        assessments_data = persona.generate_assessment_series(24)
        
        for assessment_data in assessments_data:
            # Create PHQ-9 assessment
            assessment = PHQ9Assessment(
                patient_id=patient.id,
                q1_score=assessment_data['q1_score'],
                q2_score=assessment_data['q2_score'],
                q3_score=assessment_data['q3_score'],
                q4_score=assessment_data['q4_score'],
                q5_score=assessment_data['q5_score'],
                q6_score=assessment_data['q6_score'],
                q7_score=assessment_data['q7_score'],
                q8_score=assessment_data['q8_score'],
                q9_score=assessment_data['q9_score'],
                total_score=assessment_data['total_score'],
                severity_level=assessment_data['severity_level'],
                q9_risk_flag=assessment_data['q9_risk_flag'],
                assessment_date=datetime.strptime(assessment_data['assessment_date'], '%Y-%m-%d'),
                notes=f"Week {assessment_data['week_number']} assessment - {persona.scenario}"
            )
            db.session.add(assessment)
            
            # Create crisis alert if needed
            if assessment_data['crisis_alert']:
                # Flush to get the assessment ID
                db.session.flush()
                crisis_alert = CrisisAlert(
                    assessment_id=assessment.id,
                    patient_id=patient.id,
                    alert_type='high_risk_phq9',
                    alert_message=f"High-risk PHQ-9 assessment: Total score {assessment_data['total_score']}/27, Q9 score {assessment_data['q9_score']}/3",
                    severity_level='critical' if assessment_data['q9_score'] >= 2 else 'urgent',
                    acknowledged=False
                )
                db.session.add(crisis_alert)
                logger.warning(f"CRISIS ALERT: {persona.name} - Week {assessment_data['week_number']}")
        
        # Commit assessments for this patient
        db.session.commit()
        
        # Update patient summary
        patient.total_assessments = len(assessments_data)
        if assessments_data:
            latest_assessment = assessments_data[-1]
            patient.current_phq9_severity = latest_assessment['severity_level']
            patient.last_assessment_date = datetime.strptime(latest_assessment['assessment_date'], '%Y-%m-%d')
    
    db.session.commit()
    logger.info("PHQ-9 data population completed!")

def generate_crisis_testing_data():
    """Generate additional crisis testing scenarios"""
    generator = PHQ9DataGenerator()
    crisis_data = generator.generate_crisis_testing_scenarios()
    
    # Create test users for crisis scenarios
    crisis_users = [
        {'username': 'crisis_test1', 'email': 'crisis1@test.com', 'password': 'password123'},
        {'username': 'crisis_test2', 'email': 'crisis2@test.com', 'password': 'password123'},
    ]
    
    crisis_patients = []
    for i, user_data in enumerate(crisis_users):
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            # Create user
            from werkzeug.security import generate_password_hash
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                role='patient'
            )
            db.session.add(user)
            db.session.flush()
        else:
            user = existing_user
        
        # Create patient
        patient = Patient(
            user_id=user.id,
            first_name=f'Crisis{i+1}',
            last_name='Test',
            age=25,
            gender='Unknown',
            current_phq9_severity='severe',
            total_assessments=0
        )
        db.session.add(patient)
        crisis_patients.append(patient)
    
    db.session.commit()
    
    # Add crisis assessments
    for i, patient in enumerate(crisis_patients):
        start_idx = i * 12
        end_idx = start_idx + 12
        
        for j in range(start_idx, end_idx):
            assessment_data = crisis_data[j]
            
            assessment = PHQ9Assessment(
                patient_id=patient.id,
                q1_score=assessment_data['q1_score'],
                q2_score=assessment_data['q2_score'],
                q3_score=assessment_data['q3_score'],
                q4_score=assessment_data['q4_score'],
                q5_score=assessment_data['q5_score'],
                q6_score=assessment_data['q6_score'],
                q7_score=assessment_data['q7_score'],
                q8_score=assessment_data['q8_score'],
                q9_score=assessment_data['q9_score'],
                total_score=assessment_data['total_score'],
                severity_level=assessment_data['severity_level'],
                q9_risk_flag=assessment_data['q9_risk_flag'],
                assessment_date=datetime.strptime(assessment_data['assessment_date'], '%Y-%m-%d'),
                notes=f"Crisis testing scenario: {assessment_data['scenario']}"
            )
            db.session.add(assessment)
            
            if assessment_data['crisis_alert']:
                # Flush to get the assessment ID
                db.session.flush()
                crisis_alert = CrisisAlert(
                    assessment_id=assessment.id,
                    patient_id=patient.id,
                    alert_type='crisis_test',
                    alert_message=f"CRISIS TEST: {assessment_data['scenario']} - Score {assessment_data['total_score']}/27",
                    severity_level='critical',
                    acknowledged=False
                )
                db.session.add(crisis_alert)
                logger.warning(f"CRISIS TEST ALERT: {assessment_data['scenario']}")
        
        # Commit assessments for this crisis patient
        db.session.commit()
        
        patient.total_assessments = 12
        patient.current_phq9_severity = 'severe'
        patient.last_assessment_date = datetime.now()
    
    db.session.commit()
    logger.info("Crisis testing data generated!")

def main():
    """Main function to populate the database with realistic PHQ-9 data"""
    with app.app_context():
        logger.info("Starting PHQ-9 data population...")
        
        # Create test users
        users = create_test_users()
        
        # Create patients
        patients = create_patients(users)
        
        # Populate PHQ-9 data
        populate_phq9_data(patients)
        
        # Generate crisis testing scenarios
        generate_crisis_testing_data()
        
        # Print summary
        total_assessments = PHQ9Assessment.query.count()
        total_crisis_alerts = CrisisAlert.query.count()
        total_patients = Patient.query.count()
        
        logger.info("=== DATABASE POPULATION SUMMARY ===")
        logger.info(f"Total patients: {total_patients}")
        logger.info(f"Total PHQ-9 assessments: {total_assessments}")
        logger.info(f"Total crisis alerts: {total_crisis_alerts}")
        logger.info("Database population completed successfully!")

if __name__ == "__main__":
    main()
