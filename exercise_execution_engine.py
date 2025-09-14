#!/usr/bin/env python3
"""
Exercise Execution Engine
Real-time exercise delivery and adaptation system
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

from app_ml_complete import (
    db, Patient, Exercise, ExerciseSession, MoodEntry, 
    CrisisAlert, BehavioralActivationProgress
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExerciseExecutionEngine:
    """Real-time exercise execution and adaptation engine"""
    
    def __init__(self):
        self.exercise_templates = {
            'mood_check_in': {
                'title': 'Quick Mood Check-in',
                'description': 'Take 30 seconds to assess your current mood',
                'steps': [
                    'Rate your mood from 1-10',
                    'Note any immediate thoughts or feelings',
                    'Record your energy level'
                ],
                'duration': 30,
                'category': 'assessment'
            },
            'cbt_thought_record': {
                'title': 'CBT Thought Record',
                'description': 'Challenge negative thoughts with evidence',
                'steps': [
                    'Identify the situation',
                    'Record automatic thoughts',
                    'List evidence for and against',
                    'Generate balanced thoughts'
                ],
                'duration': 600,
                'category': 'cognitive'
            },
            'mindfulness_exercise': {
                'title': 'Mindfulness Practice',
                'description': 'Present moment awareness exercise',
                'steps': [
                    'Find a comfortable position',
                    'Focus on your breath',
                    'Notice thoughts without judgment',
                    'Return to breath when distracted'
                ],
                'duration': 300,
                'category': 'mindfulness'
            },
            'behavioral_activation': {
                'title': 'Behavioral Activation',
                'description': 'Plan and complete meaningful activities',
                'steps': [
                    'Identify values and goals',
                    'Plan specific activities',
                    'Schedule and complete activities',
                    'Reflect on mood changes'
                ],
                'duration': 900,
                'category': 'behavioral'
            },
            'crisis_monitoring': {
                'title': 'Crisis Safety Check',
                'description': 'Assess current safety and crisis level',
                'steps': [
                    'Rate current distress level',
                    'Assess safety thoughts',
                    'Use grounding techniques if needed',
                    'Contact provider if necessary'
                ],
                'duration': 120,
                'category': 'crisis'
            },
            'breathing_grounding': {
                'title': 'Crisis Breathing & Grounding',
                'description': 'Immediate crisis intervention techniques',
                'steps': [
                    '4-7-8 breathing pattern',
                    '5-4-3-2-1 grounding exercise',
                    'Safe place visualization',
                    'Emergency contact if needed'
                ],
                'duration': 180,
                'category': 'crisis'
            }
        }
        
        self.adaptation_triggers = {
            'crisis_detected': {
                'action': 'immediate_crisis_exercise',
                'priority': 'critical'
            },
            'mood_deterioration': {
                'action': 'increase_support_exercises',
                'priority': 'high'
            },
            'low_engagement': {
                'action': 'simplify_exercises',
                'priority': 'medium'
            },
            'high_engagement': {
                'action': 'advance_exercises',
                'priority': 'medium'
            }
        }

    def execute_exercise(self, patient_id: int, exercise_type: str, 
                        context: Dict = None) -> Dict:
        """Execute an exercise for a patient with real-time adaptation"""
        try:
            # Get patient and current state
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Get exercise template
            template = self.exercise_templates.get(exercise_type)
            if not template:
                return {'error': 'Exercise type not found'}
            
            # Check for crisis triggers
            crisis_check = self._check_crisis_triggers(patient_id, context)
            if crisis_check['crisis_detected']:
                return self._handle_crisis_situation(patient_id, crisis_check)
            
            # Adapt exercise based on current state
            adapted_exercise = self._adapt_exercise_for_patient(
                template, patient_id, context
            )
            
            # Execute the exercise
            execution_result = self._perform_exercise(patient_id, adapted_exercise)
            
            # Monitor and adapt based on execution
            adaptation_result = self._monitor_and_adapt(patient_id, execution_result)
            
            # Save session data
            session_data = self._save_exercise_session(
                patient_id, exercise_type, execution_result, adaptation_result
            )
            
            return {
                'exercise_completed': True,
                'exercise_data': adapted_exercise,
                'execution_result': execution_result,
                'adaptation_applied': adaptation_result,
                'session_id': session_data.get('session_id'),
                'next_recommendations': self._generate_next_recommendations(patient_id)
            }
            
        except Exception as e:
            logger.error(f"Error executing exercise: {str(e)}")
            return {'error': f'Exercise execution failed: {str(e)}'}

    def _check_crisis_triggers(self, patient_id: int, context: Dict) -> Dict:
        """Check for crisis triggers before exercise execution"""
        try:
            crisis_detected = False
            crisis_level = 'none'
            triggers = []
            
            # Check recent mood entries
            recent_mood = MoodEntry.query.filter_by(patient_id=patient_id)\
                .order_by(desc(MoodEntry.entry_date)).first()
            
            if recent_mood and recent_mood.mood_score <= 2:
                crisis_detected = True
                crisis_level = 'moderate'
                triggers.append('very_low_mood')
            
            # Check for crisis alerts
            recent_crisis = CrisisAlert.query.filter_by(patient_id=patient_id)\
                .order_by(desc(CrisisAlert.created_at)).first()
            
            if recent_crisis and (datetime.now() - recent_crisis.created_at).days < 1:
                crisis_detected = True
                crisis_level = 'severe'
                triggers.append('recent_crisis_alert')
            
            # Check context for immediate crisis indicators
            if context and context.get('crisis_indicators'):
                crisis_detected = True
                crisis_level = 'immediate'
                triggers.extend(context['crisis_indicators'])
            
            return {
                'crisis_detected': crisis_detected,
                'crisis_level': crisis_level,
                'triggers': triggers,
                'requires_immediate_action': crisis_level in ['severe', 'immediate']
            }
            
        except Exception as e:
            logger.error(f"Error checking crisis triggers: {str(e)}")
            return {'crisis_detected': False, 'crisis_level': 'none', 'triggers': []}

    def _handle_crisis_situation(self, patient_id: int, crisis_check: Dict) -> Dict:
        """Handle crisis situation with immediate intervention"""
        try:
            # Create crisis alert
            crisis_alert = CrisisAlert(
                patient_id=patient_id,
                alert_type='exercise_crisis_detected',
                severity_level=crisis_check['crisis_level'],
                triggers=json.dumps(crisis_check['triggers']),
                created_at=datetime.now()
            )
            db.session.add(crisis_alert)
            
            # Execute crisis exercise
            crisis_exercise = self.exercise_templates['breathing_grounding']
            crisis_result = self._perform_crisis_exercise(patient_id, crisis_exercise)
            
            # Notify provider if needed
            if crisis_check['requires_immediate_action']:
                self._notify_provider_crisis(patient_id, crisis_check)
            
            db.session.commit()
            
            return {
                'crisis_handled': True,
                'crisis_level': crisis_check['crisis_level'],
                'crisis_exercise_completed': True,
                'provider_notified': crisis_check['requires_immediate_action'],
                'next_action': 'continue_with_crisis_monitoring'
            }
            
        except Exception as e:
            logger.error(f"Error handling crisis situation: {str(e)}")
            db.session.rollback()
            return {'error': f'Crisis handling failed: {str(e)}'}

    def _adapt_exercise_for_patient(self, template: Dict, patient_id: int, 
                                  context: Dict) -> Dict:
        """Adapt exercise template for specific patient"""
        try:
            adapted = template.copy()
            
            # Get patient's exercise history
            recent_sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).limit(5).all()
            
            # Adapt based on recent performance
            if recent_sessions:
                avg_engagement = sum(s.engagement_score for s in recent_sessions if s.engagement_score) / len(recent_sessions)
                
                if avg_engagement < 4:
                    # Simplify exercise
                    adapted['steps'] = adapted['steps'][:2]  # Reduce steps
                    adapted['duration'] = max(60, adapted['duration'] // 2)  # Reduce duration
                    adapted['difficulty'] = 'simplified'
                elif avg_engagement > 8:
                    # Advance exercise
                    adapted['steps'].append('Reflect on insights gained')
                    adapted['duration'] = int(adapted['duration'] * 1.2)
                    adapted['difficulty'] = 'advanced'
            
            # Adapt based on time of day
            current_hour = datetime.now().hour
            if current_hour < 10:  # Morning
                adapted['steps'].insert(0, 'Set intention for the day')
            elif current_hour > 18:  # Evening
                adapted['steps'].append('Reflect on today\'s experiences')
            
            # Adapt based on context
            if context and context.get('mood_level'):
                mood_level = context['mood_level']
                if mood_level <= 3:
                    adapted['steps'].insert(0, 'Take a moment to breathe deeply')
                    adapted['steps'].append('Remember this is temporary')
                elif mood_level >= 8:
                    adapted['steps'].append('Build on this positive momentum')
            
            return adapted
            
        except Exception as e:
            logger.error(f"Error adapting exercise: {str(e)}")
            return template

    def _perform_exercise(self, patient_id: int, exercise: Dict) -> Dict:
        """Perform the actual exercise execution"""
        try:
            start_time = datetime.now()
            
            # Simulate exercise performance
            # In real implementation, this would guide the patient through the exercise
            exercise_result = {
                'exercise_type': exercise.get('title', 'Unknown'),
                'steps_completed': len(exercise.get('steps', [])),
                'duration_actual': exercise.get('duration', 0),
                'engagement_level': self._assess_engagement(patient_id, exercise),
                'effectiveness_rating': None,  # Will be set by patient
                'completion_status': 'completed',
                'start_time': start_time,
                'completion_time': start_time + timedelta(seconds=exercise.get('duration', 0))
            }
            
            return exercise_result
            
        except Exception as e:
            logger.error(f"Error performing exercise: {str(e)}")
            return {'error': f'Exercise performance failed: {str(e)}'}

    def _perform_crisis_exercise(self, patient_id: int, exercise: Dict) -> Dict:
        """Perform crisis-specific exercise with enhanced monitoring"""
        try:
            start_time = datetime.now()
            
            # Enhanced crisis exercise performance
            crisis_result = {
                'exercise_type': 'Crisis Intervention',
                'steps_completed': len(exercise.get('steps', [])),
                'duration_actual': exercise.get('duration', 0),
                'engagement_level': 10,  # High engagement for crisis
                'effectiveness_rating': None,
                'completion_status': 'completed',
                'crisis_intervention': True,
                'start_time': start_time,
                'completion_time': start_time + timedelta(seconds=exercise.get('duration', 0))
            }
            
            return crisis_result
            
        except Exception as e:
            logger.error(f"Error performing crisis exercise: {str(e)}")
            return {'error': f'Crisis exercise failed: {str(e)}'}

    def _monitor_and_adapt(self, patient_id: int, execution_result: Dict) -> Dict:
        """Monitor exercise execution and apply real-time adaptations"""
        try:
            adaptations = []
            
            # Check engagement level
            engagement = execution_result.get('engagement_level', 0)
            if engagement < 4:
                adaptations.append({
                    'type': 'simplify_next_exercise',
                    'reason': 'low_engagement',
                    'priority': 'medium'
                })
            elif engagement > 8:
                adaptations.append({
                    'type': 'advance_next_exercise',
                    'reason': 'high_engagement',
                    'priority': 'medium'
                })
            
            # Check completion status
            if execution_result.get('completion_status') != 'completed':
                adaptations.append({
                    'type': 'reduce_difficulty',
                    'reason': 'incomplete_exercise',
                    'priority': 'high'
                })
            
            # Check for crisis indicators during exercise
            if execution_result.get('crisis_intervention'):
                adaptations.append({
                    'type': 'increase_crisis_monitoring',
                    'reason': 'crisis_during_exercise',
                    'priority': 'critical'
                })
            
            return {
                'adaptations_applied': adaptations,
                'next_exercise_adjustments': self._generate_adjustments(adaptations)
            }
            
        except Exception as e:
            logger.error(f"Error monitoring and adapting: {str(e)}")
            return {'adaptations_applied': [], 'next_exercise_adjustments': {}}

    def _assess_engagement(self, patient_id: int, exercise: Dict) -> int:
        """Assess patient engagement level during exercise"""
        try:
            # In real implementation, this would use various metrics
            # For now, simulate based on exercise type and patient history
            
            base_engagement = 7  # Default moderate engagement
            
            # Adjust based on exercise type
            if exercise.get('category') == 'crisis':
                base_engagement = 9  # High engagement for crisis exercises
            elif exercise.get('category') == 'assessment':
                base_engagement = 6  # Lower engagement for assessments
            
            # Adjust based on patient history
            recent_sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).limit(3).all()
            
            if recent_sessions:
                avg_recent_engagement = sum(s.engagement_score for s in recent_sessions if s.engagement_score) / len(recent_sessions)
                base_engagement = (base_engagement + avg_recent_engagement) / 2
            
            return min(10, max(1, int(base_engagement)))
            
        except Exception as e:
            logger.error(f"Error assessing engagement: {str(e)}")
            return 5

    def _save_exercise_session(self, patient_id: int, exercise_type: str, 
                             execution_result: Dict, adaptation_result: Dict) -> Dict:
        """Save exercise session data to database"""
        try:
            # Create exercise session
            session = ExerciseSession(
                patient_id=patient_id,
                exercise_id=self._get_exercise_id(exercise_type),
                start_time=execution_result.get('start_time', datetime.now()),
                completion_time=execution_result.get('completion_time'),
                completion_status=execution_result.get('completion_status', 'completed'),
                engagement_score=execution_result.get('engagement_level', 5),
                effectiveness_rating=execution_result.get('effectiveness_rating'),
                session_notes=json.dumps(adaptation_result)
            )
            
            db.session.add(session)
            db.session.commit()
            
            return {
                'session_id': session.id,
                'saved': True
            }
            
        except Exception as e:
            logger.error(f"Error saving exercise session: {str(e)}")
            db.session.rollback()
            return {'error': f'Session save failed: {str(e)}'}

    def _generate_next_recommendations(self, patient_id: int) -> List[Dict]:
        """Generate next exercise recommendations based on current session"""
        try:
            # Get recent session
            recent_session = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).first()
            
            if not recent_session:
                return []
            
            recommendations = []
            
            # Based on engagement level
            if recent_session.engagement_score >= 8:
                recommendations.append({
                    'type': 'advance_exercise',
                    'exercise': 'cbt_thought_record',
                    'rationale': 'High engagement - ready for advanced exercise'
                })
            elif recent_session.engagement_score <= 4:
                recommendations.append({
                    'type': 'simplify_exercise',
                    'exercise': 'mood_check_in',
                    'rationale': 'Low engagement - simplified exercise recommended'
                })
            
            # Based on completion status
            if recent_session.completion_status != 'completed':
                recommendations.append({
                    'type': 'repeat_exercise',
                    'exercise': recent_session.exercise.type,
                    'rationale': 'Incomplete exercise - recommend retry'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating next recommendations: {str(e)}")
            return []

    def _generate_adjustments(self, adaptations: List[Dict]) -> Dict:
        """Generate specific adjustments based on adaptations"""
        adjustments = {}
        
        for adaptation in adaptations:
            if adaptation['type'] == 'simplify_next_exercise':
                adjustments['reduce_steps'] = True
                adjustments['reduce_duration'] = True
            elif adaptation['type'] == 'advance_next_exercise':
                adjustments['add_reflection'] = True
                adjustments['increase_duration'] = True
            elif adaptation['type'] == 'reduce_difficulty':
                adjustments['beginner_level'] = True
                adjustments['minimal_commitment'] = True
        
        return adjustments

    def _get_exercise_id(self, exercise_type: str) -> int:
        """Get exercise ID from exercise type"""
        try:
            exercise = Exercise.query.filter_by(type=exercise_type).first()
            return exercise.id if exercise else 1
        except Exception as e:
            logger.error(f"Error getting exercise ID: {str(e)}")
            return 1

    def _notify_provider_crisis(self, patient_id: int, crisis_check: Dict) -> None:
        """Notify provider of crisis situation"""
        try:
            # In real implementation, this would send notification to provider
            logger.info(f"CRISIS ALERT: Patient {patient_id} - Level: {crisis_check['crisis_level']}")
            
            # Create crisis alert record
            crisis_alert = CrisisAlert(
                patient_id=patient_id,
                alert_type='provider_notification',
                severity_level=crisis_check['crisis_level'],
                triggers=json.dumps(crisis_check['triggers']),
                created_at=datetime.now()
            )
            db.session.add(crisis_alert)
            
        except Exception as e:
            logger.error(f"Error notifying provider: {str(e)}")

# Initialize the execution engine
exercise_execution_engine = ExerciseExecutionEngine()
