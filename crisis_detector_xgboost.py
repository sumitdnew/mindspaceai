# crisis_detector_xgboost.py
import xgboost as xgb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class XGBoostCrisisDetector:
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        self.is_trained = False
        self.feature_names = []
        self.model_path = 'crisis_detector_model.pkl'
    
    def prepare_features(self, patient_data):
        """Convert patient data to features XGBoost can use"""
        # Convert severity level to numeric
        severity_mapping = {
            'minimal': 0,
            'mild': 1,
            'moderate': 2,
            'moderately_severe': 3,
            'severe': 4
        }
        
        phq9_severity = patient_data.get('phq9_severity_level', 'minimal')
        phq9_severity_numeric = severity_mapping.get(phq9_severity, 0)
        
        features = {
            # PHQ-9 related features (all numeric)
            'phq9_total': patient_data.get('phq9_total_score', 0),
            'q9_score': patient_data.get('q9_score', 0),
            'phq9_severity': phq9_severity_numeric,  # Converted to numeric
            'phq9_trend': patient_data.get('phq9_trend', 0),
            
            # Mood and engagement features
            'mood_intensity': patient_data.get('mood_intensity', 5),
            'mood_low': 1 if patient_data.get('mood_intensity', 5) <= 3 else 0,
            'mood_declining': 1 if patient_data.get('mood_trend', 0) < 0 else 0,
            'exercise_completion_rate': patient_data.get('exercise_completion_rate', 1.0),
            'exercise_drop': 1 if patient_data.get('exercise_completion_rate', 1) < 0.5 else 0,
            'days_since_last_session': patient_data.get('days_since_last_session', 0),
            'days_inactive': 1 if patient_data.get('days_since_last_session', 0) > 7 else 0,
            
            # Crisis indicators
            'crisis_keyword_count': patient_data.get('crisis_keyword_count', 0),
            'crisis_words_present': 1 if patient_data.get('crisis_keyword_count', 0) > 0 else 0,
            'previous_crisis_count': patient_data.get('previous_crisis_count', 0),
            'has_crisis_history': 1 if patient_data.get('previous_crisis_count', 0) > 0 else 0,
            
            # Temporal features
            'assessment_frequency': patient_data.get('assessment_frequency', 7),
            'assessment_gap': 1 if patient_data.get('assessment_frequency', 7) > 14 else 0,
            'treatment_duration': patient_data.get('treatment_duration', 0),
            'new_patient': 1 if patient_data.get('treatment_duration', 0) < 30 else 0,
            
            # Demographic and context
            'age': patient_data.get('age', 30),
            'high_risk_age': 1 if 18 <= patient_data.get('age', 30) <= 25 else 0,
            'isolation_level': patient_data.get('isolation_level', 0),
            'social_support': patient_data.get('social_support', 1),
            
            # Additional risk factors
            'medication_adherence': patient_data.get('medication_adherence', 1.0),
            'therapy_attendance': patient_data.get('therapy_attendance', 1.0),
            'provider_concern': patient_data.get('provider_concern', 0),
            'clinical_observations': patient_data.get('clinical_observations', 0)
        }
        
        return pd.DataFrame([features])
    
    def train(self, training_data, labels):
        """Train the XGBoost model"""
        print("🚀 Training XGBoost Crisis Detector...")
        
        # Prepare features
        X = pd.concat([self.prepare_features(data) for data in training_data], ignore_index=True)
        y = np.array(labels)
        
        # Ensure all columns are numeric
        X = X.astype(float)
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Split data for validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model (updated for XGBoost 3.0+)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        # Evaluate performance
        y_pred = self.model.predict(X_val)
        accuracy = accuracy_score(y_val, y_pred)
        
        print(f"✅ Training complete! Validation accuracy: {accuracy:.3f}")
        print(f"📊 Feature importance:")
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {feature}: {importance:.3f}")
        
        self.is_trained = True
        
        # Save model
        self.save_model()
        
        return accuracy
    
    def predict_crisis_risk(self, patient_data):
        """Predict crisis risk for a patient"""
        if not self.is_trained:
            return {
                'crisis_risk': 0.0,
                'risk_level': 'UNKNOWN',
                'confidence': 'LOW',
                'error': 'Model not trained'
            }
        
        try:
            features = self.prepare_features(patient_data)
            # Ensure features are numeric
            features = features.astype(float)
            
            risk_probability = self.model.predict_proba(features)[0][1]
            
            # Determine risk level
            if risk_probability >= 0.8:
                risk_level = 'CRITICAL'
            elif risk_probability >= 0.6:
                risk_level = 'HIGH'
            elif risk_probability >= 0.4:
                risk_level = 'MEDIUM'
            elif risk_probability >= 0.2:
                risk_level = 'LOW'
            else:
                risk_level = 'MINIMAL'
            
            # Determine confidence
            if risk_probability >= 0.9 or risk_probability <= 0.1:
                confidence = 'HIGH'
            elif risk_probability >= 0.7 or risk_probability <= 0.3:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'
            
            return {
                'crisis_risk': float(risk_probability),
                'risk_level': risk_level,
                'confidence': confidence,
                'feature_contributions': self.get_feature_contributions(features),
                'recommendations': self.generate_recommendations(risk_level, risk_probability)
            }
            
        except Exception as e:
            return {
                'crisis_risk': 0.0,
                'risk_level': 'ERROR',
                'confidence': 'LOW',
                'error': str(e)
            }
    
    def get_feature_contributions(self, features):
        """Get feature importance for this specific prediction"""
        if not self.is_trained:
            return {}
        
        # Get feature importance
        importance = self.model.feature_importances_
        contributions = dict(zip(self.feature_names, importance))
        
        # Sort by importance
        return dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:5])
    
    def generate_recommendations(self, risk_level, risk_probability):
        """Generate recommendations based on risk level"""
        recommendations = []
        
        if risk_level in ['CRITICAL', 'HIGH']:
            recommendations.extend([
                "Immediate provider contact required",
                "Consider crisis intervention protocols",
                "Monitor patient closely",
                "Review safety planning"
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                "Schedule follow-up assessment",
                "Increase monitoring frequency",
                "Review treatment plan",
                "Consider additional support"
            ])
        elif risk_level == 'LOW':
            recommendations.extend([
                "Continue current treatment",
                "Regular monitoring",
                "Watch for changes"
            ])
        else:
            recommendations.extend([
                "Routine care",
                "Standard monitoring"
            ])
        
        return recommendations
    
    def save_model(self):
        """Save trained model to file"""
        if self.is_trained:
            joblib.dump({
                'model': self.model,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained
            }, self.model_path)
            print(f"💾 Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model from file"""
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.model = data['model']
                self.feature_names = data['feature_names']
                self.is_trained = data['is_trained']
                print(f" Model loaded from {self.model_path}")
                return True
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                return False
        return False