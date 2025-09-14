#!/usr/bin/env python3
"""
PHQ-9 Exercise Integration System
Comprehensive integration of PHQ-9 analysis with adaptive exercise recommendations
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
    db, Patient, PHQ9Assessment, Exercise, ExerciseSession, 
    Activity, ActivityCategory, BehavioralActivationProgress,
    CrisisAlert, RecommendationResult, MoodEntry, MindfulnessSession
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PHQ9ExerciseIntegration:
    """Comprehensive PHQ-9 to exercise integration system with adaptive recommendations"""
    
    def __init__(self):
        # Severity-based exercise prescription system
        self.severity_exercises = {
            'minimal': {  # 0-4
                'daily': ['mood_check_in'],
                'weekly': ['gratitude_exercise', 'wellness_tracking'],
                'frequency': 'low',
                'focus': 'maintenance',
                'duration': '30_seconds_to_5_minutes'
            },
            'mild': {  # 5-9
                'daily': ['mood_tracking', 'cbt_thought_record'],
                'weekly': ['mindfulness_exercise', 'activity_planning'],
                'frequency': 'moderate',
                'focus': 'skill_building',
                'duration': '5_to_15_minutes'
            },
            'moderate': {  # 10-14
                'daily': ['mood_tracking', 'behavioral_activation', 'cbt_exercises'],
                'weekly': ['mindfulness_exercises', 'activity_scheduling'],
                'frequency': 'high',
                'focus': 'active_treatment',
                'duration': '15_to_30_minutes'
            },
            'moderately_severe': {  # 15-19
                'daily': ['crisis_monitoring', 'structured_activities', 'cbt_intensive'],
                'micro_moments': ['safety_check_ins'],
                'emergency': ['breathing_grounding'],
                'frequency': 'intensive',
                'focus': 'crisis_management',
                'duration': '30_to_45_minutes'
            },
            'severe': {  # 20-27
                'daily': ['crisis_intervention', 'safety_planning', 'provider_alerts'],
                'micro_moments': ['multiple_safety_checks'],
                'emergency': ['immediate_crisis_exercises'],
                'frequency': 'crisis_level',
                'focus': 'crisis_intervention',
                'duration': 'as_needed'
            }
        }
        
        # Exercise categories and types
        self.exercise_types = {
            'mood_check_in': {
                'duration': 30,
                'difficulty': 'beginner',
                'category': 'assessment'
            },
            'cbt_thought_record': {
                'duration': 600,
                'difficulty': 'intermediate',
                'category': 'cognitive'
            },
            'mindfulness_exercise': {
                'duration': 300,
                'difficulty': 'beginner',
                'category': 'mindfulness'
            },
            'behavioral_activation': {
                'duration': 900,
                'difficulty': 'intermediate',
                'category': 'behavioral'
            },
            'crisis_monitoring': {
                'duration': 120,
                'difficulty': 'advanced',
                'category': 'crisis'
            },
            'breathing_grounding': {
                'duration': 180,
                'difficulty': 'beginner',
                'category': 'crisis'
            }
        }
        
        # Time-based scheduling
        self.schedule_times = {
            'morning': {'start': 8, 'end': 10},
            'midday': {'start': 12, 'end': 14},
            'evening': {'start': 18, 'end': 20}
        }

    def generate_adaptive_recommendations(self, patient_id: int, assessment_id: int) -> Dict:
        """Generate comprehensive adaptive exercise recommendations based on PHQ-9"""
        try:
            # Get assessment and patient data
            assessment = PHQ9Assessment.query.filter_by(id=assessment_id, patient_id=patient_id).first()
            patient = Patient.query.get(patient_id)
            
            if not assessment or not patient:
                return {'error': 'Assessment or patient not found'}
            
            # Analyze current state
            severity_level = self._get_severity_level(assessment.total_score)
            exercise_history = self._get_exercise_history(patient_id)
            mood_trends = self._analyze_mood_trends(patient_id)
            
            # Generate base recommendations
            base_recommendations = self._get_severity_based_exercises(severity_level)
            
            # Apply adaptive logic
            adaptive_recommendations = self._apply_adaptive_logic(
                base_recommendations, exercise_history, mood_trends, severity_level
            )
            
            # Create scheduling plan
            schedule_plan = self._create_schedule_plan(adaptive_recommendations, patient_id)
            
            # Generate monitoring and feedback systems
            monitoring_plan = self._create_monitoring_plan(severity_level, assessment.q9_risk_flag)
            feedback_system = self._create_feedback_system(patient_id)
            
            # Create provider integration
            provider_integration = self._create_provider_integration(severity_level, assessment.q9_risk_flag)
            
            # Create motivation system
            motivation_system = self._create_motivation_system(patient_id, exercise_history)
            
            # Ensure clinical safety
            safety_protocols = self._create_safety_protocols(severity_level, assessment.q9_risk_flag)
            
            return {
                'assessment_summary': {
                    'total_score': assessment.total_score,
                    'severity_level': severity_level,
                    'q9_risk': assessment.q9_risk_flag,
                    'assessment_date': assessment.assessment_date.isoformat()
                },
                'exercise_recommendations': adaptive_recommendations,
                'schedule_plan': schedule_plan,
                'monitoring_plan': monitoring_plan,
                'feedback_system': feedback_system,
                'provider_integration': provider_integration,
                'motivation_system': motivation_system,
                'safety_protocols': safety_protocols
            }
            
        except Exception as e:
            logger.error(f"Error generating adaptive recommendations: {str(e)}")
            return {'error': f'Failed to generate recommendations: {str(e)}'}

    def _get_severity_level(self, total_score: int) -> str:
        """Determine severity level from PHQ-9 total score"""
        if total_score <= 4:
            return 'minimal'
        elif total_score <= 9:
            return 'mild'
        elif total_score <= 14:
            return 'moderate'
        elif total_score <= 19:
            return 'moderately_severe'
        else:
            return 'severe'

    def _get_severity_based_exercises(self, severity_level: str) -> Dict:
        """Get base exercise recommendations for severity level"""
        return self.severity_exercises.get(severity_level, {})

    def _apply_adaptive_logic(self, base_recommendations: Dict, exercise_history: List[Dict], 
                            mood_trends: Dict, severity_level: str) -> Dict:
        """Apply adaptive logic to base recommendations"""
        adaptive_recs = base_recommendations.copy()
        
        # Improvement detection
        if self._detect_improvement(mood_trends, exercise_history):
            adaptive_recs = self._reduce_intensity(adaptive_recs, 0.25)
        
        # Deterioration detection
        if self._detect_deterioration(mood_trends, exercise_history):
            adaptive_recs = self._increase_intensity(adaptive_recs)
        
        # Engagement adaptation
        engagement_patterns = self._analyze_engagement_patterns(exercise_history)
        adaptive_recs = self._adapt_to_engagement(adaptive_recs, engagement_patterns)
        
        return adaptive_recs

    def _detect_improvement(self, mood_trends: Dict, exercise_history: List[Dict]) -> bool:
        """Detect if patient is showing improvement"""
        try:
            # Check for 7+ consecutive days of mood improvement
            if len(mood_trends.get('daily_scores', [])) >= 7:
                recent_scores = mood_trends['daily_scores'][-7:]
                if all(recent_scores[i] < recent_scores[i-1] for i in range(1, len(recent_scores))):
                    return True
            
            # Check for >85% exercise completion for 2 weeks
            if len(exercise_history) >= 14:
                recent_exercises = exercise_history[-14:]
                completion_rate = sum(1 for ex in recent_exercises if ex['completion_status'] == 'completed') / len(recent_exercises)
                if completion_rate > 0.85:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting improvement: {str(e)}")
            return False

    def _detect_deterioration(self, mood_trends: Dict, exercise_history: List[Dict]) -> bool:
        """Detect if patient is showing deterioration"""
        try:
            # Check for 5+ consecutive days of mood decline
            if len(mood_trends.get('daily_scores', [])) >= 5:
                recent_scores = mood_trends['daily_scores'][-5:]
                if all(recent_scores[i] > recent_scores[i-1] for i in range(1, len(recent_scores))):
                    return True
            
            # Check for <50% exercise completion
            if len(exercise_history) >= 7:
                recent_exercises = exercise_history[-7:]
                completion_rate = sum(1 for ex in recent_exercises if ex['completion_status'] == 'completed') / len(recent_exercises)
                if completion_rate < 0.5:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting deterioration: {str(e)}")
            return False

    def _reduce_intensity(self, recommendations: Dict, reduction_factor: float) -> Dict:
        """Reduce exercise intensity based on improvement"""
        reduced_recs = recommendations.copy()
        
        # Reduce frequency
        if 'frequency' in reduced_recs:
            if reduced_recs['frequency'] == 'intensive':
                reduced_recs['frequency'] = 'high'
            elif reduced_recs['frequency'] == 'high':
                reduced_recs['frequency'] = 'moderate'
            elif reduced_recs['frequency'] == 'moderate':
                reduced_recs['frequency'] = 'low'
        
        # Reduce daily exercises
        if 'daily' in reduced_recs:
            daily_exercises = reduced_recs['daily']
            reduced_count = max(1, int(len(daily_exercises) * (1 - reduction_factor)))
            reduced_recs['daily'] = daily_exercises[:reduced_count]
        
        return reduced_recs

    def _increase_intensity(self, recommendations: Dict) -> Dict:
        """Increase exercise intensity based on deterioration"""
        increased_recs = recommendations.copy()
        
        # Increase frequency
        if 'frequency' in increased_recs:
            if increased_recs['frequency'] == 'low':
                increased_recs['frequency'] = 'moderate'
            elif increased_recs['frequency'] == 'moderate':
                increased_recs['frequency'] = 'high'
            elif increased_recs['frequency'] == 'high':
                increased_recs['frequency'] = 'intensive'
        
        # Add crisis monitoring if not present
        if 'crisis_monitoring' not in increased_recs.get('daily', []):
            if 'daily' not in increased_recs:
                increased_recs['daily'] = []
            increased_recs['daily'].append('crisis_monitoring')
        
        return increased_recs

    def _create_schedule_plan(self, recommendations: Dict, patient_id: int) -> Dict:
        """Create time-based exercise scheduling plan"""
        try:
            # Get patient's preferred times
            preferred_times = self._get_patient_preferred_times(patient_id)
            
            schedule = {
                'morning': {
                    'time_range': '8:00-10:00',
                    'exercises': ['mood_check_in'],
                    'rationale': 'Start day with mood assessment'
                },
                'midday': {
                    'time_range': '12:00-14:00',
                    'exercises': [],
                    'rationale': 'Midday check-in and intervention'
                },
                'evening': {
                    'time_range': '18:00-20:00',
                    'exercises': [],
                    'rationale': 'Evening reflection and planning'
                },
                'emergency': {
                    'availability': '24/7',
                    'exercises': ['breathing_grounding', 'crisis_intervention'],
                    'rationale': 'Immediate crisis support'
                }
            }
            
            # Distribute exercises based on recommendations
            daily_exercises = recommendations.get('daily', [])
            if len(daily_exercises) >= 2:
                schedule['midday']['exercises'].append(daily_exercises[1])
            if len(daily_exercises) >= 3:
                schedule['evening']['exercises'].append(daily_exercises[2])
            
            # Add micro-moments if needed
            if 'micro_moments' in recommendations:
                schedule['micro_moments'] = {
                    'frequency': '2x_daily',
                    'exercises': recommendations['micro_moments'],
                    'rationale': 'Safety monitoring throughout day'
                }
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error creating schedule plan: {str(e)}")
            return {}

    def _create_monitoring_plan(self, severity_level: str, q9_risk: bool) -> Dict:
        """Create comprehensive monitoring plan"""
        monitoring = {
            'weekly_analysis': {
                'mood_improvement_tracking': True,
                'exercise_completion_rates': True,
                'effectiveness_measurement': True,
                'recommendation_optimization': True
            },
            'monthly_phq9_preparation': {
                'engagement_trend_analysis': True,
                'mood_exercise_correlation': True,
                'phq9_score_prediction': True,
                'provider_summary_preparation': True
            },
            'continuous_learning': {
                'exercise_outcome_tracking': True,
                'optimal_timing_identification': True,
                'early_warning_detection': True,
                'algorithm_refinement': True
            }
        }
        
        # Adjust based on severity and risk
        if q9_risk or severity_level in ['moderately_severe', 'severe']:
            monitoring['daily_crisis_monitoring'] = True
            monitoring['immediate_provider_alerts'] = True
        
        return monitoring

    def _create_feedback_system(self, patient_id: int) -> Dict:
        """Create feedback loop system for continuous optimization"""
        return {
            'weekly_analysis': {
                'mood_improvement_calculation': True,
                'exercise_effectiveness_measurement': True,
                'completion_rate_analysis': True,
                'next_week_recommendations': True
            },
            'monthly_phq9_preparation': {
                'engagement_trend_analysis': True,
                'mood_exercise_correlation': True,
                'phq9_score_prediction': True,
                'provider_progress_summary': True
            },
            'continuous_learning': {
                'best_outcome_exercise_tracking': True,
                'optimal_timing_learning': True,
                'early_warning_sign_detection': True,
                'crisis_detection_refinement': True
            }
        }

    def _create_provider_integration(self, severity_level: str, q9_risk: bool) -> Dict:
        """Create provider integration system"""
        integration = {
            'daily_dashboard': {
                'red_alerts': ['crisis_exercises_accessed', 'missed_exercises_severe'],
                'yellow_alerts': ['declining_engagement', 'concerning_mood_trends'],
                'green_status': ['on_track', 'good_engagement', 'improving_trends']
            },
            'weekly_reports': {
                'exercise_completion_summary': True,
                'effectiveness_metrics': True,
                'mood_trend_analysis': True,
                'recommended_adjustments': True,
                'patient_session_preparation': True
            },
            'crisis_escalation': {
                'immediate_notifications': q9_risk or severity_level in ['moderately_severe', 'severe'],
                'urgent_appointment_scheduling': q9_risk,
                'crisis_resource_recommendations': True
            }
        }
        
        return integration

    def _create_motivation_system(self, patient_id: int, exercise_history: List[Dict]) -> Dict:
        """Create patient motivation system"""
        return {
            'smart_notifications': {
                'personalized_timing': True,
                'progress_based_messages': True,
                'reminder_escalation': ['gentle', 'concerned', 'provider_alert']
            },
            'progress_visualization': {
                'exercise_mood_correlation': True,
                'milestone_celebration': ['7_days_consistent', 'mood_improvement_streaks'],
                'skill_development_progress': ['cbt_mastery', 'mindfulness_consistency']
            },
            'adaptive_encouragement': {
                'mood_based_messaging': True,
                'effective_exercise_highlighting': True,
                'phq9_improvement_connection': True
            }
        }

    def _create_safety_protocols(self, severity_level: str, q9_risk: bool) -> Dict:
        """Create clinical safety protocols"""
        protocols = {
            'crisis_override_protocols': {
                'suicidal_ideation_triggers': 'immediate_intensive_plan',
                'provider_notification_timeframe': '2_hours',
                'emergency_contact_integration': q9_risk
            },
            'treatment_boundaries': {
                'supplement_provider_care': True,
                'clear_contact_guidelines': True,
                'escalation_protocols': True
            },
            'evidence_based_adaptations': {
                'clinical_research_based': True,
                'provider_override_capabilities': True,
                'regular_effectiveness_validation': True
            }
        }
        
        return protocols

    def _get_exercise_history(self, patient_id: int) -> List[Dict]:
        """Get comprehensive exercise history for patient"""
        try:
            sessions = ExerciseSession.query.filter_by(patient_id=patient_id).all()
            mindfulness_sessions = MindfulnessSession.query.filter_by(patient_id=patient_id).all()
            
            history = []
            
            for session in sessions:
                history.append({
                    'type': 'exercise',
                    'exercise_type': session.exercise.type,
                    'completion_status': session.completion_status,
                    'engagement_score': session.engagement_score,
                    'effectiveness_rating': session.effectiveness_rating,
                    'date': session.start_time,
                    'duration': (session.completion_time - session.start_time).total_seconds() / 60 if session.completion_time else None
                })
            
            for session in mindfulness_sessions:
                history.append({
                    'type': 'mindfulness',
                    'exercise_type': session.technique_type,
                    'completion_status': 'completed' if session.completion_time else 'started',
                    'engagement_score': session.engagement_level,
                    'effectiveness_rating': session.effectiveness_rating,
                    'date': session.start_time,
                    'duration': session.session_duration
                })
            
            return sorted(history, key=lambda x: x['date'])
            
        except Exception as e:
            logger.error(f"Error getting exercise history: {str(e)}")
            return []

    def _analyze_mood_trends(self, patient_id: int) -> Dict:
        """Analyze mood trends from mood entries"""
        try:
            mood_entries = MoodEntry.query.filter_by(patient_id=patient_id).order_by(MoodEntry.entry_date).all()
            
            if not mood_entries:
                return {'daily_scores': [], 'trend': 'insufficient_data'}
            
            daily_scores = [entry.mood_score for entry in mood_entries]
            
            # Calculate trend
            if len(daily_scores) >= 7:
                recent_avg = sum(daily_scores[-7:]) / 7
                previous_avg = sum(daily_scores[-14:-7]) / 7 if len(daily_scores) >= 14 else daily_scores[0]
                
                if recent_avg < previous_avg:
                    trend = 'improving'
                elif recent_avg > previous_avg:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            return {
                'daily_scores': daily_scores,
                'trend': trend,
                'total_entries': len(daily_scores)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing mood trends: {str(e)}")
            return {'daily_scores': [], 'trend': 'error'}

    def _analyze_engagement_patterns(self, exercise_history: List[Dict]) -> Dict:
        """Analyze exercise engagement patterns"""
        try:
            if not exercise_history:
                return {'completion_rate': 0, 'engagement_level': 'none'}
            
            completed = sum(1 for ex in exercise_history if ex['completion_status'] == 'completed')
            completion_rate = completed / len(exercise_history)
            
            engagement_scores = [ex['engagement_score'] for ex in exercise_history if ex['engagement_score']]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
            
            if completion_rate > 0.8 and avg_engagement > 7:
                engagement_level = 'high'
            elif completion_rate > 0.5 and avg_engagement > 5:
                engagement_level = 'moderate'
            else:
                engagement_level = 'low'
            
            return {
                'completion_rate': completion_rate,
                'average_engagement': avg_engagement,
                'engagement_level': engagement_level,
                'total_sessions': len(exercise_history)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing engagement patterns: {str(e)}")
            return {'completion_rate': 0, 'engagement_level': 'error'}

    def _adapt_to_engagement(self, recommendations: Dict, engagement_patterns: Dict) -> Dict:
        """Adapt recommendations based on engagement patterns"""
        adapted_recs = recommendations.copy()
        
        completion_rate = engagement_patterns.get('completion_rate', 0)
        engagement_level = engagement_patterns.get('engagement_level', 'low')
        
        if completion_rate < 0.5:
            # Reduce difficulty and duration
            adapted_recs['difficulty_adjustment'] = 'easier'
            adapted_recs['duration_adjustment'] = 'shorter'
        elif completion_rate > 0.8 and engagement_level == 'high':
            # Offer advanced exercises
            adapted_recs['difficulty_adjustment'] = 'advanced'
            adapted_recs['duration_adjustment'] = 'longer'
        
        return adapted_recs

    def _get_patient_preferred_times(self, patient_id: int) -> Dict:
        """Get patient's preferred exercise times based on history"""
        try:
            # This would analyze when patient typically completes exercises
            # For now, return default times
            return {
                'morning': '8:00-10:00',
                'midday': '12:00-14:00',
                'evening': '18:00-20:00'
            }
        except Exception as e:
            logger.error(f"Error getting patient preferred times: {str(e)}")
            return {}

# Initialize the integration system
phq9_exercise_integration = PHQ9ExerciseIntegration()
