#!/usr/bin/env python3
"""
Setup Script for Comprehensive Patient Action Analysis & Provider Insight System
Helps integrate the system into existing applications
"""

import os
import sys
from datetime import datetime

def print_banner():
    """Print setup banner"""
    print("=" * 80)
    print("🏥 Comprehensive Patient Action Analysis & Provider Insight System")
    print("=" * 80)
    print("Setting up real-time patient insights and provider intelligence...")
    print()

def check_dependencies():
    """Check if required dependencies are available"""
    print("📋 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_login',
        'sqlalchemy',
        'numpy',
        'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies available")
    return True

def check_database_models():
    """Check if required database models exist"""
    print("\n🗄️  Checking database models...")
    
    required_models = [
        'Patient',
        'PHQ9Assessment', 
        'ExerciseSession',
        'MoodEntry',
        'CrisisAlert',
        'ThoughtRecord',
        'MindfulnessSession'
    ]
    
    try:
        # Try to import from app_ml_complete
        from app_ml_complete import (
            Patient, PHQ9Assessment, ExerciseSession, MoodEntry,
            CrisisAlert, ThoughtRecord, MindfulnessSession
        )
        print("✅ All required database models found")
        return True
    except ImportError as e:
        print(f"❌ Database models not found: {e}")
        print("\nRequired models:")
        for model in required_models:
            print(f"  - {model}")
        return False

def create_integration_code():
    """Create integration code for the main application"""
    print("\n🔧 Creating integration code...")
    
    integration_code = '''
# Add this to your main Flask application (e.g., app_ml_complete.py)

# Import the comprehensive insights system
from comprehensive_patient_insights_system import comprehensive_insights
from real_time_patient_insights import real_time_insights
from intelligent_treatment_recommendations import treatment_recommendations
from provider_session_preparation import session_preparation

# Register the blueprints
app.register_blueprint(comprehensive_insights, url_prefix='/comprehensive-insights')
app.register_blueprint(real_time_insights, url_prefix='/real-time-insights')
app.register_blueprint(treatment_recommendations, url_prefix='/treatment-recommendations')
app.register_blueprint(session_preparation, url_prefix='/session-preparation')

print("✅ Comprehensive Patient Insights System integrated successfully!")
'''
    
    # Write integration code to file
    with open('integration_code.py', 'w') as f:
        f.write(integration_code)
    
    print("✅ Integration code created: integration_code.py")
    return True

def create_example_usage():
    """Create example usage code"""
    print("\n📚 Creating example usage...")
    
    example_code = '''
# Example usage of the Comprehensive Patient Insights System

from comprehensive_patient_insights_system import ComprehensivePatientInsightsSystem

# Initialize the system
system = ComprehensivePatientInsightsSystem()

# Get comprehensive insights for a patient
patient_id = 1
insights = system.get_comprehensive_patient_insights(patient_id)

print("Patient Insights:")
print(f"Risk Level: {insights['real_time_summary']['current_status']['risk_level']}")
print(f"Mood State: {insights['real_time_summary']['current_status']['mood_state']}")
print(f"Treatment Urgency: {insights['real_time_summary']['current_status']['treatment_urgency']}")

# Process a patient action
action_result = system.process_patient_action(
    patient_id=patient_id,
    action_type='mood_checkin',
    action_data={'mood_level': 3, 'energy_level': 4}
)

print("\\nAction Analysis:")
print(f"Action Type: {action_result['action_type']}")
print(f"Risk Assessment: {action_result['risk_assessment']}")
print(f"Recommendations: {action_result['recommendations']}")

# Access the dashboard
# Navigate to: /comprehensive-dashboard/1
'''
    
    # Write example code to file
    with open('example_usage.py', 'w') as f:
        f.write(example_code)
    
    print("✅ Example usage created: example_usage.py")
    return True

def create_api_examples():
    """Create API usage examples"""
    print("\n🌐 Creating API examples...")
    
    api_examples = '''
# API Usage Examples

# 1. Get comprehensive patient insights
GET /api/comprehensive-insights/1

# 2. Process patient action
POST /api/process-patient-action/1
Content-Type: application/json

{
    "action_type": "mood_checkin",
    "action_data": {
        "mood_level": 3,
        "energy_level": 4,
        "sleep_quality": 5
    }
}

# 3. Get real-time patient summary
GET /api/patient-summary/1

# 4. Analyze mood check-in
POST /api/analyze-mood-checkin/1
Content-Type: application/json

{
    "mood_level": 3,
    "energy_level": 4,
    "timestamp": "2024-01-15T10:30:00Z"
}

# 5. Get therapy session focus recommendations
GET /api/therapy-session-focus/1

# 6. Get treatment intensity adjustments
GET /api/treatment-intensity/1

# 7. Get clinical decision support
GET /api/clinical-decision-support/1

# 8. Get pre-session brief
GET /api/pre-session-brief/1

# 9. Get session talking points
GET /api/session-talking-points/1

# 10. Get evidence-based session plan
GET /api/evidence-based-session-plan/1

# 11. Access comprehensive dashboard
GET /comprehensive-dashboard/1
'''
    
    # Write API examples to file
    with open('api_examples.md', 'w') as f:
        f.write(api_examples)
    
    print("✅ API examples created: api_examples.md")
    return True

def create_test_data():
    """Create test data for demonstration"""
    print("\n🧪 Creating test data...")
    
    test_data_code = '''
# Test data creation for demonstration

from app_ml_complete import db, Patient, MoodEntry, ExerciseSession, PHQ9Assessment
from datetime import datetime, timedelta
import random

def create_test_patient():
    """Create a test patient with sample data"""
    
    # Create test patient
    patient = Patient(
        user_id=999,
        first_name="Test",
        last_name="Patient",
        age=30,
        gender="Other",
        current_phq9_severity="moderate",
        last_assessment_date=datetime.now(),
        total_assessments=1
    )
    db.session.add(patient)
    db.session.commit()
    
    # Create PHQ-9 assessment
    assessment = PHQ9Assessment(
        patient_id=patient.id,
        q1_score=2, q2_score=2, q3_score=1, q4_score=2,
        q5_score=1, q6_score=2, q7_score=1, q8_score=1, q9_score=0,
        total_score=12,
        severity_level="moderate",
        q9_risk_flag=False,
        crisis_alert_triggered=False,
        assessment_date=datetime.now()
    )
    db.session.add(assessment)
    
    # Create mood entries for the past week
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        for j in range(random.randint(1, 3)):  # 1-3 mood entries per day
            mood_entry = MoodEntry(
                mood_id=f"test_mood_{i}_{j}",
                patient_id=patient.id,
                timestamp=date + timedelta(hours=random.randint(8, 20)),
                mood_emoji="😐",
                intensity_level=random.randint(3, 7),
                energy_level=random.randint(3, 8),
                sleep_quality=random.randint(4, 8),
                social_context="alone",
                weather_mood_metaphor="cloudy",
                color_selection="blue"
            )
            db.session.add(mood_entry)
    
    # Create exercise sessions
    exercise_types = ['cbt', 'mindfulness', 'breathing', 'behavioral_activation']
    for i in range(5):
        session = ExerciseSession(
            session_id=f"test_session_{i}",
            patient_id=patient.id,
            exercise_id=1,  # Assuming exercise with ID 1 exists
            start_time=datetime.now() - timedelta(days=i),
            completion_time=datetime.now() - timedelta(days=i) + timedelta(minutes=15),
            completion_status='completed',
            engagement_score=random.randint(6, 9),
            effectiveness_rating=random.randint(6, 9)
        )
        db.session.add(session)
    
    db.session.commit()
    print(f"✅ Test patient created with ID: {patient.id}")
    return patient.id

if __name__ == "__main__":
    patient_id = create_test_patient()
    print(f"Test patient ID: {patient_id}")
    print("You can now test the system with this patient ID")
'''
    
    # Write test data code to file
    with open('create_test_data.py', 'w') as f:
        f.write(test_data_code)
    
    print("✅ Test data creation script created: create_test_data.py")
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 80)
    print("🎉 Setup Complete! Next Steps:")
    print("=" * 80)
    
    print("\n1. 📋 Review the created files:")
    print("   - integration_code.py - Add this to your main app")
    print("   - example_usage.py - Example Python usage")
    print("   - api_examples.md - API endpoint examples")
    print("   - create_test_data.py - Create test data for demonstration")
    
    print("\n2. 🔧 Integrate into your application:")
    print("   - Copy the code from integration_code.py to your main Flask app")
    print("   - Ensure all required database models exist")
    print("   - Test the integration")
    
    print("\n3. 🧪 Test the system:")
    print("   - Run create_test_data.py to create test data")
    print("   - Access the dashboard: /comprehensive-dashboard/{patient_id}")
    print("   - Test API endpoints with the examples in api_examples.md")
    
    print("\n4. 📚 Learn more:")
    print("   - Read COMPREHENSIVE_PATIENT_INSIGHTS_README.md for full documentation")
    print("   - Review the example usage in example_usage.py")
    print("   - Explore the API endpoints in api_examples.md")
    
    print("\n5. 🚀 Start using:")
    print("   - Access patient insights via API endpoints")
    print("   - Use the comprehensive dashboard for real-time monitoring")
    print("   - Process patient actions for immediate insights")
    print("   - Generate treatment recommendations and session preparation data")
    
    print("\n" + "=" * 80)
    print("🏥 Your Comprehensive Patient Insights System is ready!")
    print("=" * 80)

def main():
    """Main setup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed: Missing dependencies")
        return False
    
    # Check database models
    if not check_database_models():
        print("\n❌ Setup failed: Missing database models")
        return False
    
    # Create integration files
    create_integration_code()
    create_example_usage()
    create_api_examples()
    create_test_data()
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
