#!/usr/bin/env python3
"""
Patient Motivation System
Smart notifications, progress visualization, and adaptive encouragement
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
    db, Patient, ExerciseSession, MoodEntry, PHQ9Assessment
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatientMotivationSystem:
    """Comprehensive patient motivation and engagement system"""
    
    def __init__(self):
        self.notification_templates = {
            'motivational': {
                'high_engagement': [
                    "Great work! Your consistency is showing real progress. Keep it up!",
                    "You're building amazing habits! Your dedication is inspiring.",
                    "Fantastic progress! You're mastering these skills beautifully."
                ],
                'moderate_engagement': [
                    "You're doing well! Every exercise brings you closer to your goals.",
                    "Keep going! You're making steady progress on your journey.",
                    "Nice work! You're developing important skills for your wellbeing."
                ],
                'low_engagement': [
                    "Remember, even small steps count. You've got this!",
                    "It's okay to start small. Every effort matters.",
                    "You're not alone in this journey. Let's take it one step at a time."
                ]
            },
            'reminder': {
                'gentle': [
                    "Time for your daily check-in. How are you feeling today?",
                    "Ready for a quick exercise? It only takes a few minutes.",
                    "Your wellbeing matters. Take a moment for yourself."
                ],
                'concerned': [
                    "We haven't heard from you in a while. Everything okay?",
                    "Missing your exercises? We're here to support you.",
                    "Your progress is important to us. Let's get back on track."
                ],
                'urgent': [
                    "URGENT: Please check in immediately. We're concerned about your wellbeing.",
                    "CRITICAL: Your safety is our priority. Please respond now.",
                    "EMERGENCY: Immediate provider contact required."
                ]
            }
        }

    def generate_smart_notification(self, patient_id: int, notification_type: str = 'reminder') -> Dict:
        """Generate personalized smart notification for patient"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Analyze patient's current state
            current_state = self._analyze_patient_current_state(patient_id)
            
            # Generate personalized message
            message = self._generate_personalized_message(
                patient_id, notification_type, current_state
            )
            
            # Determine notification priority
            priority = self._determine_notification_priority(patient_id, current_state)
            
            return {
                'patient_id': patient_id,
                'notification_type': notification_type,
                'message': message,
                'priority': priority,
                'current_state': current_state,
                'escalation_needed': priority == 'urgent'
            }
            
        except Exception as e:
            logger.error(f"Error generating smart notification: {str(e)}")
            return {'error': f'Notification generation failed: {str(e)}'}

    def create_progress_visualization(self, patient_id: int) -> Dict:
        """Create comprehensive progress visualization for patient"""
        try:
            # Get patient data
            exercise_history = self._get_exercise_history(patient_id)
            mood_trends = self._get_mood_trends(patient_id)
            
            # Calculate progress metrics
            progress_metrics = self._calculate_progress_metrics(patient_id)
            
            # Identify milestones
            milestones = self._identify_milestones(patient_id)
            
            return {
                'exercise_progress': {
                    'completion_rate': progress_metrics['completion_rate'],
                    'engagement_trend': progress_metrics['engagement_trend'],
                    'total_sessions': len(exercise_history)
                },
                'mood_progress': {
                    'current_trend': mood_trends.get('trend', 'stable'),
                    'improvement_rate': mood_trends.get('improvement_rate', 0),
                    'recent_scores': mood_trends.get('recent_scores', [])
                },
                'milestones': milestones,
                'achievements': self._identify_achievements(patient_id)
            }
            
        except Exception as e:
            logger.error(f"Error creating progress visualization: {str(e)}")
            return {'error': f'Progress visualization failed: {str(e)}'}

    def _analyze_patient_current_state(self, patient_id: int) -> Dict:
        """Analyze patient's current state for notification personalization"""
        try:
            # Get recent activity
            recent_sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).limit(5).all()
            
            # Get current mood
            current_mood = self._get_current_mood(patient_id)
            
            # Get engagement level
            engagement_level = self._get_engagement_level(patient_id)
            
            # Calculate activity gap
            activity_gap = self._calculate_activity_gap(patient_id)
            
            return {
                'recent_activity': len(recent_sessions),
                'current_mood': current_mood,
                'engagement_level': engagement_level,
                'activity_gap_days': activity_gap,
                'needs_attention': activity_gap > 3
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patient current state: {str(e)}")
            return {}

    def _generate_personalized_message(self, patient_id: int, notification_type: str, 
                                     current_state: Dict) -> str:
        """Generate personalized message based on patient state"""
        try:
            # Get patient name
            patient = Patient.query.get(patient_id)
            patient_name = patient.first_name if patient else "there"
            
            # Select appropriate template
            if notification_type == 'motivational':
                engagement_level = current_state.get('engagement_level', 'moderate')
                templates = self.notification_templates['motivational'][engagement_level]
            elif notification_type == 'reminder':
                if current_state.get('needs_attention'):
                    templates = self.notification_templates['reminder']['concerned']
                else:
                    templates = self.notification_templates['reminder']['gentle']
            else:
                templates = self.notification_templates['reminder']['gentle']
            
            # Select random template and personalize
            import random
            base_message = random.choice(templates)
            
            # Personalize message
            personalized_message = base_message.replace("you", patient_name.lower())
            
            return personalized_message
            
        except Exception as e:
            logger.error(f"Error generating personalized message: {str(e)}")
            return "Time for your daily check-in. How are you feeling today?"

    def _determine_notification_priority(self, patient_id: int, current_state: Dict) -> str:
        """Determine notification priority based on patient state"""
        try:
            # Check for long activity gap
            if current_state.get('activity_gap_days', 0) > 5:
                return 'high'
            
            # Check for low mood
            if current_state.get('current_mood', 5) <= 3:
                return 'high'
            
            # Check for declining engagement
            if current_state.get('engagement_level') == 'low':
                return 'medium'
            
            return 'normal'
            
        except Exception as e:
            logger.error(f"Error determining notification priority: {str(e)}")
            return 'normal'

    def _get_exercise_history(self, patient_id: int) -> List[Dict]:
        """Get patient's exercise history for progress analysis"""
        try:
            sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(ExerciseSession.start_time).all()
            
            history = []
            for session in sessions:
                history.append({
                    'date': session.start_time.date(),
                    'exercise_type': session.exercise.type,
                    'completion_status': session.completion_status,
                    'engagement_score': session.engagement_score
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting exercise history: {str(e)}")
            return []

    def _get_mood_trends(self, patient_id: int) -> Dict:
        """Get patient's mood trends for progress analysis"""
        try:
            mood_entries = MoodEntry.query.filter_by(patient_id=patient_id)\
                .order_by(MoodEntry.entry_date).all()
            
            if not mood_entries:
                return {'trend': 'insufficient_data', 'improvement_rate': 0}
            
            scores = [entry.mood_score for entry in mood_entries]
            
            # Calculate trend
            if len(scores) >= 7:
                recent_avg = sum(scores[-7:]) / 7
                previous_avg = sum(scores[-14:-7]) / 7 if len(scores) >= 14 else scores[0]
                
                if recent_avg < previous_avg:
                    trend = 'improving'
                    improvement_rate = (previous_avg - recent_avg) / previous_avg * 100
                elif recent_avg > previous_avg:
                    trend = 'declining'
                    improvement_rate = (recent_avg - previous_avg) / previous_avg * 100
                else:
                    trend = 'stable'
                    improvement_rate = 0
            else:
                trend = 'insufficient_data'
                improvement_rate = 0
            
            return {
                'trend': trend,
                'improvement_rate': improvement_rate,
                'recent_scores': scores[-7:] if len(scores) >= 7 else scores
            }
            
        except Exception as e:
            logger.error(f"Error getting mood trends: {str(e)}")
            return {'trend': 'error', 'improvement_rate': 0}

    def _calculate_progress_metrics(self, patient_id: int) -> Dict:
        """Calculate comprehensive progress metrics"""
        try:
            sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).limit(30).all()
            
            if not sessions:
                return {
                    'completion_rate': 0,
                    'engagement_trend': 'insufficient_data'
                }
            
            # Calculate completion rate
            completed = sum(1 for s in sessions if s.completion_status == 'completed')
            completion_rate = completed / len(sessions)
            
            # Calculate engagement trend
            if len(sessions) >= 10:
                recent_sessions = sessions[:5]
                older_sessions = sessions[5:10]
                
                recent_avg = sum(s.engagement_score for s in recent_sessions if s.engagement_score) / len(recent_sessions)
                older_avg = sum(s.engagement_score for s in older_sessions if s.engagement_score) / len(older_sessions)
                
                if recent_avg > older_avg:
                    engagement_trend = 'improving'
                elif recent_avg < older_avg:
                    engagement_trend = 'declining'
                else:
                    engagement_trend = 'stable'
            else:
                engagement_trend = 'insufficient_data'
            
            return {
                'completion_rate': completion_rate,
                'engagement_trend': engagement_trend
            }
            
        except Exception as e:
            logger.error(f"Error calculating progress metrics: {str(e)}")
            return {'completion_rate': 0, 'engagement_trend': 'error'}

    def _identify_milestones(self, patient_id: int) -> List[Dict]:
        """Identify patient milestones and achievements"""
        try:
            milestones = []
            
            # Get exercise history
            sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(ExerciseSession.start_time).all()
            
            # Check for consecutive days
            if len(sessions) >= 7:
                consecutive_days = self._calculate_consecutive_days(sessions)
                if consecutive_days >= 7:
                    milestones.append({
                        'type': 'consecutive_days',
                        'value': consecutive_days,
                        'description': f"{consecutive_days} consecutive days of exercises",
                        'achieved': True
                    })
            
            # Check for total sessions
            total_sessions = len(sessions)
            if total_sessions >= 10:
                milestones.append({
                    'type': 'total_sessions',
                    'value': total_sessions,
                    'description': f"{total_sessions} total exercise sessions",
                    'achieved': True
                })
            
            return milestones
            
        except Exception as e:
            logger.error(f"Error identifying milestones: {str(e)}")
            return []

    def _identify_achievements(self, patient_id: int) -> List[Dict]:
        """Identify specific achievements for patient"""
        try:
            achievements = []
            
            # Get progress metrics
            progress_metrics = self._calculate_progress_metrics(patient_id)
            
            # Consistency achievements
            if progress_metrics.get('completion_rate', 0) >= 0.8:
                achievements.append({
                    'type': 'high_completion',
                    'title': 'Consistency Champion',
                    'description': 'Maintained 80%+ completion rate',
                    'icon': '🏆'
                })
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error identifying achievements: {str(e)}")
            return []

    def _get_current_mood(self, patient_id: int) -> int:
        """Get patient's current mood score"""
        try:
            recent_mood = MoodEntry.query.filter_by(patient_id=patient_id)\
                .order_by(desc(MoodEntry.entry_date)).first()
            
            return recent_mood.mood_score if recent_mood else 5
            
        except Exception as e:
            logger.error(f"Error getting current mood: {str(e)}")
            return 5

    def _get_engagement_level(self, patient_id: int) -> str:
        """Get patient's current engagement level"""
        try:
            recent_sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).limit(10).all()
            
            if not recent_sessions:
                return 'none'
            
            # Calculate engagement metrics
            completion_rate = sum(1 for s in recent_sessions if s.completion_status == 'completed') / len(recent_sessions)
            avg_engagement = sum(s.engagement_score for s in recent_sessions if s.engagement_score) / len(recent_sessions)
            
            if completion_rate > 0.8 and avg_engagement > 7:
                return 'high'
            elif completion_rate > 0.5 and avg_engagement > 5:
                return 'moderate'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error getting engagement level: {str(e)}")
            return 'unknown'

    def _calculate_activity_gap(self, patient_id: int) -> int:
        """Calculate days since last activity"""
        try:
            # Get last exercise session
            last_session = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).first()
            
            # Get last mood entry
            last_mood = MoodEntry.query.filter_by(patient_id=patient_id)\
                .order_by(desc(MoodEntry.entry_date)).first()
            
            # Calculate gaps
            session_gap = (datetime.now() - last_session.start_time).days if last_session else 999
            mood_gap = (datetime.now() - last_mood.entry_date).days if last_mood else 999
            
            return min(session_gap, mood_gap)
            
        except Exception as e:
            logger.error(f"Error calculating activity gap: {str(e)}")
            return 999

    def _calculate_consecutive_days(self, sessions: List[ExerciseSession]) -> int:
        """Calculate consecutive days of exercise completion"""
        try:
            if not sessions:
                return 0
            
            # Get unique dates with completed sessions
            completed_dates = set()
            for session in sessions:
                if session.completion_status == 'completed':
                    completed_dates.add(session.start_time.date())
            
            if not completed_dates:
                return 0
            
            # Sort dates
            sorted_dates = sorted(completed_dates, reverse=True)
            
            # Count consecutive days
            consecutive = 1
            for i in range(1, len(sorted_dates)):
                if (sorted_dates[i-1] - sorted_dates[i]).days == 1:
                    consecutive += 1
                else:
                    break
            
            return consecutive
            
        except Exception as e:
            logger.error(f"Error calculating consecutive days: {str(e)}")
            return 0

# Initialize the motivation system
patient_motivation_system = PatientMotivationSystem()
