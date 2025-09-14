#!/usr/bin/env python3
"""
Intelligent Notification and Reminder System
Adaptive timing, escalation protocols, and motivational messaging for PHQ-9 exercise integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
import random
from sqlalchemy import and_, func, desc, extract
from sqlalchemy.orm import joinedload

from app_ml_complete import (
    db, Patient, ExerciseSession, MoodEntry, PHQ9Assessment, 
    NotificationSettings, EngagementMetrics
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentNotificationSystem:
    """Comprehensive intelligent notification and reminder system"""
    
    def __init__(self):
        self.escalation_levels = {
            'gentle': {'days_missed': 1, 'tone': 'supportive', 'frequency': 'normal'},
            'concerned': {'days_missed': 2, 'tone': 'caring', 'frequency': 'increased'},
            'urgent': {'days_missed': 3, 'tone': 'urgent', 'frequency': 'high'},
            'crisis': {'days_missed': 5, 'tone': 'emergency', 'frequency': 'immediate'}
        }
        
        self.motivational_messages = {
            'milestone_achievements': [
                "🎉 Congratulations! You've completed {count} exercises in a row. Your consistency is amazing!",
                "🌟 Fantastic work! You've reached {milestone}. You're building incredible habits!",
                "🏆 Outstanding! {achievement} shows your dedication to your wellbeing.",
                "💪 You're doing it! {milestone} proves your strength and commitment."
            ],
            'progress_celebrations': [
                "📈 Great news! Your mood has improved by {improvement}% this week. Keep it up!",
                "✨ You're making real progress! Your PHQ-9 score has improved by {points} points.",
                "🎯 Excellent work! You're {percentage} closer to your wellness goals.",
                "🌟 Your dedication is paying off! You've completed {percentage}% of your exercises this week."
            ],
            'educational_content': [
                "💡 Did you know? Regular exercise can improve mood by releasing endorphins, your brain's natural feel-good chemicals.",
                "🧠 Research shows that consistent behavioral activation can reduce depression symptoms by up to 50%.",
                "🌱 Mindfulness exercises can help rewire your brain to better handle stress and negative thoughts.",
                "🎯 Setting small, achievable goals each day builds momentum and confidence over time."
            ],
            'phq9_connections': [
                "📊 Your exercise completion is directly linked to PHQ-9 improvements. Every session counts!",
                "🎯 Each exercise you complete brings you closer to better PHQ-9 scores and improved wellbeing.",
                "📈 Patients who maintain 80%+ exercise completion see 3x faster PHQ-9 score improvements.",
                "🌟 Your consistent effort is the key to measurable progress in your depression treatment."
            ]
        }
        
        self.adaptive_timing_config = {
            'learning_period_days': 14,
            'min_notification_interval_hours': 2,
            'max_notification_interval_hours': 12,
            'busy_period_buffer_hours': 2,
            'optimal_completion_windows': {
                'morning': {'start': 8, 'end': 10, 'weight': 0.3},
                'midday': {'start': 12, 'end': 14, 'weight': 0.2},
                'evening': {'start': 18, 'end': 20, 'weight': 0.4},
                'flexible': {'start': 9, 'end': 21, 'weight': 0.1}
            }
        }

    def generate_adaptive_notification(self, patient_id: int) -> Dict:
        """Generate adaptive notification based on patient patterns and current state"""
        try:
            # Analyze patient patterns
            patterns = self._analyze_patient_patterns(patient_id)
            
            # Determine optimal timing
            optimal_timing = self._calculate_optimal_timing(patient_id, patterns)
            
            # Check escalation needs
            escalation_level = self._determine_escalation_level(patient_id)
            
            # Generate appropriate message
            message = self._generate_adaptive_message(patient_id, escalation_level, patterns)
            
            # Calculate notification priority
            priority = self._calculate_notification_priority(patient_id, escalation_level, patterns)
            
            return {
                'patient_id': patient_id,
                'message': message,
                'optimal_timing': optimal_timing,
                'escalation_level': escalation_level,
                'priority': priority,
                'patterns': patterns,
                'provider_alert_needed': escalation_level in ['urgent', 'crisis']
            }
            
        except Exception as e:
            logger.error(f"Error generating adaptive notification: {str(e)}")
            return {'error': f'Notification generation failed: {str(e)}'}

    def _analyze_patient_patterns(self, patient_id: int) -> Dict:
        """Analyze patient's exercise completion patterns and optimal times"""
        try:
            # Get recent exercise sessions
            sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time))\
                .limit(30).all()
            
            if not sessions:
                return {'optimal_times': [], 'busy_periods': [], 'completion_rate': 0}
            
            # Analyze completion times
            completion_times = []
            missed_periods = []
            
            for session in sessions:
                if session.completion_status == 'completed':
                    completion_times.append(session.start_time.hour)
                else:
                    missed_periods.append(session.start_time.hour)
            
            # Find optimal completion hours
            optimal_hours = self._find_optimal_hours(completion_times)
            
            # Identify busy periods (low completion rates)
            busy_hours = self._identify_busy_hours(missed_periods, completion_times)
            
            # Calculate completion rate
            completion_rate = len([s for s in sessions if s.completion_status == 'completed']) / len(sessions)
            
            return {
                'optimal_times': optimal_hours,
                'busy_periods': busy_hours,
                'completion_rate': completion_rate,
                'total_sessions': len(sessions),
                'recent_activity': self._get_recent_activity_level(patient_id)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patient patterns: {str(e)}")
            return {'optimal_times': [], 'busy_periods': [], 'completion_rate': 0}

    def _find_optimal_hours(self, completion_times: List[int]) -> List[int]:
        """Find hours when patient is most likely to complete exercises"""
        try:
            if not completion_times:
                return [9, 12, 18]  # Default optimal times
            
            # Count completions by hour
            hour_counts = {}
            for hour in completion_times:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            # Find hours with highest completion rates
            sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Return top 3 optimal hours
            optimal_hours = [hour for hour, count in sorted_hours[:3]]
            
            return optimal_hours
            
        except Exception as e:
            logger.error(f"Error finding optimal hours: {str(e)}")
            return [9, 12, 18]

    def _identify_busy_hours(self, missed_periods: List[int], completion_times: List[int]) -> List[int]:
        """Identify hours when patient is typically busy"""
        try:
            if not missed_periods:
                return []
            
            # Count missed sessions by hour
            missed_counts = {}
            for hour in missed_periods:
                missed_counts[hour] = missed_counts.get(hour, 0) + 1
            
            # Find hours with high miss rates
            busy_hours = []
            for hour, count in missed_counts.items():
                completion_count = completion_times.count(hour)
                total_attempts = count + completion_count
                if total_attempts > 0 and count / total_attempts > 0.7:  # 70% miss rate
                    busy_hours.append(hour)
            
            return busy_hours
            
        except Exception as e:
            logger.error(f"Error identifying busy hours: {str(e)}")
            return []

    def _calculate_optimal_timing(self, patient_id: int, patterns: Dict) -> Dict:
        """Calculate optimal timing for next notification"""
        try:
            current_time = datetime.now()
            optimal_hours = patterns.get('optimal_times', [9, 12, 18])
            busy_hours = patterns.get('busy_hours', [])
            
            # Find next optimal time
            next_optimal_time = None
            for hour in optimal_hours:
                candidate_time = current_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                if candidate_time > current_time:
                    next_optimal_time = candidate_time
                    break
            
            # If no optimal time today, use tomorrow
            if not next_optimal_time:
                tomorrow = current_time + timedelta(days=1)
                next_optimal_time = tomorrow.replace(hour=optimal_hours[0], minute=0, second=0, microsecond=0)
            
            # Avoid busy periods
            while next_optimal_time.hour in busy_hours:
                next_optimal_time += timedelta(hours=1)
            
            # Calculate delay until optimal time
            delay_hours = (next_optimal_time - current_time).total_seconds() / 3600
            
            return {
                'next_optimal_time': next_optimal_time,
                'delay_hours': delay_hours,
                'optimal_hours': optimal_hours,
                'busy_hours': busy_hours
            }
            
        except Exception as e:
            logger.error(f"Error calculating optimal timing: {str(e)}")
            return {'next_optimal_time': datetime.now() + timedelta(hours=2), 'delay_hours': 2}

    def _determine_escalation_level(self, patient_id: int) -> str:
        """Determine escalation level based on missed exercises and risk factors"""
        try:
            # Get recent exercise sessions
            recent_sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time))\
                .limit(10).all()
            
            if not recent_sessions:
                return 'gentle'
            
            # Calculate days since last completion
            last_completed = None
            for session in recent_sessions:
                if session.completion_status == 'completed':
                    last_completed = session.start_time
                    break
            
            if not last_completed:
                days_missed = 10  # Assume long gap if no completions
            else:
                days_missed = (datetime.now() - last_completed).days
            
            # Check PHQ-9 severity for additional risk
            patient = Patient.query.get(patient_id)
            if patient:
                recent_phq9 = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                    .order_by(desc(PHQ9Assessment.assessment_date)).first()
                
                if recent_phq9 and recent_phq9.total_score >= 15:  # Moderately severe or worse
                    days_missed += 1  # Escalate faster for high-risk patients
            
            # Determine escalation level
            if days_missed >= 5:
                return 'crisis'
            elif days_missed >= 3:
                return 'urgent'
            elif days_missed >= 2:
                return 'concerned'
            else:
                return 'gentle'
                
        except Exception as e:
            logger.error(f"Error determining escalation level: {str(e)}")
            return 'gentle'

    def _generate_adaptive_message(self, patient_id: int, escalation_level: str, patterns: Dict) -> str:
        """Generate adaptive message based on escalation level and patterns"""
        try:
            patient = Patient.query.get(patient_id)
            patient_name = patient.first_name if patient else "there"
            
            # Get recent progress
            progress_data = self._get_recent_progress(patient_id)
            
            # Select message template based on escalation level
            if escalation_level == 'crisis':
                return self._generate_crisis_message(patient_name, progress_data)
            elif escalation_level == 'urgent':
                return self._generate_urgent_message(patient_name, progress_data)
            elif escalation_level == 'concerned':
                return self._generate_concerned_message(patient_name, progress_data)
            else:
                return self._generate_motivational_message(patient_name, patterns, progress_data)
                
        except Exception as e:
            logger.error(f"Error generating adaptive message: {str(e)}")
            return "Time for your daily check-in. How are you feeling today?"

    def _generate_crisis_message(self, patient_name: str, progress_data: Dict) -> str:
        """Generate crisis-level message"""
        crisis_messages = [
            f"🚨 {patient_name}, we're very concerned about your wellbeing. Please check in immediately.",
            f"⚠️ URGENT: {patient_name}, your safety is our priority. Please respond now.",
            f"🆘 CRITICAL: {patient_name}, immediate provider contact required. Please call your provider now."
        ]
        return random.choice(crisis_messages)

    def _generate_urgent_message(self, patient_name: str, progress_data: Dict) -> str:
        """Generate urgent-level message"""
        urgent_messages = [
            f"⚠️ {patient_name}, we haven't heard from you in several days. Everything okay?",
            f"🔔 {patient_name}, your exercises are important for your treatment. Please check in soon.",
            f"📞 {patient_name}, we're concerned about your progress. Please reach out to your provider."
        ]
        return random.choice(urgent_messages)

    def _generate_concerned_message(self, patient_name: str, progress_data: Dict) -> str:
        """Generate concerned-level message"""
        concerned_messages = [
            f"🤔 {patient_name}, we noticed you've missed a few exercises. How are you doing?",
            f"💭 {patient_name}, your progress matters to us. Ready to get back on track?",
            f"🌟 {patient_name}, even small steps count. Let's take it one day at a time."
        ]
        return random.choice(concerned_messages)

    def _generate_motivational_message(self, patient_name: str, patterns: Dict, progress_data: Dict) -> str:
        """Generate motivational message with educational content"""
        try:
            # Select message type based on progress and patterns
            completion_rate = patterns.get('completion_rate', 0)
            
            if completion_rate > 0.8:
                # High engagement - celebrate progress
                if progress_data.get('mood_improvement', 0) > 0:
                    return random.choice(self.motivational_messages['progress_celebrations']).format(
                        improvement=abs(progress_data['mood_improvement']),
                        percentage=round(completion_rate * 100)
                    )
                else:
                    return random.choice(self.motivational_messages['milestone_achievements']).format(
                        count=progress_data.get('consecutive_days', 0),
                        milestone=f"{round(completion_rate * 100)}% completion rate",
                        achievement="maintaining high engagement"
                    )
            elif completion_rate > 0.5:
                # Moderate engagement - encourage consistency
                return random.choice(self.motivational_messages['phq9_connections'])
            else:
                # Low engagement - educational content
                return random.choice(self.motivational_messages['educational_content'])
                
        except Exception as e:
            logger.error(f"Error generating motivational message: {str(e)}")
            return f"Hi {patient_name}, time for your daily check-in. How are you feeling today?"

    def _get_recent_progress(self, patient_id: int) -> Dict:
        """Get recent progress data for message personalization"""
        try:
            # Get recent mood entries
            recent_moods = MoodEntry.query.filter_by(patient_id=patient_id)\
                .order_by(desc(MoodEntry.entry_date))\
                .limit(14).all()
            
            # Get recent exercise sessions
            recent_sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time))\
                .limit(14).all()
            
            # Calculate mood improvement
            mood_improvement = 0
            if len(recent_moods) >= 7:
                recent_avg = sum(m.mood_score for m in recent_moods[:7]) / 7
                previous_avg = sum(m.mood_score for m in recent_moods[7:14]) / 7 if len(recent_moods) >= 14 else recent_avg
                mood_improvement = recent_avg - previous_avg
            
            # Calculate consecutive days
            consecutive_days = 0
            if recent_sessions:
                completed_dates = set()
                for session in recent_sessions:
                    if session.completion_status == 'completed':
                        completed_dates.add(session.start_time.date())
                
                if completed_dates:
                    sorted_dates = sorted(completed_dates, reverse=True)
                    consecutive_days = 1
                    for i in range(1, len(sorted_dates)):
                        if (sorted_dates[i-1] - sorted_dates[i]).days == 1:
                            consecutive_days += 1
                        else:
                            break
            
            return {
                'mood_improvement': mood_improvement,
                'consecutive_days': consecutive_days,
                'recent_completion_rate': len([s for s in recent_sessions if s.completion_status == 'completed']) / len(recent_sessions) if recent_sessions else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting recent progress: {str(e)}")
            return {'mood_improvement': 0, 'consecutive_days': 0, 'recent_completion_rate': 0}

    def _calculate_notification_priority(self, patient_id: int, escalation_level: str, patterns: Dict) -> str:
        """Calculate notification priority based on multiple factors"""
        try:
            # Base priority from escalation level
            priority_map = {
                'crisis': 'critical',
                'urgent': 'high',
                'concerned': 'medium',
                'gentle': 'normal'
            }
            base_priority = priority_map.get(escalation_level, 'normal')
            
            # Adjust based on PHQ-9 severity
            patient = Patient.query.get(patient_id)
            if patient:
                recent_phq9 = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                    .order_by(desc(PHQ9Assessment.assessment_date)).first()
                
                if recent_phq9:
                    if recent_phq9.total_score >= 20:  # Severe depression
                        if base_priority != 'critical':
                            base_priority = 'high'
                    elif recent_phq9.total_score >= 15:  # Moderately severe
                        if base_priority == 'normal':
                            base_priority = 'medium'
            
            # Adjust based on completion rate
            completion_rate = patterns.get('completion_rate', 0)
            if completion_rate < 0.3 and base_priority == 'normal':
                base_priority = 'medium'
            
            return base_priority
            
        except Exception as e:
            logger.error(f"Error calculating notification priority: {str(e)}")
            return 'normal'

    def _get_recent_activity_level(self, patient_id: int) -> str:
        """Get patient's recent activity level"""
        try:
            # Get last 7 days of activity
            week_ago = datetime.now() - timedelta(days=7)
            recent_sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .filter(ExerciseSession.start_time >= week_ago)\
                .all()
            
            if not recent_sessions:
                return 'none'
            
            completed_sessions = [s for s in recent_sessions if s.completion_status == 'completed']
            completion_rate = len(completed_sessions) / len(recent_sessions)
            
            if completion_rate > 0.8:
                return 'high'
            elif completion_rate > 0.5:
                return 'moderate'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error getting recent activity level: {str(e)}")
            return 'unknown'

    def trigger_provider_alert(self, patient_id: int, escalation_level: str, reason: str) -> Dict:
        """Trigger provider alert for escalation situations"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            alert_data = {
                'patient_id': patient_id,
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'escalation_level': escalation_level,
                'reason': reason,
                'timestamp': datetime.now(),
                'requires_immediate_action': escalation_level in ['urgent', 'crisis']
            }
            
            # Log the alert (in a real system, this would send to provider dashboard)
            logger.warning(f"PROVIDER ALERT: {alert_data}")
            
            return {
                'alert_triggered': True,
                'alert_data': alert_data,
                'message': f"Provider alert triggered for {patient.first_name} {patient.last_name}"
            }
            
        except Exception as e:
            logger.error(f"Error triggering provider alert: {str(e)}")
            return {'error': f'Provider alert failed: {str(e)}'}

    def update_notification_settings(self, patient_id: int, settings: Dict) -> Dict:
        """Update patient's notification settings"""
        try:
            notification_settings = NotificationSettings.query.filter_by(patient_id=patient_id).first()
            
            if not notification_settings:
                notification_settings = NotificationSettings(patient_id=patient_id)
                db.session.add(notification_settings)
            
            # Update settings
            for key, value in settings.items():
                if hasattr(notification_settings, key):
                    setattr(notification_settings, key, value)
            
            notification_settings.updated_at = datetime.now()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Notification settings updated successfully',
                'settings': settings
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating notification settings: {str(e)}")
            return {'error': f'Settings update failed: {str(e)}'}

    def get_notification_analytics(self, patient_id: int) -> Dict:
        """Get analytics about notification effectiveness"""
        try:
            # Get notification settings
            settings = NotificationSettings.query.filter_by(patient_id=patient_id).first()
            
            # Get engagement metrics
            engagement = EngagementMetrics.query.filter_by(patient_id=patient_id).first()
            
            # Get recent patterns
            patterns = self._analyze_patient_patterns(patient_id)
            
            return {
                'notification_settings': {
                    'frequency_type': settings.frequency_type if settings else 'adaptive',
                    'min_interval_hours': settings.min_interval_hours if settings else 2,
                    'max_interval_hours': settings.max_interval_hours if settings else 8
                },
                'engagement_metrics': {
                    'completion_rate': engagement.completion_rate if engagement else 0,
                    'current_streak': engagement.current_streak_days if engagement else 0,
                    'longest_streak': engagement.longest_streak_days if engagement else 0
                },
                'patterns': patterns,
                'recommendations': self._generate_notification_recommendations(patient_id, patterns)
            }
            
        except Exception as e:
            logger.error(f"Error getting notification analytics: {str(e)}")
            return {'error': f'Analytics failed: {str(e)}'}

    def _generate_notification_recommendations(self, patient_id: int, patterns: Dict) -> List[str]:
        """Generate recommendations for improving notification effectiveness"""
        try:
            recommendations = []
            completion_rate = patterns.get('completion_rate', 0)
            
            if completion_rate < 0.5:
                recommendations.append("Consider increasing notification frequency during optimal hours")
                recommendations.append("Add more motivational content to encourage engagement")
            
            if not patterns.get('optimal_times'):
                recommendations.append("Continue monitoring to identify optimal notification times")
            
            if patterns.get('busy_periods'):
                recommendations.append(f"Avoid notifications during hours: {patterns['busy_periods']}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

# Initialize the intelligent notification system
intelligent_notification_system = IntelligentNotificationSystem()
