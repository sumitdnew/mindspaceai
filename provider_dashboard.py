#!/usr/bin/env python3
"""
Provider Dashboard System
Real-time monitoring and reporting for patient exercise engagement and PHQ-9 progress
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
from sqlalchemy import and_, func, desc, case
from sqlalchemy.orm import joinedload

from app_ml_complete import (
    db, Patient, PHQ9Assessment, Exercise, ExerciseSession, 
    Activity, ActivityCategory, BehavioralActivationProgress,
    CrisisAlert, RecommendationResult, MoodEntry, MindfulnessSession
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProviderDashboard:
    """Comprehensive provider dashboard for patient monitoring and alerts"""
    
    def __init__(self):
        self.alert_levels = {
            'red': 'critical',
            'yellow': 'warning', 
            'green': 'normal'
        }
        
        self.monitoring_frequencies = {
            'severe': 'daily',
            'moderately_severe': 'daily',
            'moderate': 'weekly',
            'mild': 'biweekly',
            'minimal': 'monthly'
        }

    def get_daily_dashboard(self, provider_id: int = None) -> Dict:
        """Get daily provider dashboard with patient status and alerts"""
        try:
            dashboard = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'alerts': self._get_daily_alerts(),
                'patient_status': self._get_patient_status_summary(),
                'crisis_situations': self._get_crisis_situations(),
                'engagement_trends': self._get_engagement_trends(),
                'phq9_updates': self._get_phq9_updates()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting daily dashboard: {str(e)}")
            return {'error': f'Dashboard generation failed: {str(e)}'}

    def get_patient_detailed_view(self, patient_id: int) -> Dict:
        """Get detailed view for a specific patient"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Get latest PHQ-9 assessment
            latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                .order_by(desc(PHQ9Assessment.assessment_date)).first()
            
            # Get exercise history
            exercise_history = self._get_patient_exercise_history(patient_id)
            
            # Get mood trends
            mood_trends = self._get_patient_mood_trends(patient_id)
            
            # Get crisis alerts
            crisis_alerts = self._get_patient_crisis_alerts(patient_id)
            
            # Get engagement analysis
            engagement_analysis = self._analyze_patient_engagement(patient_id)
            
            return {
                'patient_info': {
                    'id': patient.id,
                    'name': f"{patient.first_name} {patient.last_name}",
                    'age': patient.age,
                    'current_severity': latest_assessment.severity_level if latest_assessment else 'unknown'
                },
                'current_status': {
                    'latest_phq9_score': latest_assessment.total_score if latest_assessment else None,
                    'latest_assessment_date': latest_assessment.assessment_date.isoformat() if latest_assessment else None,
                    'current_mood_trend': mood_trends.get('trend', 'unknown'),
                    'engagement_level': engagement_analysis.get('engagement_level', 'unknown')
                },
                'exercise_engagement': {
                    'recent_sessions': exercise_history[-10:] if exercise_history else [],
                    'completion_rate': engagement_analysis.get('completion_rate', 0),
                    'average_engagement': engagement_analysis.get('average_engagement', 0),
                    'preferred_exercises': engagement_analysis.get('preferred_exercises', [])
                },
                'crisis_monitoring': {
                    'recent_alerts': crisis_alerts[-5:] if crisis_alerts else [],
                    'crisis_level': self._assess_crisis_level(patient_id),
                    'safety_concerns': self._check_safety_concerns(patient_id)
                },
                'progress_indicators': {
                    'mood_improvement': mood_trends.get('improvement_rate', 0),
                    'exercise_consistency': engagement_analysis.get('consistency_score', 0),
                    'skill_development': self._assess_skill_development(patient_id)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting patient detailed view: {str(e)}")
            return {'error': f'Patient view generation failed: {str(e)}'}

    def get_weekly_report(self, patient_id: int = None) -> Dict:
        """Generate comprehensive weekly report"""
        try:
            if patient_id:
                return self._generate_patient_weekly_report(patient_id)
            else:
                return self._generate_practice_weekly_report()
                
        except Exception as e:
            logger.error(f"Error generating weekly report: {str(e)}")
            return {'error': f'Weekly report generation failed: {str(e)}'}

    def get_crisis_escalation_report(self) -> Dict:
        """Generate crisis escalation report for immediate attention"""
        try:
            # Get all crisis alerts from last 24 hours
            recent_crisis = CrisisAlert.query.filter(
                CrisisAlert.created_at >= datetime.now() - timedelta(days=1)
            ).all()
            
            # Get patients with severe PHQ-9 scores
            severe_patients = db.session.query(Patient, PHQ9Assessment)\
                .join(PHQ9Assessment)\
                .filter(
                    PHQ9Assessment.total_score >= 20,
                    PHQ9Assessment.assessment_date >= datetime.now() - timedelta(days=7)
                ).all()
            
            # Get patients with declining engagement
            declining_engagement = self._identify_declining_engagement()
            
            return {
                'crisis_alerts_24h': len(recent_crisis),
                'severe_patients': len(severe_patients),
                'declining_engagement': len(declining_engagement),
                'immediate_actions_needed': self._identify_immediate_actions(),
                'escalation_recommendations': self._generate_escalation_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating crisis escalation report: {str(e)}")
            return {'error': f'Crisis report generation failed: {str(e)}'}

    def _get_daily_alerts(self) -> Dict:
        """Get daily alerts categorized by priority"""
        try:
            alerts = {
                'red': [],
                'yellow': [],
                'green': []
            }
            
            # Red alerts - Crisis situations
            crisis_alerts = CrisisAlert.query.filter(
                CrisisAlert.created_at >= datetime.now() - timedelta(hours=24)
            ).all()
            
            for alert in crisis_alerts:
                alerts['red'].append({
                    'type': 'crisis_alert',
                    'patient_id': alert.patient_id,
                    'severity': alert.severity_level,
                    'timestamp': alert.created_at.isoformat(),
                    'description': f"Crisis alert for patient {alert.patient_id}"
                })
            
            # Yellow alerts - Concerning trends
            concerning_trends = self._identify_concerning_trends()
            for trend in concerning_trends:
                alerts['yellow'].append({
                    'type': 'concerning_trend',
                    'patient_id': trend['patient_id'],
                    'trend_type': trend['trend_type'],
                    'description': trend['description']
                })
            
            # Green status - Good progress
            good_progress = self._identify_good_progress()
            for progress in good_progress:
                alerts['green'].append({
                    'type': 'good_progress',
                    'patient_id': progress['patient_id'],
                    'progress_type': progress['progress_type'],
                    'description': progress['description']
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting daily alerts: {str(e)}")
            return {'red': [], 'yellow': [], 'green': []}

    def _get_patient_status_summary(self) -> Dict:
        """Get summary of all patient statuses"""
        try:
            patients = Patient.query.all()
            status_summary = {
                'total_patients': len(patients),
                'by_severity': {},
                'by_engagement': {},
                'by_risk': {}
            }
            
            for patient in patients:
                # Get latest assessment
                latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient.id)\
                    .order_by(desc(PHQ9Assessment.assessment_date)).first()
                
                if latest_assessment:
                    severity = latest_assessment.severity_level
                    status_summary['by_severity'][severity] = status_summary['by_severity'].get(severity, 0) + 1
                    
                    if latest_assessment.q9_risk_flag:
                        status_summary['by_risk']['high_risk'] = status_summary['by_risk'].get('high_risk', 0) + 1
                
                # Get engagement level
                engagement = self._analyze_patient_engagement(patient.id)
                engagement_level = engagement.get('engagement_level', 'unknown')
                status_summary['by_engagement'][engagement_level] = status_summary['by_engagement'].get(engagement_level, 0) + 1
            
            return status_summary
            
        except Exception as e:
            logger.error(f"Error getting patient status summary: {str(e)}")
            return {}

    def _get_crisis_situations(self) -> List[Dict]:
        """Get current crisis situations requiring attention"""
        try:
            crisis_situations = []
            
            # Get recent crisis alerts
            recent_crisis = CrisisAlert.query.filter(
                CrisisAlert.created_at >= datetime.now() - timedelta(hours=12)
            ).all()
            
            for crisis in recent_crisis:
                patient = Patient.query.get(crisis.patient_id)
                if patient:
                    crisis_situations.append({
                        'patient_id': crisis.patient_id,
                        'patient_name': f"{patient.first_name} {patient.last_name}",
                        'crisis_level': crisis.severity_level,
                        'alert_type': crisis.alert_type,
                        'timestamp': crisis.created_at.isoformat(),
                        'requires_immediate_action': crisis.severity_level in ['severe', 'immediate']
                    })
            
            return crisis_situations
            
        except Exception as e:
            logger.error(f"Error getting crisis situations: {str(e)}")
            return []

    def _get_engagement_trends(self) -> Dict:
        """Get engagement trends across all patients"""
        try:
            patients = Patient.query.all()
            engagement_data = []
            
            for patient in patients:
                engagement = self._analyze_patient_engagement(patient.id)
                if engagement:
                    engagement_data.append({
                        'patient_id': patient.id,
                        'completion_rate': engagement.get('completion_rate', 0),
                        'engagement_level': engagement.get('engagement_level', 'unknown'),
                        'trend': engagement.get('trend', 'stable')
                    })
            
            # Calculate overall trends
            if engagement_data:
                avg_completion = sum(d['completion_rate'] for d in engagement_data) / len(engagement_data)
                high_engagement = sum(1 for d in engagement_data if d['engagement_level'] == 'high')
                improving_trends = sum(1 for d in engagement_data if d['trend'] == 'improving')
                
                return {
                    'average_completion_rate': avg_completion,
                    'high_engagement_count': high_engagement,
                    'improving_trends_count': improving_trends,
                    'total_patients': len(engagement_data)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting engagement trends: {str(e)}")
            return {}

    def _get_phq9_updates(self) -> List[Dict]:
        """Get recent PHQ-9 assessment updates"""
        try:
            recent_assessments = PHQ9Assessment.query.filter(
                PHQ9Assessment.assessment_date >= datetime.now() - timedelta(days=7)
            ).order_by(desc(PHQ9Assessment.assessment_date)).all()
            
            updates = []
            for assessment in recent_assessments:
                patient = Patient.query.get(assessment.patient_id)
                if patient:
                    updates.append({
                        'patient_id': assessment.patient_id,
                        'patient_name': f"{patient.first_name} {patient.last_name}",
                        'score': assessment.total_score,
                        'severity': assessment.severity_level,
                        'assessment_date': assessment.assessment_date.isoformat(),
                        'change_from_previous': self._calculate_phq9_change(assessment.patient_id, assessment.total_score)
                    })
            
            return updates
            
        except Exception as e:
            logger.error(f"Error getting PHQ-9 updates: {str(e)}")
            return []

    def _get_patient_exercise_history(self, patient_id: int) -> List[Dict]:
        """Get patient's exercise history"""
        try:
            sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).all()
            
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
            logger.error(f"Error getting patient exercise history: {str(e)}")
            return []

    def _get_patient_mood_trends(self, patient_id: int) -> Dict:
        """Get patient's mood trends"""
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
                'total_entries': len(scores),
                'recent_scores': scores[-7:] if len(scores) >= 7 else scores
            }
            
        except Exception as e:
            logger.error(f"Error getting patient mood trends: {str(e)}")
            return {'trend': 'error', 'improvement_rate': 0}

    def _get_patient_crisis_alerts(self, patient_id: int) -> List[Dict]:
        """Get patient's crisis alerts"""
        try:
            alerts = CrisisAlert.query.filter_by(patient_id=patient_id)\
                .order_by(desc(CrisisAlert.created_at)).all()
            
            return [{
                'alert_type': alert.alert_type,
                'severity_level': alert.severity_level,
                'created_at': alert.created_at.isoformat(),
                'triggers': json.loads(alert.triggers) if alert.triggers else []
            } for alert in alerts]
            
        except Exception as e:
            logger.error(f"Error getting patient crisis alerts: {str(e)}")
            return []

    def _analyze_patient_engagement(self, patient_id: int) -> Dict:
        """Analyze patient's exercise engagement"""
        try:
            sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).limit(20).all()
            
            if not sessions:
                return {'engagement_level': 'none', 'completion_rate': 0}
            
            # Calculate completion rate
            completed = sum(1 for s in sessions if s.completion_status == 'completed')
            completion_rate = completed / len(sessions)
            
            # Calculate average engagement
            engagement_scores = [s.engagement_score for s in sessions if s.engagement_score]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
            
            # Determine engagement level
            if completion_rate > 0.8 and avg_engagement > 7:
                engagement_level = 'high'
            elif completion_rate > 0.5 and avg_engagement > 5:
                engagement_level = 'moderate'
            else:
                engagement_level = 'low'
            
            # Calculate trend
            if len(sessions) >= 10:
                recent_sessions = sessions[:5]
                older_sessions = sessions[5:10]
                
                recent_avg = sum(s.engagement_score for s in recent_sessions if s.engagement_score) / len(recent_sessions)
                older_avg = sum(s.engagement_score for s in older_sessions if s.engagement_score) / len(older_sessions)
                
                if recent_avg > older_avg:
                    trend = 'improving'
                elif recent_avg < older_avg:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            return {
                'engagement_level': engagement_level,
                'completion_rate': completion_rate,
                'average_engagement': avg_engagement,
                'trend': trend,
                'total_sessions': len(sessions),
                'consistency_score': self._calculate_consistency_score(sessions)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patient engagement: {str(e)}")
            return {'engagement_level': 'error', 'completion_rate': 0}

    def _assess_crisis_level(self, patient_id: int) -> str:
        """Assess current crisis level for patient"""
        try:
            # Check recent crisis alerts
            recent_crisis = CrisisAlert.query.filter_by(patient_id=patient_id)\
                .order_by(desc(CrisisAlert.created_at)).first()
            
            if recent_crisis and (datetime.now() - recent_crisis.created_at).days < 1:
                return recent_crisis.severity_level
            
            # Check recent mood
            recent_mood = MoodEntry.query.filter_by(patient_id=patient_id)\
                .order_by(desc(MoodEntry.entry_date)).first()
            
            if recent_mood and recent_mood.mood_score <= 2:
                return 'moderate'
            
            return 'none'
            
        except Exception as e:
            logger.error(f"Error assessing crisis level: {str(e)}")
            return 'unknown'

    def _check_safety_concerns(self, patient_id: int) -> List[str]:
        """Check for safety concerns for patient"""
        try:
            concerns = []
            
            # Check for very low mood
            recent_mood = MoodEntry.query.filter_by(patient_id=patient_id)\
                .order_by(desc(MoodEntry.entry_date)).first()
            
            if recent_mood and recent_mood.mood_score <= 2:
                concerns.append('very_low_mood')
            
            # Check for missed exercises in severe patients
            latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                .order_by(desc(PHQ9Assessment.assessment_date)).first()
            
            if latest_assessment and latest_assessment.total_score >= 15:
                recent_sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                    .order_by(desc(ExerciseSession.start_time)).limit(3).all()
                
                if not recent_sessions or all(s.completion_status != 'completed' for s in recent_sessions):
                    concerns.append('missed_exercises_severe_patient')
            
            return concerns
            
        except Exception as e:
            logger.error(f"Error checking safety concerns: {str(e)}")
            return []

    def _assess_skill_development(self, patient_id: int) -> Dict:
        """Assess patient's skill development progress"""
        try:
            sessions = ExerciseSession.query.filter_by(patient_id=patient_id)\
                .order_by(desc(ExerciseSession.start_time)).limit(20).all()
            
            if not sessions:
                return {'skill_level': 'beginner', 'progress': 'insufficient_data'}
            
            # Calculate skill level based on exercise types and effectiveness
            cbt_sessions = [s for s in sessions if 'cbt' in s.exercise.type.lower()]
            mindfulness_sessions = [s for s in sessions if 'mindfulness' in s.exercise.type.lower()]
            
            skill_development = {
                'cbt_mastery': len(cbt_sessions),
                'mindfulness_consistency': len(mindfulness_sessions),
                'total_sessions': len(sessions),
                'average_effectiveness': sum(s.effectiveness_rating for s in sessions if s.effectiveness_rating) / len(sessions) if sessions else 0
            }
            
            # Determine overall skill level
            if skill_development['total_sessions'] > 20 and skill_development['average_effectiveness'] > 8:
                skill_level = 'advanced'
            elif skill_development['total_sessions'] > 10 and skill_development['average_effectiveness'] > 6:
                skill_level = 'intermediate'
            else:
                skill_level = 'beginner'
            
            skill_development['skill_level'] = skill_level
            return skill_development
            
        except Exception as e:
            logger.error(f"Error assessing skill development: {str(e)}")
            return {'skill_level': 'unknown', 'progress': 'error'}

    def _calculate_phq9_change(self, patient_id: int, current_score: int) -> Optional[float]:
        """Calculate change in PHQ-9 score from previous assessment"""
        try:
            assessments = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                .order_by(desc(PHQ9Assessment.assessment_date)).limit(2).all()
            
            if len(assessments) >= 2:
                previous_score = assessments[1].total_score
                return current_score - previous_score
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating PHQ-9 change: {str(e)}")
            return None

    def _calculate_consistency_score(self, sessions: List[ExerciseSession]) -> float:
        """Calculate consistency score based on exercise completion patterns"""
        try:
            if not sessions:
                return 0.0
            
            # Calculate consistency based on regular completion
            completed_sessions = [s for s in sessions if s.completion_status == 'completed']
            consistency_rate = len(completed_sessions) / len(sessions)
            
            # Bonus for recent consistency
            recent_sessions = sessions[:7] if len(sessions) >= 7 else sessions
            recent_completed = sum(1 for s in recent_sessions if s.completion_status == 'completed')
            recent_consistency = recent_completed / len(recent_sessions)
            
            # Weighted average
            consistency_score = (consistency_rate * 0.7) + (recent_consistency * 0.3)
            
            return consistency_score
            
        except Exception as e:
            logger.error(f"Error calculating consistency score: {str(e)}")
            return 0.0

    def _identify_concerning_trends(self) -> List[Dict]:
        """Identify concerning trends across patients"""
        try:
            concerning_trends = []
            patients = Patient.query.all()
            
            for patient in patients:
                # Check for declining mood
                mood_trends = self._get_patient_mood_trends(patient.id)
                if mood_trends.get('trend') == 'declining':
                    concerning_trends.append({
                        'patient_id': patient.id,
                        'trend_type': 'declining_mood',
                        'description': f"Patient {patient.id} showing declining mood trend"
                    })
                
                # Check for declining engagement
                engagement = self._analyze_patient_engagement(patient.id)
                if engagement.get('trend') == 'declining':
                    concerning_trends.append({
                        'patient_id': patient.id,
                        'trend_type': 'declining_engagement',
                        'description': f"Patient {patient.id} showing declining exercise engagement"
                    })
            
            return concerning_trends
            
        except Exception as e:
            logger.error(f"Error identifying concerning trends: {str(e)}")
            return []

    def _identify_good_progress(self) -> List[Dict]:
        """Identify patients showing good progress"""
        try:
            good_progress = []
            patients = Patient.query.all()
            
            for patient in patients:
                # Check for improving mood
                mood_trends = self._get_patient_mood_trends(patient.id)
                if mood_trends.get('trend') == 'improving':
                    good_progress.append({
                        'patient_id': patient.id,
                        'progress_type': 'improving_mood',
                        'description': f"Patient {patient.id} showing mood improvement"
                    })
                
                # Check for high engagement
                engagement = self._analyze_patient_engagement(patient.id)
                if engagement.get('engagement_level') == 'high':
                    good_progress.append({
                        'patient_id': patient.id,
                        'progress_type': 'high_engagement',
                        'description': f"Patient {patient.id} maintaining high exercise engagement"
                    })
            
            return good_progress
            
        except Exception as e:
            logger.error(f"Error identifying good progress: {str(e)}")
            return []

    def _identify_declining_engagement(self) -> List[Dict]:
        """Identify patients with declining engagement"""
        try:
            declining_patients = []
            patients = Patient.query.all()
            
            for patient in patients:
                engagement = self._analyze_patient_engagement(patient.id)
                if engagement.get('trend') == 'declining':
                    declining_patients.append({
                        'patient_id': patient.id,
                        'completion_rate': engagement.get('completion_rate', 0),
                        'engagement_level': engagement.get('engagement_level', 'unknown')
                    })
            
            return declining_patients
            
        except Exception as e:
            logger.error(f"Error identifying declining engagement: {str(e)}")
            return []

    def _identify_immediate_actions(self) -> List[Dict]:
        """Identify immediate actions needed"""
        try:
            actions = []
            
            # Check for crisis alerts
            recent_crisis = CrisisAlert.query.filter(
                CrisisAlert.created_at >= datetime.now() - timedelta(hours=6)
            ).all()
            
            for crisis in recent_crisis:
                actions.append({
                    'type': 'crisis_intervention',
                    'patient_id': crisis.patient_id,
                    'priority': 'immediate',
                    'description': f"Immediate crisis intervention needed for patient {crisis.patient_id}"
                })
            
            # Check for severe patients with missed exercises
            severe_patients = db.session.query(Patient, PHQ9Assessment)\
                .join(PHQ9Assessment)\
                .filter(PHQ9Assessment.total_score >= 20).all()
            
            for patient, assessment in severe_patients:
                recent_sessions = ExerciseSession.query.filter_by(patient_id=patient.id)\
                    .order_by(desc(ExerciseSession.start_time)).limit(3).all()
                
                if not recent_sessions or all(s.completion_status != 'completed' for s in recent_sessions):
                    actions.append({
                        'type': 'missed_exercises_severe',
                        'patient_id': patient.id,
                        'priority': 'high',
                        'description': f"Severe patient {patient.id} missing exercises - immediate contact needed"
                    })
            
            return actions
            
        except Exception as e:
            logger.error(f"Error identifying immediate actions: {str(e)}")
            return []

    def _generate_escalation_recommendations(self) -> List[Dict]:
        """Generate escalation recommendations for crisis situations"""
        try:
            recommendations = []
            
            # Get all crisis alerts
            crisis_alerts = CrisisAlert.query.filter(
                CrisisAlert.created_at >= datetime.now() - timedelta(days=1)
            ).all()
            
            for alert in crisis_alerts:
                patient = Patient.query.get(alert.patient_id)
                if patient:
                    recommendations.append({
                        'patient_id': alert.patient_id,
                        'patient_name': f"{patient.first_name} {patient.last_name}",
                        'crisis_level': alert.severity_level,
                        'recommended_action': self._get_crisis_recommendation(alert.severity_level),
                        'urgency': 'immediate' if alert.severity_level in ['severe', 'immediate'] else 'high'
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating escalation recommendations: {str(e)}")
            return []

    def _get_crisis_recommendation(self, crisis_level: str) -> str:
        """Get specific recommendation based on crisis level"""
        recommendations = {
            'immediate': 'Immediate provider contact and crisis intervention required',
            'severe': 'Urgent provider contact within 2 hours',
            'moderate': 'Schedule urgent appointment within 24 hours',
            'mild': 'Monitor closely and schedule follow-up appointment'
        }
        
        return recommendations.get(crisis_level, 'Monitor patient status')

    def _generate_patient_weekly_report(self, patient_id: int) -> Dict:
        """Generate weekly report for specific patient"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Get weekly data
            week_ago = datetime.now() - timedelta(days=7)
            
            # Exercise sessions this week
            weekly_sessions = ExerciseSession.query.filter(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            ).all()
            
            # Mood entries this week
            weekly_mood = MoodEntry.query.filter(
                MoodEntry.patient_id == patient_id,
                MoodEntry.entry_date >= week_ago
            ).all()
            
            # Crisis alerts this week
            weekly_crisis = CrisisAlert.query.filter(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= week_ago
            ).all()
            
            return {
                'patient_info': {
                    'id': patient.id,
                    'name': f"{patient.first_name} {patient.last_name}"
                },
                'weekly_summary': {
                    'exercise_sessions': len(weekly_sessions),
                    'completed_exercises': sum(1 for s in weekly_sessions if s.completion_status == 'completed'),
                    'mood_entries': len(weekly_mood),
                    'crisis_alerts': len(weekly_crisis),
                    'average_mood': sum(m.mood_score for m in weekly_mood) / len(weekly_mood) if weekly_mood else None
                },
                'engagement_analysis': self._analyze_patient_engagement(patient_id),
                'mood_trends': self._get_patient_mood_trends(patient_id),
                'recommendations': self._generate_weekly_recommendations(patient_id, weekly_sessions, weekly_mood)
            }
            
        except Exception as e:
            logger.error(f"Error generating patient weekly report: {str(e)}")
            return {'error': f'Weekly report generation failed: {str(e)}'}

    def _generate_practice_weekly_report(self) -> Dict:
        """Generate weekly report for entire practice"""
        try:
            # Get all patients
            patients = Patient.query.all()
            
            # Weekly statistics
            week_ago = datetime.now() - timedelta(days=7)
            
            weekly_sessions = ExerciseSession.query.filter(
                ExerciseSession.start_time >= week_ago
            ).all()
            
            weekly_crisis = CrisisAlert.query.filter(
                CrisisAlert.created_at >= week_ago
            ).all()
            
            return {
                'practice_summary': {
                    'total_patients': len(patients),
                    'active_patients': len([p for p in patients if self._is_patient_active(p.id)]),
                    'weekly_exercise_sessions': len(weekly_sessions),
                    'weekly_crisis_alerts': len(weekly_crisis)
                },
                'engagement_overview': self._get_engagement_trends(),
                'crisis_overview': {
                    'total_crisis_alerts': len(weekly_crisis),
                    'severe_crisis': len([c for c in weekly_crisis if c.severity_level in ['severe', 'immediate']])
                },
                'recommendations': self._generate_practice_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating practice weekly report: {str(e)}")
            return {'error': f'Practice report generation failed: {str(e)}'}

    def _is_patient_active(self, patient_id: int) -> bool:
        """Check if patient is active (has recent activity)"""
        try:
            week_ago = datetime.now() - timedelta(days=7)
            
            # Check for recent exercise sessions
            recent_sessions = ExerciseSession.query.filter(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            ).first()
            
            # Check for recent mood entries
            recent_mood = MoodEntry.query.filter(
                MoodEntry.patient_id == patient_id,
                MoodEntry.entry_date >= week_ago
            ).first()
            
            return recent_sessions is not None or recent_mood is not None
            
        except Exception as e:
            logger.error(f"Error checking patient activity: {str(e)}")
            return False

    def _generate_weekly_recommendations(self, patient_id: int, sessions: List[ExerciseSession], 
                                       mood_entries: List[MoodEntry]) -> List[Dict]:
        """Generate weekly recommendations for patient"""
        try:
            recommendations = []
            
            # Analyze exercise completion
            completion_rate = sum(1 for s in sessions if s.completion_status == 'completed') / len(sessions) if sessions else 0
            
            if completion_rate < 0.5:
                recommendations.append({
                    'type': 'increase_support',
                    'description': 'Low exercise completion - consider simplified exercises or additional support',
                    'priority': 'high'
                })
            
            # Analyze mood trends
            if mood_entries:
                mood_scores = [m.mood_score for m in mood_entries]
                if len(mood_scores) >= 3:
                    recent_avg = sum(mood_scores[-3:]) / 3
                    if recent_avg <= 3:
                        recommendations.append({
                            'type': 'mood_intervention',
                            'description': 'Consistently low mood - consider crisis monitoring and provider contact',
                            'priority': 'high'
                        })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating weekly recommendations: {str(e)}")
            return []

    def _generate_practice_recommendations(self) -> List[Dict]:
        """Generate practice-wide recommendations"""
        try:
            recommendations = []
            
            # Check overall engagement
            engagement_trends = self._get_engagement_trends()
            avg_completion = engagement_trends.get('average_completion_rate', 0)
            
            if avg_completion < 0.6:
                recommendations.append({
                    'type': 'engagement_improvement',
                    'description': 'Overall low engagement - consider system-wide engagement strategies',
                    'priority': 'medium'
                })
            
            # Check crisis frequency
            week_ago = datetime.now() - timedelta(days=7)
            weekly_crisis = CrisisAlert.query.filter(
                CrisisAlert.created_at >= week_ago
            ).all()
            
            if len(weekly_crisis) > 5:
                recommendations.append({
                    'type': 'crisis_management',
                    'description': 'High crisis frequency - review crisis protocols and provider availability',
                    'priority': 'high'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating practice recommendations: {str(e)}")
            return []

# Initialize the provider dashboard
provider_dashboard = ProviderDashboard()
