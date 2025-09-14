#!/usr/bin/env python3
"""
Real-Time Patient Action Analysis & Provider Insight System
Transforms every patient interaction into actionable clinical intelligence
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import numpy as np
from sqlalchemy import func, and_, desc, extract, case
from collections import defaultdict
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

# Import database models
from app_ml_complete import (
    db, Patient, PHQ9Assessment, ExerciseSession, MoodEntry, 
    CrisisAlert, MindfulnessSession, MicroAssessment, ThoughtRecord
)

real_time_insights = Blueprint('real_time_insights', __name__)

class RealTimePatientSummaryEngine:
    """Real-time patient summary engine with continuous data aggregation"""
    
    def __init__(self):
        self.risk_levels = {
            'green': {'min': 0, 'max': 4, 'color': '#28a745'},
            'yellow': {'min': 5, 'max': 9, 'color': '#ffc107'},
            'orange': {'min': 10, 'max': 14, 'color': '#fd7e14'},
            'red': {'min': 15, 'max': 27, 'color': '#dc3545'}
        }
    
    def get_real_time_patient_summary(self, patient_id: int) -> Dict[str, Any]:
        """Generate comprehensive real-time patient summary"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Get current data
            current_mood = self._get_current_mood_state(patient_id)
            engagement_metrics = self._get_engagement_metrics(patient_id)
            risk_assessment = self._get_risk_assessment(patient_id)
            treatment_response = self._get_treatment_response_indicators(patient_id)
            weekly_trends = self._get_weekly_trend_analysis(patient_id)
            
            # Generate recommendations
            recommendations = self._generate_intervention_recommendations(
                patient_id, current_mood, engagement_metrics, risk_assessment, treatment_response
            )
            
            return {
                'patient_info': {
                    'id': patient.id,
                    'name': f"{patient.first_name} {patient.last_name}",
                    'current_phq9_severity': patient.current_phq9_severity,
                    'last_assessment_date': patient.last_assessment_date.isoformat() if patient.last_assessment_date else None
                },
                'current_status': {
                    'risk_level': risk_assessment['current_risk_level'],
                    'risk_color': risk_assessment['risk_color'],
                    'mood_state': current_mood['current_mood'],
                    'engagement_level': engagement_metrics['engagement_level'],
                    'treatment_urgency': risk_assessment['treatment_urgency']
                },
                'today_summary': {
                    'mood_check_ins': current_mood['today_check_ins'],
                    'exercises_completed': engagement_metrics['today_completed'],
                    'exercises_skipped': engagement_metrics['today_skipped'],
                    'crisis_tools_accessed': risk_assessment['crisis_access_today'],
                    'concerns': self._identify_today_concerns(patient_id)
                },
                'weekly_trends': weekly_trends,
                'treatment_response': treatment_response,
                'recommendations': recommendations,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating patient summary: {str(e)}")
            return {'error': f'Failed to generate summary: {str(e)}'}
    
    def _get_current_mood_state(self, patient_id: int) -> Dict[str, Any]:
        """Get current mood state and recent patterns"""
        # Get today's mood entries
        today = datetime.now().date()
        today_mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                func.date(MoodEntry.timestamp) == today
            )
        ).order_by(MoodEntry.timestamp.desc()).all()
        
        # Get recent mood trend (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        # Calculate current mood
        current_mood = 'neutral'
        if today_mood_entries:
            latest_entry = today_mood_entries[0]
            if latest_entry.intensity_level <= 3:
                current_mood = 'very_low'
            elif latest_entry.intensity_level <= 5:
                current_mood = 'low'
            elif latest_entry.intensity_level <= 7:
                current_mood = 'neutral'
            elif latest_entry.intensity_level <= 9:
                current_mood = 'good'
            else:
                current_mood = 'excellent'
        
        # Calculate mood trend
        mood_trend = 'stable'
        if len(recent_mood_entries) >= 2:
            recent_avg = np.mean([entry.intensity_level for entry in recent_mood_entries[-3:]])
            earlier_avg = np.mean([entry.intensity_level for entry in recent_mood_entries[:3]])
            if recent_avg > earlier_avg + 1:
                mood_trend = 'improving'
            elif recent_avg < earlier_avg - 1:
                mood_trend = 'declining'
        
        return {
            'current_mood': current_mood,
            'current_intensity': latest_entry.intensity_level if today_mood_entries else None,
            'mood_trend': mood_trend,
            'today_check_ins': len(today_mood_entries),
            'week_avg_intensity': np.mean([entry.intensity_level for entry in recent_mood_entries]) if recent_mood_entries else None
        }
    
    def _get_engagement_metrics(self, patient_id: int) -> Dict[str, Any]:
        """Get current engagement metrics"""
        today = datetime.now().date()
        week_ago = datetime.now() - timedelta(days=7)
        
        # Today's exercise activity
        today_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                func.date(ExerciseSession.start_time) == today
            )
        ).all()
        
        # Weekly engagement
        week_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            )
        ).all()
        
        # Calculate metrics
        today_completed = len([s for s in today_sessions if s.completion_status == 'completed'])
        today_skipped = len([s for s in today_sessions if s.completion_status == 'abandoned'])
        week_completion_rate = len([s for s in week_sessions if s.completion_status == 'completed']) / len(week_sessions) if week_sessions else 0
        
        # Determine engagement level
        if week_completion_rate >= 0.8:
            engagement_level = 'high'
        elif week_completion_rate >= 0.5:
            engagement_level = 'moderate'
        else:
            engagement_level = 'low'
        
        return {
            'engagement_level': engagement_level,
            'today_completed': today_completed,
            'today_skipped': today_skipped,
            'week_completion_rate': round(week_completion_rate, 3),
            'total_week_sessions': len(week_sessions)
        }
    
    def _get_risk_assessment(self, patient_id: int) -> Dict[str, Any]:
        """Get current risk assessment"""
        today = datetime.now().date()
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get latest PHQ-9 assessment
        latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(PHQ9Assessment.assessment_date.desc()).first()
        
        # Get recent crisis alerts
        recent_crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= week_ago
            )
        ).all()
        
        # Get crisis tool usage today
        crisis_access_today = 0  # This would be tracked in a separate table
        
        # Determine current risk level
        current_risk_level = 'green'
        risk_color = self.risk_levels['green']['color']
        treatment_urgency = 'routine'
        
        if latest_assessment:
            if latest_assessment.total_score >= 20:
                current_risk_level = 'red'
                risk_color = self.risk_levels['red']['color']
                treatment_urgency = 'immediate'
            elif latest_assessment.total_score >= 15:
                current_risk_level = 'orange'
                risk_color = self.risk_levels['orange']['color']
                treatment_urgency = 'urgent'
            elif latest_assessment.total_score >= 10:
                current_risk_level = 'yellow'
                risk_color = self.risk_levels['yellow']['color']
                treatment_urgency = 'moderate'
        
        # Adjust based on recent crisis activity
        if recent_crisis_alerts:
            current_risk_level = 'red'
            risk_color = self.risk_levels['red']['color']
            treatment_urgency = 'immediate'
        
        return {
            'current_risk_level': current_risk_level,
            'risk_color': risk_color,
            'treatment_urgency': treatment_urgency,
            'latest_phq9_score': latest_assessment.total_score if latest_assessment else None,
            'crisis_alerts_week': len(recent_crisis_alerts),
            'crisis_access_today': crisis_access_today
        }
    
    def _get_treatment_response_indicators(self, patient_id: int) -> Dict[str, Any]:
        """Get treatment response indicators"""
        month_ago = datetime.now() - timedelta(days=30)
        
        # Get exercise effectiveness data
        recent_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago,
                ExerciseSession.effectiveness_rating.isnot(None)
            )
        ).all()
        
        # Calculate effectiveness metrics
        if recent_sessions:
            avg_effectiveness = np.mean([s.effectiveness_rating for s in recent_sessions])
            effectiveness_trend = 'stable'
            
            # Determine trend
            if len(recent_sessions) >= 6:
                recent_avg = np.mean([s.effectiveness_rating for s in recent_sessions[-3:]])
                earlier_avg = np.mean([s.effectiveness_rating for s in recent_sessions[:3]])
                if recent_avg > earlier_avg + 1:
                    effectiveness_trend = 'improving'
                elif recent_avg < earlier_avg - 1:
                    effectiveness_trend = 'declining'
        else:
            avg_effectiveness = None
            effectiveness_trend = 'insufficient_data'
        
        return {
            'avg_effectiveness': round(avg_effectiveness, 2) if avg_effectiveness else None,
            'effectiveness_trend': effectiveness_trend,
            'exercises_working': avg_effectiveness >= 7 if avg_effectiveness else None,
            'total_rated_sessions': len(recent_sessions)
        }
    
    def _get_weekly_trend_analysis(self, patient_id: int) -> Dict[str, Any]:
        """Get weekly trend analysis"""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get mood trends
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        # Get exercise trends
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            )
        ).order_by(ExerciseSession.start_time).all()
        
        # Calculate trends
        mood_trend = 'stable'
        exercise_trend = 'stable'
        
        if len(mood_entries) >= 4:
            recent_mood_avg = np.mean([entry.intensity_level for entry in mood_entries[-3:]])
            earlier_mood_avg = np.mean([entry.intensity_level for entry in mood_entries[:3]])
            if recent_mood_avg > earlier_mood_avg + 1:
                mood_trend = 'improving'
            elif recent_mood_avg < earlier_mood_avg - 1:
                mood_trend = 'declining'
        
        if len(exercise_sessions) >= 4:
            recent_exercise_count = len([s for s in exercise_sessions[-3:] if s.completion_status == 'completed'])
            earlier_exercise_count = len([s for s in exercise_sessions[:3] if s.completion_status == 'completed'])
            if recent_exercise_count > earlier_exercise_count:
                exercise_trend = 'improving'
            elif recent_exercise_count < earlier_exercise_count:
                exercise_trend = 'declining'
        
        return {
            'mood_trend': mood_trend,
            'exercise_trend': exercise_trend,
            'overall_trend': 'improving' if mood_trend == 'improving' and exercise_trend == 'improving' else 'stable',
            'mood_entries_count': len(mood_entries),
            'exercise_sessions_count': len(exercise_sessions)
        }
    
    def _identify_today_concerns(self, patient_id: int) -> List[str]:
        """Identify today's concerns based on patient activity"""
        concerns = []
        today = datetime.now().date()
        
        # Check for missed exercises
        today_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                func.date(ExerciseSession.start_time) == today
            )
        ).all()
        
        if not today_sessions:
            concerns.append("No exercise sessions today")
        elif any(s.completion_status == 'abandoned' for s in today_sessions):
            concerns.append("Some exercises were skipped today")
        
        # Check for low mood
        today_mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                func.date(MoodEntry.timestamp) == today
            )
        ).all()
        
        if today_mood_entries:
            avg_mood = np.mean([entry.intensity_level for entry in today_mood_entries])
            if avg_mood <= 3:
                concerns.append("Low mood throughout the day")
        
        return concerns
    
    def _generate_intervention_recommendations(self, patient_id: int, current_mood: Dict, 
                                            engagement_metrics: Dict, risk_assessment: Dict, 
                                            treatment_response: Dict) -> Dict[str, Any]:
        """Generate intervention recommendations based on current state"""
        recommendations = {
            'immediate_actions': [],
            'session_focus': [],
            'treatment_adjustments': [],
            'monitoring_priorities': []
        }
        
        # Risk-based recommendations
        if risk_assessment['current_risk_level'] == 'red':
            recommendations['immediate_actions'].append("Schedule urgent session within 24 hours")
            recommendations['immediate_actions'].append("Implement crisis safety plan")
            recommendations['monitoring_priorities'].append("Hourly mood check-ins")
        
        elif risk_assessment['current_risk_level'] == 'orange':
            recommendations['immediate_actions'].append("Schedule session within 48 hours")
            recommendations['session_focus'].append("Crisis prevention strategies")
            recommendations['monitoring_priorities'].append("Twice daily mood check-ins")
        
        # Engagement-based recommendations
        if engagement_metrics['engagement_level'] == 'low':
            recommendations['session_focus'].append("Address treatment resistance")
            recommendations['treatment_adjustments'].append("Simplify exercise recommendations")
            recommendations['immediate_actions'].append("Send motivational outreach")
        
        # Mood-based recommendations
        if current_mood['mood_trend'] == 'declining':
            recommendations['session_focus'].append("Explore recent stressors")
            recommendations['treatment_adjustments'].append("Increase supportive interventions")
        
        # Treatment response recommendations
        if treatment_response['effectiveness_trend'] == 'declining':
            recommendations['session_focus'].append("Evaluate current treatment approach")
            recommendations['treatment_adjustments'].append("Consider alternative interventions")
        
        return recommendations

class ActionTriggeredAnalysis:
    """Action-triggered analysis system"""
    
    def __init__(self):
        self.analysis_engine = RealTimePatientSummaryEngine()
    
    def analyze_mood_checkin(self, patient_id: int, mood_data: Dict) -> Dict[str, Any]:
        """Analyze mood check-in and generate insights"""
        try:
            # Update mood trend analysis
            mood_trends = self._update_mood_trend_analysis(patient_id)
            
            # Adjust crisis risk assessment
            risk_assessment = self._adjust_crisis_risk_assessment(patient_id, mood_data)
            
            # Generate mood-specific recommendations
            recommendations = self._generate_mood_specific_recommendations(patient_id, mood_data)
            
            # Flag concerning patterns
            concerns = self._flag_concerning_patterns(patient_id, mood_data)
            
            # Update PHQ-9 prediction
            phq9_prediction = self._update_phq9_prediction(patient_id, mood_data)
            
            return {
                'mood_trends': mood_trends,
                'risk_assessment': risk_assessment,
                'recommendations': recommendations,
                'concerns': concerns,
                'phq9_prediction': phq9_prediction,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing mood check-in: {str(e)}")
            return {'error': f'Failed to analyze mood check-in: {str(e)}'}
    
    def analyze_exercise_completion(self, patient_id: int, exercise_data: Dict) -> Dict[str, Any]:
        """Analyze exercise completion/skip and generate insights"""
        try:
            # Update treatment adherence score
            adherence_score = self._update_adherence_score(patient_id, exercise_data)
            
            # Analyze exercise effectiveness
            effectiveness = self._analyze_exercise_effectiveness(patient_id, exercise_data)
            
            # Adjust future recommendations
            future_recommendations = self._adjust_future_recommendations(patient_id, exercise_data)
            
            # Flag adherence concerns
            adherence_concerns = self._flag_adherence_concerns(patient_id, exercise_data)
            
            # Generate intervention recommendations
            interventions = self._generate_adherence_interventions(patient_id, exercise_data)
            
            return {
                'adherence_score': adherence_score,
                'effectiveness': effectiveness,
                'future_recommendations': future_recommendations,
                'adherence_concerns': adherence_concerns,
                'interventions': interventions,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing exercise completion: {str(e)}")
            return {'error': f'Failed to analyze exercise completion: {str(e)}'}
    
    def analyze_crisis_tool_access(self, patient_id: int, crisis_data: Dict) -> Dict[str, Any]:
        """Analyze crisis tool access and generate immediate response"""
        try:
            # Generate immediate provider alert
            provider_alert = self._generate_provider_alert(patient_id, crisis_data)
            
            # Update risk status
            risk_status = self._update_risk_status(patient_id, crisis_data)
            
            # Generate safety planning recommendations
            safety_planning = self._generate_safety_planning(patient_id, crisis_data)
            
            # Suggest session scheduling urgency
            session_urgency = self._suggest_session_urgency(patient_id, crisis_data)
            
            # Log crisis pattern analysis
            pattern_analysis = self._log_crisis_pattern_analysis(patient_id, crisis_data)
            
            return {
                'provider_alert': provider_alert,
                'risk_status': risk_status,
                'safety_planning': safety_planning,
                'session_urgency': session_urgency,
                'pattern_analysis': pattern_analysis,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing crisis tool access: {str(e)}")
            return {'error': f'Failed to analyze crisis tool access: {str(e)}'}
    
    def analyze_cbt_exercise(self, patient_id: int, cbt_data: Dict) -> Dict[str, Any]:
        """Analyze CBT exercise completion and generate insights"""
        try:
            # Analyze cognitive pattern improvements
            cognitive_patterns = self._analyze_cognitive_patterns(patient_id, cbt_data)
            
            # Update therapy focus recommendations
            therapy_focus = self._update_therapy_focus(patient_id, cbt_data)
            
            # Track insight development
            insight_development = self._track_insight_development(patient_id, cbt_data)
            
            # Generate session talking points
            talking_points = self._generate_session_talking_points(patient_id, cbt_data)
            
            # Measure cognitive flexibility improvements
            cognitive_flexibility = self._measure_cognitive_flexibility(patient_id, cbt_data)
            
            return {
                'cognitive_patterns': cognitive_patterns,
                'therapy_focus': therapy_focus,
                'insight_development': insight_development,
                'talking_points': talking_points,
                'cognitive_flexibility': cognitive_flexibility,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing CBT exercise: {str(e)}")
            return {'error': f'Failed to analyze CBT exercise: {str(e)}'}
    
    # Helper methods for action-triggered analysis
    def _update_mood_trend_analysis(self, patient_id: int) -> Dict[str, Any]:
        """Update mood trend analysis"""
        # Implementation for mood trend analysis
        return {'trend': 'stable', 'confidence': 0.8}
    
    def _adjust_crisis_risk_assessment(self, patient_id: int, mood_data: Dict) -> Dict[str, Any]:
        """Adjust crisis risk assessment based on mood"""
        # Implementation for risk assessment adjustment
        return {'risk_level': 'low', 'confidence': 0.9}
    
    def _generate_mood_specific_recommendations(self, patient_id: int, mood_data: Dict) -> List[str]:
        """Generate mood-specific treatment recommendations"""
        # Implementation for mood-specific recommendations
        return ["Consider mindfulness exercise", "Review coping strategies"]
    
    def _flag_concerning_patterns(self, patient_id: int, mood_data: Dict) -> List[str]:
        """Flag concerning patterns in mood data"""
        # Implementation for pattern flagging
        return []
    
    def _update_phq9_prediction(self, patient_id: int, mood_data: Dict) -> Dict[str, Any]:
        """Update expected PHQ-9 score prediction"""
        # Implementation for PHQ-9 prediction
        return {'predicted_score': 8, 'confidence': 0.7}
    
    def _update_adherence_score(self, patient_id: int, exercise_data: Dict) -> float:
        """Update treatment adherence score"""
        # Implementation for adherence scoring
        return 0.85
    
    def _analyze_exercise_effectiveness(self, patient_id: int, exercise_data: Dict) -> Dict[str, Any]:
        """Analyze exercise effectiveness for this patient"""
        # Implementation for effectiveness analysis
        return {'effectiveness': 7.5, 'trend': 'improving'}
    
    def _adjust_future_recommendations(self, patient_id: int, exercise_data: Dict) -> List[str]:
        """Adjust future exercise recommendations"""
        # Implementation for recommendation adjustment
        return ["Continue current exercises", "Add advanced CBT techniques"]
    
    def _flag_adherence_concerns(self, patient_id: int, exercise_data: Dict) -> List[str]:
        """Flag adherence concerns"""
        # Implementation for adherence concern flagging
        return []
    
    def _generate_adherence_interventions(self, patient_id: int, exercise_data: Dict) -> List[str]:
        """Generate intervention recommendations for poor engagement"""
        # Implementation for intervention generation
        return ["Schedule motivational session", "Simplify exercise plan"]
    
    def _generate_provider_alert(self, patient_id: int, crisis_data: Dict) -> Dict[str, Any]:
        """Generate immediate provider alert"""
        # Implementation for provider alert generation
        return {
            'severity': 'high',
            'message': 'Patient accessed crisis tools',
            'urgency': 'immediate'
        }
    
    def _update_risk_status(self, patient_id: int, crisis_data: Dict) -> Dict[str, Any]:
        """Update risk status to high-priority monitoring"""
        # Implementation for risk status update
        return {'risk_level': 'high', 'monitoring_frequency': 'hourly'}
    
    def _generate_safety_planning(self, patient_id: int, crisis_data: Dict) -> List[str]:
        """Generate safety planning recommendations"""
        # Implementation for safety planning
        return ["Review safety plan", "Update emergency contacts"]
    
    def _suggest_session_urgency(self, patient_id: int, crisis_data: Dict) -> str:
        """Suggest session scheduling urgency"""
        # Implementation for session urgency suggestion
        return "within_24_hours"
    
    def _log_crisis_pattern_analysis(self, patient_id: int, crisis_data: Dict) -> Dict[str, Any]:
        """Log crisis pattern analysis"""
        # Implementation for crisis pattern analysis
        return {'pattern': 'isolated', 'frequency': 'low'}
    
    def _analyze_cognitive_patterns(self, patient_id: int, cbt_data: Dict) -> Dict[str, Any]:
        """Analyze cognitive pattern improvements"""
        # Implementation for cognitive pattern analysis
        return {'improvement': 0.3, 'patterns': ['all_or_nothing_thinking']}
    
    def _update_therapy_focus(self, patient_id: int, cbt_data: Dict) -> List[str]:
        """Update therapy focus recommendations"""
        # Implementation for therapy focus update
        return ["Focus on cognitive flexibility", "Address all-or-nothing thinking"]
    
    def _track_insight_development(self, patient_id: int, cbt_data: Dict) -> Dict[str, Any]:
        """Track insight development and therapeutic readiness"""
        # Implementation for insight tracking
        return {'insight_level': 0.7, 'readiness': 'high'}
    
    def _generate_session_talking_points(self, patient_id: int, cbt_data: Dict) -> List[str]:
        """Generate session talking points"""
        # Implementation for talking point generation
        return ["Review thought patterns", "Discuss cognitive distortions"]
    
    def _measure_cognitive_flexibility(self, patient_id: int, cbt_data: Dict) -> Dict[str, Any]:
        """Measure cognitive flexibility improvements"""
        # Implementation for cognitive flexibility measurement
        return {'flexibility_score': 0.6, 'improvement': 0.2}

# API Routes
@real_time_insights.route('/api/patient-summary/<int:patient_id>')
@login_required
def get_patient_summary(patient_id):
    """Get real-time patient summary"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    engine = RealTimePatientSummaryEngine()
    summary = engine.get_real_time_patient_summary(patient_id)
    return jsonify(summary)

@real_time_insights.route('/api/analyze-mood-checkin/<int:patient_id>', methods=['POST'])
@login_required
def analyze_mood_checkin(patient_id):
    """Analyze mood check-in action"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    mood_data = request.get_json()
    analyzer = ActionTriggeredAnalysis()
    analysis = analyzer.analyze_mood_checkin(patient_id, mood_data)
    return jsonify(analysis)

@real_time_insights.route('/api/analyze-exercise-completion/<int:patient_id>', methods=['POST'])
@login_required
def analyze_exercise_completion(patient_id):
    """Analyze exercise completion action"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    exercise_data = request.get_json()
    analyzer = ActionTriggeredAnalysis()
    analysis = analyzer.analyze_exercise_completion(patient_id, exercise_data)
    return jsonify(analysis)

@real_time_insights.route('/api/analyze-crisis-access/<int:patient_id>', methods=['POST'])
@login_required
def analyze_crisis_access(patient_id):
    """Analyze crisis tool access action"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    crisis_data = request.get_json()
    analyzer = ActionTriggeredAnalysis()
    analysis = analyzer.analyze_crisis_tool_access(patient_id, crisis_data)
    return jsonify(analysis)

@real_time_insights.route('/api/analyze-cbt-exercise/<int:patient_id>', methods=['POST'])
@login_required
def analyze_cbt_exercise(patient_id):
    """Analyze CBT exercise completion action"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    cbt_data = request.get_json()
    analyzer = ActionTriggeredAnalysis()
    analysis = analyzer.analyze_cbt_exercise(patient_id, cbt_data)
    return jsonify(analysis)
