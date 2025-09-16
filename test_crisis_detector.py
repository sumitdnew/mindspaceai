# test_crisis_detector.py
from crisis_detector_xgboost import XGBoostCrisisDetector
from train_crisis_detector import train_crisis_detector

def test_crisis_detector():
    """Test the crisis detection system"""
    print(" Testing crisis detector...")
    
    # Train or load model
    detector = train_crisis_detector()
    
    if not detector:
        print("❌ No detector available")
        return
    
    # Test with sample data
    test_patient = {
        'phq9_total_score': 18,
        'q9_score': 2,
        'mood_intensity': 2,
        'exercise_completion_rate': 0.3,
        'days_since_last_session': 10,
        'crisis_keyword_count': 3,
        'previous_crisis_count': 1,
        'age': 22,
        'treatment_duration': 45
    }
    
    # Make prediction
    prediction = detector.predict_crisis_risk(test_patient)
    
    print(f" Test prediction:")
    print(f"   Crisis Risk: {prediction['crisis_risk']:.3f}")
    print(f"   Risk Level: {prediction['risk_level']}")
    print(f"   Confidence: {prediction['confidence']}")
    print(f"   Recommendations: {prediction['recommendations']}")

if __name__ == "__main__":
    test_crisis_detector()