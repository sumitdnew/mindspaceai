# train_crisis_detector.py
from crisis_detector_xgboost import XGBoostCrisisDetector
from app_ml_complete import app, db, Patient, CrisisAlert, PHQ9Assessment, MoodEntry, ExerciseSession
from datetime import datetime, timedelta
import random

def create_training_data():
    """Create training data from existing database"""
    print("📊 Creating training data...")
    
    # Get all patients
    patients = Patient.query.all()
    training_data = []
    labels = []
    
    for patient in patients:
        # Get patient features
        patient_features = get_patient_features(patient.id)
        
        # Check if patient has crisis alerts (positive examples)
        crisis_alerts = CrisisAlert.query.filter_by(patient_id=patient.id).count()
        has_crisis = 1 if crisis_alerts > 0 else 0
        
        training_data.append(patient_features)
        labels.append(has_crisis)
    
    print(f"✅ Created training data: {len(training_data)} patients, {sum(labels)} with crises")
    return training_data, labels

def get_patient_features(patient_id):
    """Extract features for a specific patient"""
    # Get recent PHQ-9 assessments
    recent_phq9 = PHQ9Assessment.query.filter_by(patient_id=patient_id).order_by(PHQ9Assessment.assessment_date.desc()).first()
    
    # Get recent mood entries
    recent_mood = MoodEntry.query.filter_by(patient_id=patient_id).order_by(MoodEntry.timestamp.desc()).first()
    
    # Get recent exercise sessions
    recent_exercise = ExerciseSession.query.filter_by(patient_id=patient_id).order_by(ExerciseSession.completion_time.desc()).first()
    
    # Get crisis history
    crisis_count = CrisisAlert.query.filter_by(patient_id=patient_id).count()
    
    # Calculate features
    features = {
        'phq9_total_score': recent_phq9.total_score if recent_phq9 else 0,
        'q9_score': recent_phq9.q9_score if recent_phq9 else 0,
        'phq9_severity_level': recent_phq9.severity_level if recent_phq9 else 'minimal',
        'phq9_trend': 0,  # Placeholder - would need historical data
        'mood_intensity': recent_mood.intensity_level if recent_mood else 5,
        'mood_trend': 0,  # Placeholder
        'exercise_completion_rate': 0.8 if recent_exercise else 0.0,
        'days_since_last_session': 0 if recent_exercise else 30,
        'crisis_keyword_count': 0,  # Placeholder - would need text analysis
        'previous_crisis_count': crisis_count,
        'assessment_frequency': 7,  # Placeholder
        'treatment_duration': 90,  # Placeholder
        'age': 30,  # Placeholder
        'isolation_level': 0,  # Placeholder
        'social_support': 1,  # Placeholder
        'medication_adherence': 0.8,  # Placeholder
        'therapy_attendance': 0.8,  # Placeholder
        'provider_concern': 0,  # Placeholder
        'clinical_observations': 0  # Placeholder
    }
    
    return features

def train_crisis_detector():
    """Train the crisis detection model"""
    print("🚀 Starting crisis detector training...")
    
    # Create detector
    detector = XGBoostCrisisDetector()
    
    # Try to load existing model first
    if detector.load_model():
        print("✅ Using existing trained model")
        return detector
    
    # Create training data within app context
    with app.app_context():
        training_data, labels = create_training_data()
    
    if len(training_data) < 10:
        print("❌ Not enough training data. Need at least 10 patients.")
        return None
    
    # Train model
    accuracy = detector.train(training_data, labels)
    
    if accuracy > 0.7:
        print(f"✅ Model trained successfully with {accuracy:.3f} accuracy")
        return detector
    else:
        print(f"⚠️ Model accuracy is low ({accuracy:.3f}). Consider more training data.")
        return detector

if __name__ == "__main__":
    # This will run when you execute the script
    detector = train_crisis_detector()
    if detector:
        print("🎉 Crisis detector ready!")
    else:
        print("❌ Failed to train crisis detector")