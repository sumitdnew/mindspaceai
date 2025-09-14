#!/usr/bin/env python3
"""
Intelligent Notification Integration System
Comprehensive integration of adaptive notifications with PHQ-9 exercise system
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
    db, Patient, ExerciseSession, MoodEntry, PHQ9Assessment, 
    NotificationSettings, EngagementMetrics
)
from intelligent_notification_system import intelligent_notification_system
from notification_scheduler import notification_scheduler
from patient_motivation_system import patient_motivation_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentNotificationIntegration:
    """Comprehensive integration system for intelligent notifications"""
    
    def __init__(self):
        self.integration_config = {
            'auto_schedule_enabled': True,
            'provider_alert_threshold': 3,  # days missed
            'crisis_escalation_threshold': 5,  # days missed
            'mood_trend_analysis_days': 7,
            'engagement_analysis_days': 14,
            'notification_effectiveness_tracking': True
        }

    def process_patient_notification_cycle(self, patient_id: int) -> Dict:
        """Complete notification cycle for a patient"""
        try:
            # Step 1: Analyze current patient state
            patient_state = self._analyze_patient_state(patient_id)
            
            # Step 2: Generate adaptive notification
            notification = intelligent_notification_system.generate_adaptive_notification(patient_id)
            
            # Step 3: Schedule notification
            schedule_result = notification_scheduler.schedule_patient_notifications(patient_id)
            
            # Step 4: Update engagement metrics
            self._update_engagement_metrics(patient_id, notification)
            
            # Step 5: Check for provider alerts
            provider_alerts = self._check_provider_alert_requirements(patient_id, patient_state)
            
            return {
                'patient_id': patient_id,
                'patient_state': patient_state,
                'notification': notification,
                'schedule_result': schedule_result,
                'provider_alerts': provider_alerts,
                'cycle_completed': True
            }
            
        except Exception as e:
            logger.error(f"Error in notification cycle: {str(e)}")
            return {'error': f'Notification cycle failed: {str(e)}'}

    def _analyze_patient_state(self, patient_id: int) -> Dict:
        """Comprehensive analysis of patient's current state"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Get recent PHQ-9 assessment
            recent_phq9 = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                .order_by(desc(PHQ9Assessment.assessment_date)).first()
            
            # Get recent exercise sessions
            recent_sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time))\
                .limit(30).all()
            
            # Get recent mood entries
            recent_moods = MoodEntry.query.filter_by(patient_id=patient_id)\
                .order_by(desc(MoodEntry.entry_date))\
                .limit(14).all()
            
            # Calculate key metrics
            completion_rate = self._calculate_completion_rate(recent_sessions)
            mood_trend = self._calculate_mood_trend(recent_moods)
            engagement_level = self._calculate_engagement_level(recent_sessions)
            risk_level = self._calculate_risk_level(recent_phq9, recent_sessions, recent_moods)
            
            return {
                'patient_info': {
                    'id': patient_id,
                    'name': f"{patient.first_name} {patient.last_name}",
                    'severity_level': recent_phq9.severity_level if recent_phq9 else 'unknown'
                },
                'metrics': {
                    'completion_rate': completion_rate,
                    'mood_trend': mood_trend,
                    'engagement_level': engagement_level,
                    'risk_level': risk_level
                },
                'recent_activity': {
                    'last_exercise': recent_sessions[0].start_time if recent_sessions else None,
                    'last_mood_entry': recent_moods[0].entry_date if recent_moods else None,
                    'days_since_last_activity': self._calculate_days_since_activity(recent_sessions, recent_moods)
                },
                'phq9_data': {
                    'total_score': recent_phq9.total_score if recent_phq9 else None,
                    'assessment_date': recent_phq9.assessment_date if recent_phq9 else None,
                    'severity': recent_phq9.severity_level if recent_phq9 else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patient state: {str(e)}")
            return {'error': f'Patient state analysis failed: {str(e)}'}

    def _calculate_completion_rate(self, sessions: List[ExerciseSession]) -> float:
        """Calculate exercise completion rate"""
        try:
            if not sessions:
                return 0.0
            
            completed = sum(1 for s in sessions if s.completion_status == 'completed')
            return completed / len(sessions)
            
        except Exception as e:
            logger.error(f"Error calculating completion rate: {str(e)}")
            return 0.0

    def _calculate_mood_trend(self, mood_entries: List[MoodEntry]) -> Dict:
        """Calculate mood trend over time"""
        try:
            if len(mood_entries) < 7:
                return {'trend': 'insufficient_data', 'change': 0}
            
            # Calculate recent vs previous week average
            recent_scores = [m.mood_score for m in mood_entries[:7]]
            previous_scores = [m.mood_score for m in mood_entries[7:14]] if len(mood_entries) >= 14 else recent_scores
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            previous_avg = sum(previous_scores) / len(previous_scores)
            
            change = recent_avg - previous_avg
            
            if change > 0.5:
                trend = 'improving'
            elif change < -0.5:
                trend = 'declining'
            else:
                trend = 'stable'
            
            return {
                'trend': trend,
                'change': change,
                'recent_avg': recent_avg,
                'previous_avg': previous_avg
            }
            
        except Exception as e:
            logger.error(f"Error calculating mood trend: {str(e)}")
            return {'trend': 'error', 'change': 0}

    def _calculate_engagement_level(self, sessions: List[ExerciseSession]) -> str:
        """Calculate patient engagement level"""
        try:
            if not sessions:
                return 'none'
            
            # Calculate engagement metrics
            completion_rate = self._calculate_completion_rate(sessions)
            avg_engagement = sum(s.engagement_score for s in sessions if s.engagement_score) / len(sessions)
            
            if completion_rate > 0.8 and avg_engagement > 7:
                return 'high'
            elif completion_rate > 0.5 and avg_engagement > 5:
                return 'moderate'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error calculating engagement level: {str(e)}")
            return 'unknown'

    def _calculate_risk_level(self, phq9: PHQ9Assessment, sessions: List[ExerciseSession], 
                            moods: List[MoodEntry]) -> str:
        """Calculate patient risk level"""
        try:
            risk_score = 0
            
            # PHQ-9 severity risk
            if phq9:
                if phq9.total_score >= 20:
                    risk_score += 3
                elif phq9.total_score >= 15:
                    risk_score += 2
                elif phq9.total_score >= 10:
                    risk_score += 1
            
            # Activity gap risk
            days_since_activity = self._calculate_days_since_activity(sessions, moods)
            if days_since_activity >= 5:
                risk_score += 3
            elif days_since_activity >= 3:
                risk_score += 2
            elif days_since_activity >= 1:
                risk_score += 1
            
            # Mood decline risk
            if moods:
                recent_mood = moods[0].mood_score
                if recent_mood <= 3:
                    risk_score += 2
                elif recent_mood <= 5:
                    risk_score += 1
            
            # Determine risk level
            if risk_score >= 5:
                return 'high'
            elif risk_score >= 3:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error calculating risk level: {str(e)}")
            return 'unknown'

    def _calculate_days_since_activity(self, sessions: List[ExerciseSession], 
                                     moods: List[MoodEntry]) -> int:
        """Calculate days since last activity"""
        try:
            last_activity = None
            
            # Check last exercise session
            if sessions:
                last_activity = sessions[0].start_time
            
            # Check last mood entry
            if moods:
                mood_time = moods[0].entry_date
                if not last_activity or mood_time > last_activity:
                    last_activity = mood_time
            
            if not last_activity:
                return 999  # No activity recorded
            
            return (datetime.now() - last_activity).days
            
        except Exception as e:
            logger.error(f"Error calculating days since activity: {str(e)}")
            return 999

    def _update_engagement_metrics(self, patient_id: int, notification: Dict):
        """Update engagement metrics based on notification"""
        try:
            engagement = EngagementMetrics.query.filter_by(patient_id=patient_id).first()
            
            if not engagement:
                engagement = EngagementMetrics(patient_id=patient_id)
                db.session.add(engagement)
            
            # Update metrics based on notification data
            if 'patterns' in notification:
                patterns = notification['patterns']
                engagement.completion_rate = patterns.get('completion_rate', 0)
            
            # Update last check-in
            engagement.last_check_in_date = datetime.now()
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating engagement metrics: {str(e)}")
            db.session.rollback()

    def _check_provider_alert_requirements(self, patient_id: int, patient_state: Dict) -> List[Dict]:
        """Check if provider alerts are required"""
        try:
            alerts = []
            
            # Check for high risk level
            if patient_state.get('metrics', {}).get('risk_level') == 'high':
                alerts.append({
                    'type': 'high_risk',
                    'reason': 'Patient identified as high risk',
                    'priority': 'high'
                })
            
            # Check for long activity gap
            days_since_activity = patient_state.get('recent_activity', {}).get('days_since_last_activity', 0)
            if days_since_activity >= self.integration_config['crisis_escalation_threshold']:
                alerts.append({
                    'type': 'crisis_escalation',
                    'reason': f'Patient inactive for {days_since_activity} days',
                    'priority': 'critical'
                })
            elif days_since_activity >= self.integration_config['provider_alert_threshold']:
                alerts.append({
                    'type': 'provider_alert',
                    'reason': f'Patient inactive for {days_since_activity} days',
                    'priority': 'medium'
                })
            
            # Check for mood decline
            mood_trend = patient_state.get('metrics', {}).get('mood_trend', {})
            if mood_trend.get('trend') == 'declining' and mood_trend.get('change', 0) < -1:
                alerts.append({
                    'type': 'mood_decline',
                    'reason': 'Significant mood decline detected',
                    'priority': 'medium'
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking provider alert requirements: {str(e)}")
            return []

    def get_comprehensive_notification_report(self, patient_id: int) -> Dict:
        """Get comprehensive notification report for patient"""
        try:
            # Get patient state
            patient_state = self._analyze_patient_state(patient_id)
            
            # Get notification analytics
            analytics = intelligent_notification_system.get_notification_analytics(patient_id)
            
            # Get scheduled notifications
            scheduled = notification_scheduler.get_scheduled_notifications(patient_id)
            
            # Get provider alerts
            alerts = notification_scheduler.get_provider_alerts()
            patient_alerts = [alert for alert in alerts if alert['patient_id'] == patient_id]
            
            # Get motivation system data
            motivation_data = patient_motivation_system.create_progress_visualization(patient_id)
            
            return {
                'patient_state': patient_state,
                'notification_analytics': analytics,
                'scheduled_notifications': scheduled,
                'provider_alerts': patient_alerts,
                'motivation_data': motivation_data,
                'recommendations': self._generate_integration_recommendations(patient_id, patient_state)
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive report: {str(e)}")
            return {'error': f'Report generation failed: {str(e)}'}

    def _generate_integration_recommendations(self, patient_id: int, patient_state: Dict) -> List[str]:
        """Generate recommendations based on patient state"""
        try:
            recommendations = []
            
            # Get metrics
            metrics = patient_state.get('metrics', {})
            completion_rate = metrics.get('completion_rate', 0)
            engagement_level = metrics.get('engagement_level', 'unknown')
            risk_level = metrics.get('risk_level', 'unknown')
            
            # Completion rate recommendations
            if completion_rate < 0.5:
                recommendations.append("Consider increasing notification frequency to improve engagement")
                recommendations.append("Add more motivational content to encourage exercise completion")
            
            # Engagement level recommendations
            if engagement_level == 'low':
                recommendations.append("Focus on building consistent daily habits")
                recommendations.append("Consider reducing exercise complexity to increase completion")
            
            # Risk level recommendations
            if risk_level == 'high':
                recommendations.append("Monitor patient closely and maintain frequent check-ins")
                recommendations.append("Ensure provider is aware of high-risk status")
            
            # Mood trend recommendations
            mood_trend = metrics.get('mood_trend', {})
            if mood_trend.get('trend') == 'declining':
                recommendations.append("Increase mood monitoring frequency")
                recommendations.append("Consider crisis intervention exercises")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def bulk_process_notifications(self, patient_ids: List[int]) -> Dict:
        """Process notifications for multiple patients"""
        try:
            results = []
            successful = 0
            failed = 0
            
            for patient_id in patient_ids:
                result = self.process_patient_notification_cycle(patient_id)
                results.append({'patient_id': patient_id, 'result': result})
                
                if 'error' in result:
                    failed += 1
                else:
                    successful += 1
            
            return {
                'success': True,
                'total_patients': len(patient_ids),
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error in bulk processing: {str(e)}")
            return {'error': f'Bulk processing failed: {str(e)}'}

    def update_integration_settings(self, settings: Dict) -> Dict:
        """Update integration configuration settings"""
        try:
            for key, value in settings.items():
                if key in self.integration_config:
                    self.integration_config[key] = value
            
            return {
                'success': True,
                'message': 'Integration settings updated successfully',
                'settings': self.integration_config
            }
            
        except Exception as e:
            logger.error(f"Error updating integration settings: {str(e)}")
            return {'error': f'Settings update failed: {str(e)}'}

    def get_system_health_report(self) -> Dict:
        """Get overall system health report"""
        try:
            # Get all scheduled notifications
            all_scheduled = notification_scheduler.get_scheduled_notifications()
            
            # Get all provider alerts
            all_alerts = notification_scheduler.get_provider_alerts(include_resolved=True)
            
            # Get patient count
            patient_count = Patient.query.count()
            
            # Get active patients (with recent activity)
            week_ago = datetime.now() - timedelta(days=7)
            active_patients = db.session.query(Patient.id).join(ExerciseSession)\
                .filter(ExerciseSession.start_time >= week_ago)\
                .distinct().count()
            
            return {
                'system_status': 'healthy',
                'metrics': {
                    'total_patients': patient_count,
                    'active_patients': active_patients,
                    'scheduled_notifications': len(all_scheduled),
                    'provider_alerts': len(all_alerts),
                    'critical_alerts': len([a for a in all_alerts if a.get('priority') == 'critical'])
                },
                'configuration': self.integration_config,
                'last_updated': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health report: {str(e)}")
            return {'error': f'Health report failed: {str(e)}'}

    def emergency_notification_override(self, patient_id: int, message: str, 
                                      priority: str = 'critical') -> Dict:
        """Emergency notification override for urgent situations"""
        try:
            # Create emergency notification
            emergency_notification = {
                'patient_id': patient_id,
                'message': message,
                'priority': priority,
                'escalation_level': 'crisis',
                'optimal_timing': {
                    'next_optimal_time': datetime.now() + timedelta(minutes=1),
                    'delay_hours': 0.016  # 1 minute
                },
                'provider_alert_needed': True
            }
            
            # Schedule immediately
            schedule_result = notification_scheduler.schedule_patient_notifications(patient_id)
            
            # Trigger immediate provider alert
            alert_result = intelligent_notification_system.trigger_provider_alert(
                patient_id, 'crisis', f"Emergency override: {message}"
            )
            
            return {
                'success': True,
                'emergency_notification': emergency_notification,
                'schedule_result': schedule_result,
                'alert_result': alert_result,
                'message': 'Emergency notification triggered successfully'
            }
            
        except Exception as e:
            logger.error(f"Error in emergency notification override: {str(e)}")
            return {'error': f'Emergency override failed: {str(e)}'}

# Initialize the intelligent notification integration
intelligent_notification_integration = IntelligentNotificationIntegration()
