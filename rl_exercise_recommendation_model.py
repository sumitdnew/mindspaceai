#!/usr/bin/env python3
"""
Reinforcement Learning Exercise Recommendation Model
Trains a model to recommend exercises based on provider feedback
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import json
import logging
from datetime import datetime, timedelta
import pickle
import joblib

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb

# Deep Learning (optional)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available. Deep learning features disabled.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExerciseRecommendationDataset(Dataset):
    """PyTorch Dataset for exercise recommendations"""
    
    def __init__(self, features, labels, rewards):
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels)
        self.rewards = torch.FloatTensor(rewards)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx], self.rewards[idx]

class ExerciseRecommendationNN(nn.Module):
    """Neural Network for exercise recommendations"""
    
    def __init__(self, input_size, hidden_sizes, output_size, dropout_rate=0.3):
        super(ExerciseRecommendationNN, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
                nn.BatchNorm1d(hidden_size)
            ])
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, output_size))
        layers.append(nn.Softmax(dim=1))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)

class RLExerciseRecommendationModel:
    """Reinforcement Learning model for exercise recommendations"""
    
    def __init__(self, model_type='xgboost', use_deep_learning=False):
        self.model_type = model_type
        self.use_deep_learning = use_deep_learning
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_importance = {}
        self.training_history = []
        
        # Exercise types
        self.exercise_types = [
            'mood_check_in', 'cbt_thought_record', 'mindfulness_exercise',
            'behavioral_activation', 'crisis_monitoring', 'breathing_grounding'
        ]
        
        # Feature columns
        self.feature_columns = [
            'patient_age', 'patient_gender', 'phq9_total_score', 'severity_level',
            'q9_risk_flag', 'mood_trend_avg', 'mood_trend_slope', 'engagement_score',
            'completion_rate', 'days_since_assessment', 'time_of_day', 'day_of_week',
            'previous_exercise_success', 'crisis_history', 'medication_status'
        ]
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the ML model"""
        if self.use_deep_learning and TORCH_AVAILABLE:
            self.model = ExerciseRecommendationNN(
                input_size=len(self.feature_columns),
                hidden_sizes=[128, 64, 32],
                output_size=len(self.exercise_types)
            )
        elif self.model_type == 'xgboost':
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        elif self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def prepare_training_data(self, feedback_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data from provider feedback"""
        try:
            features = []
            labels = []
            rewards = []
            
            for sample in feedback_data:
                # Extract features
                feature_vector = self._extract_features(sample)
                if feature_vector is None:
                    continue
                
                # Extract label (exercise type)
                exercise_type = sample.get('recommended_exercise')
                if exercise_type not in self.exercise_types:
                    continue
                
                label = self.exercise_types.index(exercise_type)
                
                # Extract reward signal
                reward = sample.get('reward_signal', 0.0)
                
                features.append(feature_vector)
                labels.append(label)
                rewards.append(reward)
            
            if not features:
                logger.warning("No valid training samples found")
                return np.array([]), np.array([]), np.array([])
            
            features = np.array(features)
            labels = np.array(labels)
            rewards = np.array(rewards)
            
            logger.info(f"Prepared {len(features)} training samples")
            return features, labels, rewards
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return np.array([]), np.array([]), np.array([])
    
    def _extract_features(self, sample: Dict) -> Optional[np.ndarray]:
        """Extract features from a training sample"""
        try:
            patient_context = sample.get('patient_context', {})
            assessment_data = patient_context.get('assessment_data', {})
            exercise_history = patient_context.get('exercise_history', [])
            mood_trend = patient_context.get('mood_trend', [])
            
            # Basic patient features
            age = patient_context.get('age', 35)
            gender = 1 if patient_context.get('gender') == 'Male' else 0
            
            # PHQ-9 features
            phq9_score = assessment_data.get('total_score', 0)
            severity_level = self._encode_severity(assessment_data.get('severity_level', 'minimal'))
            q9_risk = 1 if assessment_data.get('q9_risk', False) else 0
            
            # Mood trend features
            mood_avg = np.mean(mood_trend) if mood_trend else 5.0
            mood_slope = np.polyfit(range(len(mood_trend)), mood_trend, 1)[0] if len(mood_trend) > 1 else 0.0
            
            # Engagement features
            engagement_scores = [ex.get('engagement_score', 5) for ex in exercise_history if ex.get('engagement_score')]
            engagement_avg = np.mean(engagement_scores) if engagement_scores else 5.0
            
            # Completion rate
            completed = sum(1 for ex in exercise_history if ex.get('completion_status') == 'completed')
            completion_rate = completed / len(exercise_history) if exercise_history else 0.5
            
            # Time features
            timestamp = datetime.fromisoformat(sample.get('timestamp', datetime.now().isoformat()))
            time_of_day = timestamp.hour / 24.0  # Normalize to 0-1
            day_of_week = timestamp.weekday() / 7.0  # Normalize to 0-1
            
            # Days since assessment
            assessment_date = assessment_data.get('assessment_date')
            if assessment_date:
                assessment_dt = datetime.fromisoformat(assessment_date)
                days_since = (timestamp - assessment_dt).days
            else:
                days_since = 0
            
            # Previous exercise success
            recent_exercises = exercise_history[:5]  # Last 5 exercises
            success_rate = sum(1 for ex in recent_exercises if ex.get('completion_status') == 'completed') / len(recent_exercises) if recent_exercises else 0.5
            
            # Crisis history
            crisis_history = 1 if any(ex.get('type') == 'crisis_monitoring' for ex in exercise_history) else 0
            
            # Medication status (placeholder - would come from patient data)
            medication_status = 0  # 0 = no medication, 1 = on medication
            
            feature_vector = np.array([
                age, gender, phq9_score, severity_level, q9_risk,
                mood_avg, mood_slope, engagement_avg, completion_rate,
                days_since, time_of_day, day_of_week, success_rate,
                crisis_history, medication_status
            ])
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return None
    
    def _encode_severity(self, severity: str) -> int:
        """Encode severity level to numeric"""
        severity_map = {
            'minimal': 0,
            'mild': 1,
            'moderate': 2,
            'moderately_severe': 3,
            'severe': 4
        }
        return severity_map.get(severity, 0)
    
    def train(self, feedback_data: List[Dict], validation_split=0.2) -> Dict:
        """Train the RL model on provider feedback data"""
        try:
            logger.info("Starting RL model training...")
            
            # Prepare training data
            features, labels, rewards = self.prepare_training_data(feedback_data)
            
            if len(features) == 0:
                return {'error': 'No valid training data available'}
            
            # Split data
            X_train, X_val, y_train, y_val, r_train, r_val = train_test_split(
                features, labels, rewards, test_size=validation_split, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
            
            # Train model
            if self.use_deep_learning and TORCH_AVAILABLE:
                training_results = self._train_neural_network(X_train_scaled, y_train, r_train, X_val_scaled, y_val, r_val)
            else:
                training_results = self._train_sklearn_model(X_train_scaled, y_train, r_train, X_val_scaled, y_val, r_val)
            
            # Calculate feature importance
            self._calculate_feature_importance()
            
            # Store training history
            self.training_history.append({
                'timestamp': datetime.now().isoformat(),
                'training_samples': len(features),
                'validation_samples': len(X_val),
                'results': training_results
            })
            
            logger.info("RL model training completed successfully")
            return training_results
            
        except Exception as e:
            logger.error(f"Error training RL model: {str(e)}")
            return {'error': f'Training failed: {str(e)}'}
    
    def _train_sklearn_model(self, X_train, y_train, r_train, X_val, y_val, r_val) -> Dict:
        """Train sklearn-based model"""
        try:
            # Train model
            self.model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self.model.predict(X_val)
            y_proba = self.model.predict_proba(X_val)
            
            # Calculate metrics
            accuracy = accuracy_score(y_val, y_pred)
            
            # Calculate reward-weighted accuracy
            reward_weights = r_val / np.sum(r_val) if np.sum(r_val) > 0 else np.ones_like(r_val) / len(r_val)
            weighted_accuracy = np.sum((y_pred == y_val) * reward_weights)
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
            
            results = {
                'model_type': self.model_type,
                'accuracy': accuracy,
                'weighted_accuracy': weighted_accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'classification_report': classification_report(y_val, y_pred, output_dict=True),
                'confusion_matrix': confusion_matrix(y_val, y_pred).tolist()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error training sklearn model: {str(e)}")
            return {'error': f'Sklearn training failed: {str(e)}'}
    
    def _train_neural_network(self, X_train, y_train, r_train, X_val, y_val, r_val) -> Dict:
        """Train neural network model"""
        try:
            if not TORCH_AVAILABLE:
                raise ImportError("PyTorch not available")
            
            # Create datasets
            train_dataset = ExerciseRecommendationDataset(X_train, y_train, r_train)
            val_dataset = ExerciseRecommendationDataset(X_val, y_val, r_val)
            
            # Create data loaders
            train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
            
            # Initialize model
            self.model = ExerciseRecommendationNN(
                input_size=X_train.shape[1],
                hidden_sizes=[128, 64, 32],
                output_size=len(self.exercise_types)
            )
            
            # Loss and optimizer
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            
            # Training loop
            num_epochs = 100
            train_losses = []
            val_accuracies = []
            
            for epoch in range(num_epochs):
                # Training
                self.model.train()
                train_loss = 0.0
                
                for batch_features, batch_labels, batch_rewards in train_loader:
                    optimizer.zero_grad()
                    outputs = self.model(batch_features)
                    loss = criterion(outputs, batch_labels)
                    loss.backward()
                    optimizer.step()
                    train_loss += loss.item()
                
                train_losses.append(train_loss / len(train_loader))
                
                # Validation
                self.model.eval()
                correct = 0
                total = 0
                
                with torch.no_grad():
                    for batch_features, batch_labels, batch_rewards in val_loader:
                        outputs = self.model(batch_features)
                        _, predicted = torch.max(outputs.data, 1)
                        total += batch_labels.size(0)
                        correct += (predicted == batch_labels).sum().item()
                
                val_accuracy = correct / total
                val_accuracies.append(val_accuracy)
                
                if epoch % 10 == 0:
                    logger.info(f"Epoch {epoch}: Train Loss: {train_losses[-1]:.4f}, Val Accuracy: {val_accuracy:.4f}")
            
            results = {
                'model_type': 'neural_network',
                'accuracy': val_accuracies[-1],
                'final_train_loss': train_losses[-1],
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'epochs': num_epochs,
                'train_losses': train_losses,
                'val_accuracies': val_accuracies
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error training neural network: {str(e)}")
            return {'error': f'Neural network training failed: {str(e)}'}
    
    def predict(self, patient_context: Dict, exercise_context: Dict = None) -> Dict:
        """Make exercise recommendations for a patient"""
        try:
            if self.model is None:
                return {'error': 'Model not trained'}
            
            # Extract features
            sample = {
                'patient_context': patient_context,
                'exercise_context': exercise_context,
                'timestamp': datetime.now().isoformat()
            }
            
            features = self._extract_features(sample)
            if features is None:
                return {'error': 'Could not extract features'}
            
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Make prediction
            if self.use_deep_learning and TORCH_AVAILABLE:
                self.model.eval()
                with torch.no_grad():
                    features_tensor = torch.FloatTensor(features_scaled)
                    outputs = self.model(features_tensor)
                    probabilities = outputs.numpy()[0]
                    predicted_exercise_idx = np.argmax(probabilities)
            else:
                probabilities = self.model.predict_proba(features_scaled)[0]
                predicted_exercise_idx = np.argmax(probabilities)
            
            # Get top recommendations
            exercise_scores = list(zip(self.exercise_types, probabilities))
            exercise_scores.sort(key=lambda x: x[1], reverse=True)
            
            recommendations = []
            for exercise_type, score in exercise_scores[:3]:  # Top 3 recommendations
                recommendations.append({
                    'exercise_type': exercise_type,
                    'confidence_score': float(score),
                    'recommendation_reason': self._get_recommendation_reason(exercise_type, features)
                })
            
            return {
                'recommended_exercise': self.exercise_types[predicted_exercise_idx],
                'confidence_score': float(probabilities[predicted_exercise_idx]),
                'all_recommendations': recommendations,
                'feature_importance': self.feature_importance,
                'model_type': self.model_type
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return {'error': f'Prediction failed: {str(e)}'}
    
    def _get_recommendation_reason(self, exercise_type: str, features: np.ndarray) -> str:
        """Get human-readable reason for recommendation"""
        reasons = {
            'mood_check_in': 'Quick assessment for mood monitoring',
            'cbt_thought_record': 'Cognitive restructuring for negative thoughts',
            'mindfulness_exercise': 'Stress reduction and present moment awareness',
            'behavioral_activation': 'Activity planning to improve mood',
            'crisis_monitoring': 'Safety assessment and crisis prevention',
            'breathing_grounding': 'Immediate crisis intervention technique'
        }
        
        base_reason = reasons.get(exercise_type, 'General mental health exercise')
        
        # Add context-specific reasons
        if features[4] > 0:  # Q9 risk flag
            base_reason += ' (High risk patient - safety focus)'
        elif features[3] > 2:  # High severity
            base_reason += ' (High severity - intensive intervention)'
        elif features[7] < 5:  # Low engagement
            base_reason += ' (Low engagement - simplified approach)'
        
        return base_reason
    
    def _calculate_feature_importance(self):
        """Calculate feature importance"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = dict(zip(self.feature_columns, self.model.feature_importances_))
            elif hasattr(self.model, 'coef_'):
                self.feature_importance = dict(zip(self.feature_columns, np.abs(self.model.coef_[0])))
            else:
                # For neural networks, use gradient-based importance
                self.feature_importance = {col: 1.0 / len(self.feature_columns) for col in self.feature_columns}
        except Exception as e:
            logger.error(f"Error calculating feature importance: {str(e)}")
            self.feature_importance = {col: 1.0 / len(self.feature_columns) for col in self.feature_columns}
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_importance': self.feature_importance,
                'training_history': self.training_history,
                'model_type': self.model_type,
                'use_deep_learning': self.use_deep_learning,
                'exercise_types': self.exercise_types,
                'feature_columns': self.feature_columns
            }
            
            if self.use_deep_learning and TORCH_AVAILABLE:
                torch.save(model_data, filepath)
            else:
                joblib.dump(model_data, filepath)
            
            logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        try:
            if self.use_deep_learning and TORCH_AVAILABLE:
                model_data = torch.load(filepath)
            else:
                model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_importance = model_data['feature_importance']
            self.training_history = model_data['training_history']
            self.model_type = model_data['model_type']
            self.use_deep_learning = model_data['use_deep_learning']
            self.exercise_types = model_data['exercise_types']
            self.feature_columns = model_data['feature_columns']
            
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
    
    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        return {
            'model_type': self.model_type,
            'use_deep_learning': self.use_deep_learning,
            'is_trained': self.model is not None,
            'training_samples': len(self.training_history),
            'feature_importance': self.feature_importance,
            'exercise_types': self.exercise_types,
            'last_training': self.training_history[-1]['timestamp'] if self.training_history else None
        }

# Initialize the RL model
rl_exercise_model = RLExerciseRecommendationModel(model_type='xgboost', use_deep_learning=False)
