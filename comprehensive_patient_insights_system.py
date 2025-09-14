#!/usr/bin/env python3
"""
Comprehensive Patient Action Analysis & Provider Insight System
Unified system that transforms every patient interaction into actionable clinical intelligence
"""

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import numpy as np
from sqlalchemy import func, and_, desc, extract
from collections import defaultdict
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

# Import database models
from app_ml_complete import (
    db, Patient, PHQ9Assessment, ExerciseSession, MoodEntry, 
    CrisisAlert, MindfulnessSession, MicroAssessment, ThoughtRecord
)

comprehensive_insights = Blueprint('comprehensive_insights', __name__)

class ComprehensivePatientInsightsSystem:
    """Comprehensive system that transforms patient actions into provider insights"""
    
    def __init__(self):
        self.risk_levels = {
            'green': {'min': 0, 'max': 4, 'color': '#28a745'},
            'yellow': {'min': 5, 'max': 9, 'color': '#ffc107'},
            'orange': {'min': 10, 'max': 14, 'color': '#fd7e14'},
            'red': {'min': 15, 'max': 27, 'color': '#dc3545'}
        }
    
    def get_comprehensive_patient_insights(self, patient_id: int) -> Dict[str, Any]:
        """Get comprehensive patient insights and recommendations"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Generate all insights
            real_time_summary = self._get_real_time_patient_summary(patient_id)
            treatment_recommendations = self._get_treatment_recommendations(patient_id)
            session_preparation = self._get_session_preparation_data(patient_id)
            crisis_management = self._get_crisis_management_insights(patient_id)
            treatment_documentation = self._get_treatment_documentation_support(patient_id)
            
            return {
                'patient_info': {
                    'id': patient.id,
                    'name': f"{patient.first_name} {patient.last_name}",
                    'current_severity': patient.current_phq9_severity,
                    'last_assessment_date': patient.last_assessment_date.isoformat() if patient.last_assessment_date else None
                },
                'real_time_summary': real_time_summary,
                'treatment_recommendations': treatment_recommendations,
                'session_preparation': session_preparation,
                'crisis_management': crisis_management,
                'treatment_documentation': treatment_documentation,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating comprehensive insights: {str(e)}")
            return {'error': f'Failed to generate insights: {str(e)}'}
    
    def process_patient_action(self, patient_id: int, action_type: str, action_data: Dict) -> Dict[str, Any]:
        """Process a patient action and generate immediate insights"""
        try:
            if action_type == 'mood_checkin':
                return self._process_mood_checkin(patient_id, action_data)
            elif action_type == 'exercise_completion':
                return self._process_exercise_completion(patient_id, action_data)
            elif action_type == 'crisis_access':
                return self._process_crisis_access(patient_id, action_data)
            elif action_type == 'cbt_exercise':
                return self._process_cbt_exercise(patient_id, action_data)
            else:
                return {'error': f'Unknown action type: {action_type}'}
                
        except Exception as e:
            logging.error(f"Error processing patient action: {str(e)}")
            return {'error': f'Failed to process action: {str(e)}'}
    
    def _get_real_time_patient_summary(self, patient_id: int) -> Dict[str, Any]:
        """Get real-time patient summary"""
        today = datetime.now().date()
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get current mood state
        today_mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                func.date(MoodEntry.timestamp) == today
            )
        ).order_by(MoodEntry.timestamp.desc()).all()
        
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
        
        # Get engagement metrics
        today_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                func.date(ExerciseSession.start_time) == today
            )
        ).all()
        
        today_completed = len([s for s in today_sessions if s.completion_status == 'completed'])
        today_skipped = len([s for s in today_sessions if s.completion_status == 'abandoned'])
        
        # Get risk assessment
        latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(PHQ9Assessment.assessment_date.desc()).first()
        
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
        
        # Get weekly trends
        week_mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        mood_trend = 'stable'
        if len(week_mood_entries) >= 4:
            recent_avg = np.mean([entry.intensity_level for entry in week_mood_entries[-3:]])
            earlier_avg = np.mean([entry.intensity_level for entry in week_mood_entries[:3]])
            if recent_avg > earlier_avg + 1:
                mood_trend = 'improving'
            elif recent_avg < earlier_avg - 1:
                mood_trend = 'declining'
        
        return {
            'current_status': {
                'risk_level': current_risk_level,
                'risk_color': risk_color,
                'mood_state': current_mood,
                'treatment_urgency': treatment_urgency
            },
            'today_summary': {
                'mood_check_ins': len(today_mood_entries),
                'exercises_completed': today_completed,
                'exercises_skipped': today_skipped,
                'concerns': self._identify_today_concerns(patient_id)
            },
            'weekly_trends': {
                'mood_trend': mood_trend,
                'overall_trend': 'improving' if mood_trend == 'improving' else 'stable'
            }
        }
    
    def _get_treatment_recommendations(self, patient_id: int) -> Dict[str, Any]:
        """Get treatment recommendations"""
        # Analyze patterns for recommendations
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get mood patterns
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        # Get exercise patterns
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            )
        ).all()
        
        recommendations = {
            'session_focus': [],
            'treatment_adjustments': [],
            'immediate_actions': []
        }
        
        # Generate recommendations based on patterns
        if mood_entries:
            avg_mood = np.mean([entry.intensity_level for entry in mood_entries])
            if avg_mood <= 3:
                recommendations['session_focus'].append("Explore recent stressors and mood triggers")
                recommendations['treatment_adjustments'].append("Increase supportive interventions")
            elif avg_mood >= 8:
                recommendations['session_focus'].append("Build on positive mood and reinforce coping strategies")
        
        if exercise_sessions:
            completion_rate = len([s for s in exercise_sessions if s.completion_status == 'completed']) / len(exercise_sessions)
            if completion_rate < 0.5:
                recommendations['session_focus'].append("Address barriers to exercise engagement")
                recommendations['immediate_actions'].append("Send motivational outreach")
            elif completion_rate >= 0.8:
                recommendations['session_focus'].append("Reinforce successful exercise habits")
        
        return recommendations
    
    def _get_session_preparation_data(self, patient_id: int) -> Dict[str, Any]:
        """Get session preparation data"""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get week overview
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).count()
        
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            )
        ).all()
        
        completed_exercises = len([s for s in exercise_sessions if s.completion_status == 'completed'])
        
        # Generate talking points
        talking_points = []
        
        if mood_entries >= 5:
            talking_points.append("You've been consistent with mood tracking - how is that helping you?")
        elif mood_entries < 3:
            talking_points.append("I notice fewer mood check-ins this week - what's been getting in the way?")
        
        if completed_exercises >= 5:
            talking_points.append("Great job completing your exercises this week - which ones were most helpful?")
        elif completed_exercises < 2:
            talking_points.append("You've had trouble with exercises this week - let's figure out what barriers you're facing")
        
        return {
            'week_overview': {
                'mood_entries': mood_entries,
                'exercises_completed': completed_exercises,
                'total_exercises': len(exercise_sessions)
            },
            'talking_points': talking_points,
            'session_focus': self._suggest_session_focus(patient_id)
        }
    
    def _get_crisis_management_insights(self, patient_id: int) -> Dict[str, Any]:
        """Get crisis management insights"""
        month_ago = datetime.now() - timedelta(days=30)
        
        # Get crisis alerts
        crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= month_ago
            )
        ).all()
        
        crisis_insights = {
            'crisis_episodes': len(crisis_alerts),
            'risk_level': 'low',
            'safety_planning': [],
            'intervention_recommendations': []
        }
        
        if crisis_alerts:
            crisis_insights['risk_level'] = 'high'
            crisis_insights['safety_planning'].append("Review and update safety plan")
            crisis_insights['intervention_recommendations'].append("Implement crisis prevention strategies")
        else:
            crisis_insights['safety_planning'].append("Maintain current safety plan")
            crisis_insights['intervention_recommendations'].append("Continue current crisis prevention approach")
        
        return crisis_insights
    
    def _get_treatment_documentation_support(self, patient_id: int) -> Dict[str, Any]:
        """Get treatment documentation support"""
        month_ago = datetime.now() - timedelta(days=30)
        
        # Get objective measurements
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= month_ago
            )
        ).all()
        
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago
            )
        ).all()
        
        # Calculate metrics
        avg_mood = np.mean([entry.intensity_level for entry in mood_entries]) if mood_entries else None
        completion_rate = len([s for s in exercise_sessions if s.completion_status == 'completed']) / len(exercise_sessions) if exercise_sessions else 0
        
        documentation = {
            'objective_measurements': {
                'avg_mood_level': round(avg_mood, 2) if avg_mood else None,
                'exercise_completion_rate': round(completion_rate, 3),
                'total_sessions': len(exercise_sessions)
            },
            'progress_notes': [
                f"Patient completed {len([s for s in exercise_sessions if s.completion_status == 'completed'])} of {len(exercise_sessions)} assigned exercises",
                f"Average mood level: {round(avg_mood, 2) if avg_mood else 'No data'}/10",
                f"Engagement level: {'High' if completion_rate >= 0.8 else 'Moderate' if completion_rate >= 0.5 else 'Low'}"
            ],
            'outcome_measurements': {
                'functional_improvement': 'Moderate' if avg_mood and avg_mood >= 6 else 'Limited',
                'skill_acquisition': 'Good' if completion_rate >= 0.7 else 'Needs improvement',
                'treatment_goal_progress': 'On track' if completion_rate >= 0.6 else 'Behind schedule'
            }
        }
        
        return documentation
    
    def _process_mood_checkin(self, patient_id: int, mood_data: Dict) -> Dict[str, Any]:
        """Process mood check-in action"""
        # Update mood trend analysis
        mood_trends = self._update_mood_trend_analysis(patient_id)
        
        # Adjust crisis risk assessment
        risk_assessment = self._adjust_crisis_risk_assessment(patient_id, mood_data)
        
        # Generate mood-specific recommendations
        recommendations = self._generate_mood_specific_recommendations(patient_id, mood_data)
        
        # Flag concerning patterns
        concerns = self._flag_concerning_patterns(patient_id, mood_data)
        
        return {
            'action_type': 'mood_checkin',
            'mood_trends': mood_trends,
            'risk_assessment': risk_assessment,
            'recommendations': recommendations,
            'concerns': concerns,
            'processed_at': datetime.now().isoformat()
        }
    
    def _process_exercise_completion(self, patient_id: int, exercise_data: Dict) -> Dict[str, Any]:
        """Process exercise completion action"""
        # Update treatment adherence score
        adherence_score = self._update_adherence_score(patient_id, exercise_data)
        
        # Analyze exercise effectiveness
        effectiveness = self._analyze_exercise_effectiveness(patient_id, exercise_data)
        
        # Adjust future recommendations
        future_recommendations = self._adjust_future_recommendations(patient_id, exercise_data)
        
        return {
            'action_type': 'exercise_completion',
            'adherence_score': adherence_score,
            'effectiveness': effectiveness,
            'future_recommendations': future_recommendations,
            'processed_at': datetime.now().isoformat()
        }
    
    def _process_crisis_access(self, patient_id: int, crisis_data: Dict) -> Dict[str, Any]:
        """Process crisis tool access action"""
        # Generate immediate provider alert
        provider_alert = self._generate_provider_alert(patient_id, crisis_data)
        
        # Update risk status
        risk_status = self._update_risk_status(patient_id, crisis_data)
        
        # Generate safety planning recommendations
        safety_planning = self._generate_safety_planning(patient_id, crisis_data)
        
        return {
            'action_type': 'crisis_access',
            'provider_alert': provider_alert,
            'risk_status': risk_status,
            'safety_planning': safety_planning,
            'processed_at': datetime.now().isoformat()
        }
    
    def _process_cbt_exercise(self, patient_id: int, cbt_data: Dict) -> Dict[str, Any]:
        """Process CBT exercise completion action"""
        # Analyze cognitive pattern improvements
        cognitive_patterns = self._analyze_cognitive_patterns(patient_id, cbt_data)
        
        # Update therapy focus recommendations
        therapy_focus = self._update_therapy_focus(patient_id, cbt_data)
        
        # Generate session talking points
        talking_points = self._generate_session_talking_points(patient_id, cbt_data)
        
        return {
            'action_type': 'cbt_exercise',
            'cognitive_patterns': cognitive_patterns,
            'therapy_focus': therapy_focus,
            'talking_points': talking_points,
            'processed_at': datetime.now().isoformat()
        }
    
    # Helper methods for action processing
    def _identify_today_concerns(self, patient_id: int) -> List[str]:
        """Identify today's concerns"""
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
        
        return concerns
    
    def _suggest_session_focus(self, patient_id: int) -> str:
        """Suggest session focus"""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Check for concerning patterns
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        if len(mood_entries) >= 3:
            recent_avg = np.mean([entry.intensity_level for entry in mood_entries[-3:]])
            earlier_avg = np.mean([entry.intensity_level for entry in mood_entries[:3]])
            if recent_avg < earlier_avg - 2:
                return "mood_stabilization"
        
        return "general_progress"
    
    # Placeholder methods for action processing
    def _update_mood_trend_analysis(self, patient_id: int) -> Dict[str, Any]:
        return {'trend': 'stable', 'confidence': 0.8}
    
    def _adjust_crisis_risk_assessment(self, patient_id: int, mood_data: Dict) -> Dict[str, Any]:
        return {'risk_level': 'low', 'confidence': 0.9}
    
    def _generate_mood_specific_recommendations(self, patient_id: int, mood_data: Dict) -> List[str]:
        return ["Consider mindfulness exercise", "Review coping strategies"]
    
    def _flag_concerning_patterns(self, patient_id: int, mood_data: Dict) -> List[str]:
        return []
    
    def _update_adherence_score(self, patient_id: int, exercise_data: Dict) -> float:
        return 0.85
    
    def _analyze_exercise_effectiveness(self, patient_id: int, exercise_data: Dict) -> Dict[str, Any]:
        return {'effectiveness': 7.5, 'trend': 'improving'}
    
    def _adjust_future_recommendations(self, patient_id: int, exercise_data: Dict) -> List[str]:
        return ["Continue current exercises", "Add advanced CBT techniques"]
    
    def _generate_provider_alert(self, patient_id: int, crisis_data: Dict) -> Dict[str, Any]:
        return {
            'severity': 'high',
            'message': 'Patient accessed crisis tools',
            'urgency': 'immediate'
        }
    
    def _update_risk_status(self, patient_id: int, crisis_data: Dict) -> Dict[str, Any]:
        return {'risk_level': 'high', 'monitoring_frequency': 'hourly'}
    
    def _generate_safety_planning(self, patient_id: int, crisis_data: Dict) -> List[str]:
        return ["Review safety plan", "Update emergency contacts"]
    
    def _analyze_cognitive_patterns(self, patient_id: int, cbt_data: Dict) -> Dict[str, Any]:
        return {'improvement': 0.3, 'patterns': ['all_or_nothing_thinking']}
    
    def _update_therapy_focus(self, patient_id: int, cbt_data: Dict) -> List[str]:
        return ["Focus on cognitive flexibility", "Address all-or-nothing thinking"]
    
    def _generate_session_talking_points(self, patient_id: int, cbt_data: Dict) -> List[str]:
        return ["Review thought patterns", "Discuss cognitive distortions"]

# API Routes
@comprehensive_insights.route('/api/comprehensive-insights/<int:patient_id>')
@login_required
def get_comprehensive_insights(patient_id):
    """Get comprehensive patient insights"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    system = ComprehensivePatientInsightsSystem()
    insights = system.get_comprehensive_patient_insights(patient_id)
    return jsonify(insights)

@comprehensive_insights.route('/api/process-patient-action/<int:patient_id>', methods=['POST'])
@login_required
def process_patient_action(patient_id):
    """Process a patient action and generate insights"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    action_type = data.get('action_type')
    action_data = data.get('action_data', {})
    
    system = ComprehensivePatientInsightsSystem()
    result = system.process_patient_action(patient_id, action_type, action_data)
    return jsonify(result)

@comprehensive_insights.route('/comprehensive-dashboard/<int:patient_id>')
@login_required
def comprehensive_dashboard(patient_id):
    """Comprehensive patient insights dashboard"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    return render_template('comprehensive_patient_dashboard.html', patient_id=patient_id)
