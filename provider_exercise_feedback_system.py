#!/usr/bin/env python3
"""
Provider Exercise Feedback System
Enables providers to review, approve, and modify exercise recommendations for patients
Collects feedback data for reinforcement learning model training
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
from sqlalchemy import and_, func, desc
from sqlalchemy.orm import joinedload

# Models will be imported dynamically to avoid circular imports

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProviderExerciseFeedbackService:
    """Provider feedback system for exercise recommendations"""
    
    def __init__(self):
        # Models will be imported dynamically
        self._models = None
        
        # Initialize feedback types
        self.feedback_types = {
            'approve': 'approved',
            'reject': 'rejected', 
            'modify': 'modified',
            'add': 'added',
            'remove': 'removed'
        }
        
        self.feedback_categories = {
            'clinical_appropriateness': 'Clinical appropriateness for patient condition',
            'safety_concerns': 'Safety concerns or contraindications',
            'patient_preference': 'Patient preference or history',
            'timing_issues': 'Timing or scheduling concerns',
            'effectiveness': 'Expected effectiveness based on evidence',
            'other': 'Other clinical considerations'
        }
    
    def _get_models(self):
        """Get database models dynamically to avoid circular imports"""
        if self._models is None:
            import app_ml_complete
            self._models = {
                'db': app_ml_complete.db,
                'Patient': app_ml_complete.Patient,
                'PHQ9Assessment': app_ml_complete.PHQ9Assessment,
                'Exercise': app_ml_complete.Exercise,
                'ExerciseSession': app_ml_complete.ExerciseSession,
                'CrisisAlert': app_ml_complete.CrisisAlert,
                'RecommendationResult': app_ml_complete.RecommendationResult,
                'MoodEntry': app_ml_complete.MoodEntry,
                'User': app_ml_complete.User,
                'ProviderExerciseFeedback': app_ml_complete.ProviderExerciseFeedback
            }
        return self._models

    def get_patient_exercise_recommendations(self, patient_id: int, provider_id: int) -> Dict:
        """Get current exercise recommendations for a patient that need provider review"""
        try:
            models = self._get_models()
            Patient = models['Patient']
            PHQ9Assessment = models['PHQ9Assessment']
            
            # Get patient and latest assessment
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                .order_by(desc(PHQ9Assessment.assessment_date)).first()
            
            if not latest_assessment:
                return {'error': 'No PHQ-9 assessment found for patient'}
            
            # Get current exercise recommendations (from rule-based system)
            from phq9_exercise_integration import phq9_exercise_integration
            recommendations = phq9_exercise_integration.generate_adaptive_recommendations(
                patient_id, latest_assessment.id
            )
            
            if 'error' in recommendations:
                return {'error': f'Failed to generate recommendations: {recommendations["error"]}'}
            
            # Get exercise history and feedback
            exercise_history = self._get_exercise_history(patient_id)
            previous_feedback = self._get_previous_feedback(patient_id, provider_id)
            
            # Format recommendations for provider review
            formatted_recommendations = self._format_recommendations_for_provider(
                recommendations, patient, latest_assessment
            )
            
            return {
                'patient_info': {
                    'id': patient.id,
                    'name': f"{patient.first_name} {patient.last_name}",
                    'age': patient.age,
                    'current_severity': latest_assessment.severity_level,
                    'total_score': latest_assessment.total_score,
                    'q9_risk': latest_assessment.q9_risk_flag,
                    'last_assessment': latest_assessment.assessment_date.isoformat()
                },
                'recommendations': formatted_recommendations,
                'exercise_history': exercise_history,
                'previous_feedback': previous_feedback,
                'available_exercises': self._get_available_exercises(),
                'feedback_categories': self.feedback_categories
            }
            
        except Exception as e:
            logger.error(f"Error getting patient exercise recommendations: {str(e)}")
            return {'error': f'Failed to get recommendations: {str(e)}'}

    def submit_provider_feedback(self, patient_id: int, provider_id: int, 
                               feedback_data: Dict) -> Dict:
        """Submit provider feedback on exercise recommendations"""
        try:
            # Validate feedback data
            if not self._validate_feedback_data(feedback_data):
                return {'error': 'Invalid feedback data'}
            
            # Create feedback record
            feedback_record = ProviderExerciseFeedback(
                patient_id=patient_id,
                provider_id=provider_id,
                recommendation_id=feedback_data.get('recommendation_id'),
                exercise_type=feedback_data.get('exercise_type'),
                action=feedback_data.get('action'),  # approve, reject, modify, add, remove
                feedback_category=feedback_data.get('category'),
                feedback_text=feedback_data.get('feedback_text', ''),
                modified_recommendations=json.dumps(feedback_data.get('modified_recommendations', {})),
                clinical_rationale=feedback_data.get('clinical_rationale', ''),
                submitted_at=datetime.now()
            )
            
            db.session.add(feedback_record)
            
            # If approved, create the actual exercise session/recommendation
            if feedback_data.get('action') == 'approve':
                self._create_approved_exercise_session(patient_id, feedback_data)
            
            # If modified, create modified recommendation
            elif feedback_data.get('action') == 'modify':
                self._create_modified_recommendation(patient_id, feedback_data)
            
            # If new exercise added, create new recommendation
            elif feedback_data.get('action') == 'add':
                self._create_new_exercise_recommendation(patient_id, feedback_data)
            
            db.session.commit()
            
            # Update RL training data
            self._update_rl_training_data(patient_id, provider_id, feedback_data)
            
            return {
                'success': True,
                'feedback_id': feedback_record.id,
                'message': 'Feedback submitted successfully',
                'next_recommendations': self._get_next_recommendations(patient_id)
            }
            
        except Exception as e:
            logger.error(f"Error submitting provider feedback: {str(e)}")
            db.session.rollback()
            return {'error': f'Failed to submit feedback: {str(e)}'}

    def get_provider_dashboard(self, provider_id: int) -> Dict:
        """Get comprehensive provider dashboard for exercise management"""
        try:
            # Get provider's patients
            patients = Patient.query.join(User).filter(User.role == 'patient').all()
            
            dashboard_data = {
                'provider_id': provider_id,
                'total_patients': len(patients),
                'pending_reviews': 0,
                'recent_feedback': [],
                'patient_summaries': [],
                'feedback_analytics': {},
                'rl_training_progress': {}
            }
            
            # Get pending reviews
            for patient in patients:
                pending_reviews = self._get_pending_reviews(patient.id, provider_id)
                dashboard_data['pending_reviews'] += len(pending_reviews)
                
                # Get patient summary
                patient_summary = self._get_patient_summary(patient.id, provider_id)
                dashboard_data['patient_summaries'].append(patient_summary)
            
            # Get recent feedback
            dashboard_data['recent_feedback'] = self._get_recent_feedback(provider_id)
            
            # Get feedback analytics
            dashboard_data['feedback_analytics'] = self._get_feedback_analytics(provider_id)
            
            # Get RL training progress
            dashboard_data['rl_training_progress'] = self._get_rl_training_progress(provider_id)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting provider dashboard: {str(e)}")
            return {'error': f'Failed to get dashboard: {str(e)}'}

    def get_rl_training_data(self, provider_id: int = None, limit: int = 1000) -> Dict:
        """Get training data for reinforcement learning model"""
        try:
            # Get feedback data
            query = ProviderExerciseFeedback.query
            
            if provider_id:
                query = query.filter_by(provider_id=provider_id)
            
            feedback_records = query.order_by(desc(ProviderExerciseFeedback.submitted_at))\
                .limit(limit).all()
            
            training_data = []
            
            for record in feedback_records:
                # Get patient context at time of feedback
                patient_context = self._get_patient_context(record.patient_id, record.submitted_at)
                
                # Get exercise recommendation context
                exercise_context = self._get_exercise_context(record.exercise_type)
                
                # Create training sample
                training_sample = {
                    'patient_id': record.patient_id,
                    'provider_id': record.provider_id,
                    'timestamp': record.submitted_at.isoformat(),
                    'patient_context': patient_context,
                    'exercise_context': exercise_context,
                    'recommended_exercise': record.exercise_type,
                    'provider_action': record.action,
                    'feedback_category': record.feedback_category,
                    'clinical_rationale': record.clinical_rationale,
                    'reward_signal': self._calculate_reward_signal(record),
                    'outcome_data': self._get_outcome_data(record.patient_id, record.submitted_at)
                }
                
                training_data.append(training_sample)
            
            return {
                'training_data': training_data,
                'total_samples': len(training_data),
                'data_quality_metrics': self._calculate_data_quality_metrics(training_data),
                'feature_importance': self._calculate_feature_importance(training_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting RL training data: {str(e)}")
            return {'error': f'Failed to get training data: {str(e)}'}

    def _format_recommendations_for_provider(self, recommendations: Dict, 
                                           patient: Patient, assessment: PHQ9Assessment) -> Dict:
        """Format exercise recommendations for provider review"""
        formatted = {
            'severity_based_recommendations': recommendations.get('exercise_recommendations', {}),
            'schedule_plan': recommendations.get('schedule_plan', {}),
            'monitoring_plan': recommendations.get('monitoring_plan', {}),
            'safety_protocols': recommendations.get('safety_protocols', {}),
            'recommendation_id': f"rec_{patient.id}_{assessment.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'rule_based_source': True
        }
        
        return formatted

    def _get_exercise_history(self, patient_id: int) -> List[Dict]:
        """Get patient's exercise history"""
        try:
            sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).limit(20).all()
            
            history = []
            for session in sessions:
                history.append({
                    'exercise_type': session.exercise.type,
                    'completion_status': session.completion_status,
                    'engagement_score': session.engagement_score,
                    'effectiveness_rating': session.effectiveness_rating,
                    'date': session.start_time.isoformat(),
                    'duration': (session.completion_time - session.start_time).total_seconds() / 60 if session.completion_time else None
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting exercise history: {str(e)}")
            return []

    def _get_previous_feedback(self, patient_id: int, provider_id: int) -> List[Dict]:
        """Get previous provider feedback for this patient"""
        try:
            feedback_records = ProviderExerciseFeedback.query.filter_by(
                patient_id=patient_id, provider_id=provider_id
            ).order_by(desc(ProviderExerciseFeedback.submitted_at)).limit(10).all()
            
            feedback = []
            for record in feedback_records:
                feedback.append({
                    'exercise_type': record.exercise_type,
                    'action': record.action,
                    'category': record.feedback_category,
                    'rationale': record.clinical_rationale,
                    'date': record.submitted_at.isoformat(),
                    'modified_recommendations': json.loads(record.modified_recommendations) if record.modified_recommendations else {}
                })
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error getting previous feedback: {str(e)}")
            return []

    def _get_available_exercises(self) -> List[Dict]:
        """Get all available exercises for provider to choose from"""
        try:
            exercises = Exercise.query.all()
            
            available = []
            for exercise in exercises:
                available.append({
                    'id': exercise.id,
                    'type': exercise.type,
                    'name': exercise.name,
                    'difficulty_level': exercise.difficulty_level,
                    'estimated_duration': exercise.estimated_duration,
                    'clinical_focus_areas': exercise.clinical_focus_areas,
                    'description': exercise.description
                })
            
            return available
            
        except Exception as e:
            logger.error(f"Error getting available exercises: {str(e)}")
            return []

    def _validate_feedback_data(self, feedback_data: Dict) -> bool:
        """Validate provider feedback data"""
        required_fields = ['action', 'exercise_type']
        valid_actions = ['approve', 'reject', 'modify', 'add', 'remove']
        
        for field in required_fields:
            if field not in feedback_data:
                return False
        
        if feedback_data['action'] not in valid_actions:
            return False
        
        return True

    def _create_approved_exercise_session(self, patient_id: int, feedback_data: Dict) -> None:
        """Create exercise session for approved recommendation"""
        try:
            # This would create the actual exercise session
            # Implementation depends on your exercise session creation logic
            pass
            
        except Exception as e:
            logger.error(f"Error creating approved exercise session: {str(e)}")

    def _create_modified_recommendation(self, patient_id: int, feedback_data: Dict) -> None:
        """Create modified exercise recommendation"""
        try:
            # Store modified recommendation
            modified_rec = RecommendationResult(
                patient_id=patient_id,
                recommendation_type='exercise_modified',
                recommendation_data=json.dumps(feedback_data.get('modified_recommendations', {})),
                provider_feedback=feedback_data.get('clinical_rationale', ''),
                created_at=datetime.now()
            )
            
            db.session.add(modified_rec)
            
        except Exception as e:
            logger.error(f"Error creating modified recommendation: {str(e)}")

    def _create_new_exercise_recommendation(self, patient_id: int, feedback_data: Dict) -> None:
        """Create new exercise recommendation added by provider"""
        try:
            new_rec = RecommendationResult(
                patient_id=patient_id,
                recommendation_type='exercise_added',
                recommendation_data=json.dumps({
                    'exercise_type': feedback_data.get('exercise_type'),
                    'added_by_provider': True,
                    'clinical_rationale': feedback_data.get('clinical_rationale', '')
                }),
                created_at=datetime.now()
            )
            
            db.session.add(new_rec)
            
        except Exception as e:
            logger.error(f"Error creating new exercise recommendation: {str(e)}")

    def _update_rl_training_data(self, patient_id: int, provider_id: int, feedback_data: Dict) -> None:
        """Update reinforcement learning training data"""
        try:
            # This would update the RL training dataset
            # Implementation depends on your RL data storage system
            pass
            
        except Exception as e:
            logger.error(f"Error updating RL training data: {str(e)}")

    def _get_next_recommendations(self, patient_id: int) -> List[Dict]:
        """Get next set of recommendations after feedback"""
        try:
            # This would generate next recommendations based on feedback
            # Implementation depends on your recommendation system
            return []
            
        except Exception as e:
            logger.error(f"Error getting next recommendations: {str(e)}")
            return []

    def _get_pending_reviews(self, patient_id: int, provider_id: int) -> List[Dict]:
        """Get pending exercise reviews for a patient"""
        try:
            # This would check for pending reviews
            # Implementation depends on your review system
            return []
            
        except Exception as e:
            logger.error(f"Error getting pending reviews: {str(e)}")
            return []

    def _get_patient_summary(self, patient_id: int, provider_id: int) -> Dict:
        """Get patient summary for provider dashboard"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {}
            
            latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                .order_by(desc(PHQ9Assessment.assessment_date)).first()
            
            recent_feedback = ProviderExerciseFeedback.query.filter_by(
                patient_id=patient_id, provider_id=provider_id
            ).order_by(desc(ProviderExerciseFeedback.submitted_at)).limit(5).all()
            
            return {
                'patient_id': patient.id,
                'name': f"{patient.first_name} {patient.last_name}",
                'current_severity': latest_assessment.severity_level if latest_assessment else 'unknown',
                'last_assessment': latest_assessment.assessment_date.isoformat() if latest_assessment else None,
                'recent_feedback_count': len(recent_feedback),
                'last_feedback': recent_feedback[0].submitted_at.isoformat() if recent_feedback else None
            }
            
        except Exception as e:
            logger.error(f"Error getting patient summary: {str(e)}")
            return {}

    def _get_recent_feedback(self, provider_id: int) -> List[Dict]:
        """Get recent feedback from provider"""
        try:
            recent_feedback = ProviderExerciseFeedback.query.filter_by(provider_id=provider_id)\
                .order_by(desc(ProviderExerciseFeedback.submitted_at)).limit(10).all()
            
            feedback = []
            for record in recent_feedback:
                feedback.append({
                    'patient_id': record.patient_id,
                    'exercise_type': record.exercise_type,
                    'action': record.action,
                    'category': record.feedback_category,
                    'date': record.submitted_at.isoformat()
                })
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error getting recent feedback: {str(e)}")
            return []

    def _get_feedback_analytics(self, provider_id: int) -> Dict:
        """Get feedback analytics for provider"""
        try:
            # Get feedback statistics
            total_feedback = ProviderExerciseFeedback.query.filter_by(provider_id=provider_id).count()
            
            action_counts = db.session.query(
                ProviderExerciseFeedback.action,
                func.count(ProviderExerciseFeedback.id)
            ).filter_by(provider_id=provider_id).group_by(ProviderExerciseFeedback.action).all()
            
            category_counts = db.session.query(
                ProviderExerciseFeedback.feedback_category,
                func.count(ProviderExerciseFeedback.id)
            ).filter_by(provider_id=provider_id).group_by(ProviderExerciseFeedback.feedback_category).all()
            
            return {
                'total_feedback': total_feedback,
                'action_distribution': dict(action_counts),
                'category_distribution': dict(category_counts),
                'feedback_trends': self._calculate_feedback_trends(provider_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback analytics: {str(e)}")
            return {}

    def _get_rl_training_progress(self, provider_id: int) -> Dict:
        """Get RL training progress for provider"""
        try:
            # This would get RL training progress
            # Implementation depends on your RL system
            return {
                'training_samples': 0,
                'model_accuracy': 0.0,
                'last_training': None,
                'next_training': None
            }
            
        except Exception as e:
            logger.error(f"Error getting RL training progress: {str(e)}")
            return {}

    def _get_patient_context(self, patient_id: int, timestamp: datetime) -> Dict:
        """Get patient context at specific timestamp for RL training"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {}
            
            # Get assessment at or before timestamp
            assessment = PHQ9Assessment.query.filter(
                and_(
                    PHQ9Assessment.patient_id == patient_id,
                    PHQ9Assessment.assessment_date <= timestamp
                )
            ).order_by(desc(PHQ9Assessment.assessment_date)).first()
            
            # Get mood entries around timestamp
            mood_entries = MoodEntry.query.filter(
                and_(
                    MoodEntry.patient_id == patient_id,
                    MoodEntry.entry_date <= timestamp
                )
            ).order_by(desc(MoodEntry.entry_date)).limit(7).all()
            
            # Get exercise history before timestamp
            exercise_history = ExerciseSession.query.filter(
                and_(
                    ExerciseSession.patient_id == patient_id,
                    ExerciseSession.start_time <= timestamp
                )
            ).order_by(desc(ExerciseSession.start_time)).limit(10).all()
            
            return {
                'patient_id': patient_id,
                'age': patient.age,
                'gender': patient.gender,
                'assessment_data': {
                    'total_score': assessment.total_score if assessment else None,
                    'severity_level': assessment.severity_level if assessment else None,
                    'q9_risk': assessment.q9_risk_flag if assessment else False,
                    'assessment_date': assessment.assessment_date.isoformat() if assessment else None
                },
                'mood_trend': [entry.mood_score for entry in mood_entries],
                'exercise_history': [{
                    'type': session.exercise.type,
                    'completion_status': session.completion_status,
                    'engagement_score': session.engagement_score,
                    'date': session.start_time.isoformat()
                } for session in exercise_history],
                'context_timestamp': timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting patient context: {str(e)}")
            return {}

    def _get_exercise_context(self, exercise_type: str) -> Dict:
        """Get exercise context for RL training"""
        try:
            exercise = Exercise.query.filter_by(type=exercise_type).first()
            if not exercise:
                return {}
            
            return {
                'exercise_id': exercise.id,
                'type': exercise.type,
                'name': exercise.name,
                'difficulty_level': exercise.difficulty_level,
                'estimated_duration': exercise.estimated_duration,
                'clinical_focus_areas': exercise.clinical_focus_areas,
                'engagement_mechanics': exercise.engagement_mechanics
            }
            
        except Exception as e:
            logger.error(f"Error getting exercise context: {str(e)}")
            return {}

    def _calculate_reward_signal(self, feedback_record) -> float:
        """Calculate reward signal for RL training"""
        try:
            # Simple reward calculation based on provider action
            reward_map = {
                'approve': 1.0,
                'modify': 0.5,
                'add': 0.8,
                'reject': -0.5,
                'remove': -0.3
            }
            
            base_reward = reward_map.get(feedback_record.action, 0.0)
            
            # Adjust based on feedback category
            if feedback_record.feedback_category == 'safety_concerns':
                base_reward *= 1.5  # Higher weight for safety
            elif feedback_record.feedback_category == 'effectiveness':
                base_reward *= 1.2  # Higher weight for effectiveness
            
            return base_reward
            
        except Exception as e:
            logger.error(f"Error calculating reward signal: {str(e)}")
            return 0.0

    def _get_outcome_data(self, patient_id: int, timestamp: datetime) -> Dict:
        """Get outcome data for RL training"""
        try:
            # Get mood improvement after feedback
            mood_after = MoodEntry.query.filter(
                and_(
                    MoodEntry.patient_id == patient_id,
                    MoodEntry.entry_date > timestamp
                )
            ).order_by(MoodEntry.entry_date).limit(7).all()
            
            # Get exercise completion after feedback
            exercises_after = ExerciseSession.query.filter(
                and_(
                    ExerciseSession.patient_id == patient_id,
                    ExerciseSession.start_time > timestamp
                )
            ).order_by(ExerciseSession.start_time).limit(10).all()
            
            return {
                'mood_improvement': [entry.mood_score for entry in mood_after],
                'exercise_completion': [session.completion_status for session in exercises_after],
                'engagement_scores': [session.engagement_score for session in exercises_after if session.engagement_score],
                'outcome_period_days': 7
            }
            
        except Exception as e:
            logger.error(f"Error getting outcome data: {str(e)}")
            return {}

    def _calculate_data_quality_metrics(self, training_data: List[Dict]) -> Dict:
        """Calculate data quality metrics for RL training"""
        try:
            if not training_data:
                return {}
            
            total_samples = len(training_data)
            complete_samples = sum(1 for sample in training_data if sample.get('patient_context') and sample.get('exercise_context'))
            
            return {
                'total_samples': total_samples,
                'complete_samples': complete_samples,
                'completeness_rate': complete_samples / total_samples if total_samples > 0 else 0,
                'average_reward': sum(sample.get('reward_signal', 0) for sample in training_data) / total_samples if total_samples > 0 else 0,
                'feedback_distribution': self._calculate_feedback_distribution(training_data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating data quality metrics: {str(e)}")
            return {}

    def _calculate_feature_importance(self, training_data: List[Dict]) -> Dict:
        """Calculate feature importance for RL training"""
        try:
            # Simple feature importance calculation
            # In practice, you'd use more sophisticated methods
            
            feature_counts = {}
            for sample in training_data:
                patient_context = sample.get('patient_context', {})
                assessment_data = patient_context.get('assessment_data', {})
                
                # Count features
                severity = assessment_data.get('severity_level')
                if severity:
                    feature_counts[f'severity_{severity}'] = feature_counts.get(f'severity_{severity}', 0) + 1
                
                q9_risk = assessment_data.get('q9_risk')
                if q9_risk:
                    feature_counts['q9_risk'] = feature_counts.get('q9_risk', 0) + 1
            
            return feature_counts
            
        except Exception as e:
            logger.error(f"Error calculating feature importance: {str(e)}")
            return {}

    def _calculate_feedback_trends(self, provider_id: int) -> Dict:
        """Calculate feedback trends over time"""
        try:
            # Get feedback over last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            recent_feedback = ProviderExerciseFeedback.query.filter(
                and_(
                    ProviderExerciseFeedback.provider_id == provider_id,
                    ProviderExerciseFeedback.submitted_at >= thirty_days_ago
                )
            ).all()
            
            # Calculate trends
            daily_counts = {}
            for feedback in recent_feedback:
                date_key = feedback.submitted_at.date().isoformat()
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
            
            return {
                'daily_feedback_counts': daily_counts,
                'average_daily_feedback': len(recent_feedback) / 30,
                'trend_direction': 'increasing' if len(recent_feedback) > 15 else 'stable'
            }
            
        except Exception as e:
            logger.error(f"Error calculating feedback trends: {str(e)}")
            return {}

    def _calculate_feedback_distribution(self, training_data: List[Dict]) -> Dict:
        """Calculate feedback distribution for data quality"""
        try:
            action_counts = {}
            category_counts = {}
            
            for sample in training_data:
                action = sample.get('provider_action')
                category = sample.get('feedback_category')
                
                if action:
                    action_counts[action] = action_counts.get(action, 0) + 1
                
                if category:
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                'action_distribution': action_counts,
                'category_distribution': category_counts
            }
            
        except Exception as e:
            logger.error(f"Error calculating feedback distribution: {str(e)}")
            return {}

# Initialize the feedback system
provider_exercise_feedback = ProviderExerciseFeedbackService()
