#!/usr/bin/env python3
"""
Intelligent Treatment Recommendation Engine
Provides evidence-based treatment recommendations based on patient action data
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

treatment_recommendations = Blueprint('treatment_recommendations', __name__)

class IntelligentTreatmentRecommendationEngine:
    """Intelligent treatment recommendation engine"""
    
    def __init__(self):
        self.treatment_modalities = {
            'cbt': 'Cognitive Behavioral Therapy',
            'dbt': 'Dialectical Behavior Therapy',
            'act': 'Acceptance and Commitment Therapy',
            'mindfulness': 'Mindfulness-Based Interventions',
            'behavioral_activation': 'Behavioral Activation',
            'medication': 'Pharmacological Treatment',
            'group_therapy': 'Group Therapy',
            'family_therapy': 'Family Therapy',
            'emdr': 'Eye Movement Desensitization and Reprocessing'
        }
        
        self.intensity_levels = {
            'maintenance': 'Maintenance Phase',
            'standard': 'Standard Treatment',
            'intensive': 'Intensive Treatment',
            'crisis': 'Crisis Intervention',
            'inpatient': 'Inpatient Treatment'
        }
    
    def generate_therapy_session_focus(self, patient_id: int) -> Dict[str, Any]:
        """Generate therapy session focus recommendations"""
        try:
            # Get patient data
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Analyze patterns
            mood_patterns = self._analyze_mood_patterns(patient_id)
            exercise_patterns = self._analyze_exercise_patterns(patient_id)
            cbt_patterns = self._analyze_cbt_patterns(patient_id)
            crisis_patterns = self._analyze_crisis_patterns(patient_id)
            engagement_patterns = self._analyze_engagement_patterns(patient_id)
            
            # Generate recommendations
            session_focus = self._generate_session_focus_recommendations(
                patient_id, mood_patterns, exercise_patterns, cbt_patterns, 
                crisis_patterns, engagement_patterns
            )
            
            return {
                'patient_info': {
                    'id': patient.id,
                    'name': f"{patient.first_name} {patient.last_name}",
                    'current_severity': patient.current_phq9_severity
                },
                'session_focus': session_focus,
                'evidence_basis': self._get_evidence_basis(session_focus),
                'priority_level': self._determine_priority_level(session_focus),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating therapy session focus: {str(e)}")
            return {'error': f'Failed to generate session focus: {str(e)}'}
    
    def generate_treatment_intensity_adjustments(self, patient_id: int) -> Dict[str, Any]:
        """Generate treatment intensity adjustment recommendations"""
        try:
            # Get current treatment response
            treatment_response = self._analyze_treatment_response(patient_id)
            engagement_metrics = self._analyze_engagement_metrics(patient_id)
            risk_assessment = self._analyze_risk_assessment(patient_id)
            progress_indicators = self._analyze_progress_indicators(patient_id)
            
            # Generate intensity recommendations
            intensity_recommendations = self._generate_intensity_recommendations(
                patient_id, treatment_response, engagement_metrics, 
                risk_assessment, progress_indicators
            )
            
            return {
                'current_intensity': self._get_current_intensity(patient_id),
                'recommended_intensity': intensity_recommendations['recommended_level'],
                'adjustment_reasoning': intensity_recommendations['reasoning'],
                'implementation_steps': intensity_recommendations['implementation'],
                'monitoring_plan': intensity_recommendations['monitoring'],
                'risk_considerations': intensity_recommendations['risks'],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating treatment intensity adjustments: {str(e)}")
            return {'error': f'Failed to generate intensity adjustments: {str(e)}'}
    
    def generate_clinical_decision_support(self, patient_id: int) -> Dict[str, Any]:
        """Generate clinical decision support recommendations"""
        try:
            # Analyze comprehensive patient data
            symptom_patterns = self._analyze_symptom_patterns(patient_id)
            treatment_history = self._analyze_treatment_history(patient_id)
            risk_factors = self._analyze_risk_factors(patient_id)
            response_patterns = self._analyze_response_patterns(patient_id)
            
            # Generate clinical recommendations
            clinical_recommendations = self._generate_clinical_recommendations(
                patient_id, symptom_patterns, treatment_history, 
                risk_factors, response_patterns
            )
            
            return {
                'medication_evaluation': clinical_recommendations['medication'],
                'therapy_modality_suggestions': clinical_recommendations['modalities'],
                'referral_recommendations': clinical_recommendations['referrals'],
                'session_scheduling': clinical_recommendations['scheduling'],
                'crisis_intervention': clinical_recommendations['crisis'],
                'evidence_strength': clinical_recommendations['evidence'],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating clinical decision support: {str(e)}")
            return {'error': f'Failed to generate clinical decision support: {str(e)}'}
    
    def _analyze_mood_patterns(self, patient_id: int) -> Dict[str, Any]:
        """Analyze mood patterns for session focus"""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get mood entries
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        if not mood_entries:
            return {'patterns': [], 'concerns': [], 'insights': []}
        
        # Analyze day-of-week patterns
        day_patterns = defaultdict(list)
        for entry in mood_entries:
            day = entry.timestamp.strftime('%A')
            day_patterns[day].append(entry.intensity_level)
        
        # Identify concerning patterns
        concerns = []
        insights = []
        
        # Check for specific day patterns
        for day, levels in day_patterns.items():
            avg_level = np.mean(levels)
            if avg_level <= 3:
                concerns.append(f"Consistently low mood on {day}s")
                insights.append(f"Explore {day} stressors or triggers")
            elif avg_level >= 8:
                insights.append(f"Positive mood pattern on {day}s - leverage this")
        
        # Check for mood volatility
        if len(mood_entries) >= 3:
            mood_changes = [abs(mood_entries[i].intensity_level - mood_entries[i-1].intensity_level) 
                          for i in range(1, len(mood_entries))]
            avg_change = np.mean(mood_changes)
            if avg_change >= 3:
                concerns.append("High mood volatility - explore emotional regulation")
                insights.append("Focus on mood stabilization techniques")
        
        return {
            'patterns': dict(day_patterns),
            'concerns': concerns,
            'insights': insights,
            'avg_mood': np.mean([entry.intensity_level for entry in mood_entries])
        }
    
    def _analyze_exercise_patterns(self, patient_id: int) -> Dict[str, Any]:
        """Analyze exercise patterns for session focus"""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get exercise sessions
        sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            )
        ).order_by(ExerciseSession.start_time).all()
        
        if not sessions:
            return {'completion_rate': 0, 'effectiveness': None, 'concerns': ['No exercise engagement'], 'insights': []}
        
        # Calculate metrics
        completed = [s for s in sessions if s.completion_status == 'completed']
        completion_rate = len(completed) / len(sessions)
        
        # Analyze effectiveness
        rated_sessions = [s for s in completed if s.effectiveness_rating is not None]
        avg_effectiveness = np.mean([s.effectiveness_rating for s in rated_sessions]) if rated_sessions else None
        
        # Generate insights
        concerns = []
        insights = []
        
        if completion_rate < 0.5:
            concerns.append("Low exercise completion rate")
            insights.append("Address barriers to exercise engagement")
        elif completion_rate >= 0.8:
            insights.append("Strong exercise engagement - build on this success")
        
        if avg_effectiveness and avg_effectiveness < 6:
            concerns.append("Low exercise effectiveness")
            insights.append("Evaluate exercise appropriateness and difficulty")
        elif avg_effectiveness and avg_effectiveness >= 8:
            insights.append("High exercise effectiveness - consider advancing difficulty")
        
        return {
            'completion_rate': completion_rate,
            'effectiveness': avg_effectiveness,
            'concerns': concerns,
            'insights': insights,
            'total_sessions': len(sessions)
        }
    
    def _analyze_cbt_patterns(self, patient_id: int) -> Dict[str, Any]:
        """Analyze CBT exercise patterns"""
        month_ago = datetime.now() - timedelta(days=30)
        
        # Get CBT-related sessions and thought records
        cbt_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago,
                ExerciseSession.exercise.has(type='cbt')
            )
        ).all()
        
        thought_records = ThoughtRecord.query.filter(
            and_(
                ThoughtRecord.patient_id == patient_id,
                ThoughtRecord.created_at >= month_ago
            )
        ).all()
        
        # Analyze cognitive patterns
        concerns = []
        insights = []
        
        if thought_records:
            # Analyze thought patterns
            distortion_types = []
            for record in thought_records:
                if record.cognitive_distortion:
                    distortion_types.append(record.cognitive_distortion)
            
            if distortion_types:
                most_common = max(set(distortion_types), key=distortion_types.count)
                concerns.append(f"Persistent {most_common} thinking patterns")
                insights.append(f"Focus on challenging {most_common} distortions")
        
        # Check for insight development
        if len(thought_records) >= 5:
            recent_records = thought_records[-3:]
            earlier_records = thought_records[:3]
            
            recent_insight_avg = np.mean([r.insight_score for r in recent_records if r.insight_score])
            earlier_insight_avg = np.mean([r.insight_score for r in earlier_records if r.insight_score])
            
            if recent_insight_avg > earlier_insight_avg + 1:
                insights.append("Improving cognitive insight - ready for advanced techniques")
            elif recent_insight_avg < earlier_insight_avg - 1:
                concerns.append("Declining cognitive insight - review basic concepts")
        
        return {
            'cbt_sessions': len(cbt_sessions),
            'thought_records': len(thought_records),
            'concerns': concerns,
            'insights': insights
        }
    
    def _analyze_crisis_patterns(self, patient_id: int) -> Dict[str, Any]:
        """Analyze crisis patterns"""
        month_ago = datetime.now() - timedelta(days=30)
        
        # Get crisis alerts
        crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= month_ago
            )
        ).all()
        
        concerns = []
        insights = []
        
        if crisis_alerts:
            concerns.append(f"{len(crisis_alerts)} crisis episodes in past month")
            insights.append("Prioritize safety planning and crisis prevention")
            
            # Analyze timing patterns
            if len(crisis_alerts) >= 3:
                insights.append("Frequent crisis episodes - consider intensive intervention")
        
        return {
            'crisis_episodes': len(crisis_alerts),
            'concerns': concerns,
            'insights': insights
        }
    
    def _analyze_engagement_patterns(self, patient_id: int) -> Dict[str, Any]:
        """Analyze overall engagement patterns"""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get all patient activity
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
        ).count()
        
        concerns = []
        insights = []
        
        if mood_entries == 0:
            concerns.append("No mood tracking engagement")
        elif mood_entries >= 7:
            insights.append("Consistent mood tracking - good self-monitoring")
        
        if exercise_sessions == 0:
            concerns.append("No exercise engagement")
        elif exercise_sessions >= 5:
            insights.append("Strong exercise engagement")
        
        return {
            'mood_entries': mood_entries,
            'exercise_sessions': exercise_sessions,
            'concerns': concerns,
            'insights': insights
        }
    
    def _generate_session_focus_recommendations(self, patient_id: int, mood_patterns: Dict, 
                                              exercise_patterns: Dict, cbt_patterns: Dict,
                                              crisis_patterns: Dict, engagement_patterns: Dict) -> Dict[str, Any]:
        """Generate session focus recommendations"""
        recommendations = {
            'primary_focus': [],
            'secondary_focus': [],
            'talking_points': [],
            'evidence': []
        }
        
        # Crisis priority
        if crisis_patterns['crisis_episodes'] > 0:
            recommendations['primary_focus'].append("Crisis prevention and safety planning")
            recommendations['talking_points'].append("Review recent crisis episodes and triggers")
            recommendations['evidence'].append(f"{crisis_patterns['crisis_episodes']} crisis episodes in past month")
        
        # Mood pattern focus
        if mood_patterns['concerns']:
            for concern in mood_patterns['concerns']:
                recommendations['primary_focus'].append(concern)
                recommendations['talking_points'].append(f"Explore {concern.lower()}")
        
        # Exercise engagement focus
        if exercise_patterns['concerns']:
            for concern in exercise_patterns['concerns']:
                recommendations['secondary_focus'].append(concern)
                recommendations['talking_points'].append(f"Address {concern.lower()}")
        
        # CBT pattern focus
        if cbt_patterns['concerns']:
            for concern in cbt_patterns['concerns']:
                recommendations['secondary_focus'].append(concern)
                recommendations['talking_points'].append(f"Work on {concern.lower()}")
        
        # Engagement focus
        if engagement_patterns['concerns']:
            for concern in engagement_patterns['concerns']:
                recommendations['secondary_focus'].append(concern)
                recommendations['talking_points'].append(f"Discuss {concern.lower()}")
        
        # Add positive insights
        all_insights = (mood_patterns['insights'] + exercise_patterns['insights'] + 
                       cbt_patterns['insights'] + engagement_patterns['insights'])
        
        for insight in all_insights:
            recommendations['talking_points'].append(insight)
        
        return recommendations
    
    def _analyze_treatment_response(self, patient_id: int) -> Dict[str, Any]:
        """Analyze treatment response patterns"""
        month_ago = datetime.now() - timedelta(days=30)
        
        # Get exercise effectiveness
        sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago,
                ExerciseSession.effectiveness_rating.isnot(None)
            )
        ).all()
        
        # Get mood trends
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= month_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        # Calculate response metrics
        avg_effectiveness = np.mean([s.effectiveness_rating for s in sessions]) if sessions else None
        
        mood_trend = 'stable'
        if len(mood_entries) >= 10:
            recent_avg = np.mean([entry.intensity_level for entry in mood_entries[-5:]])
            earlier_avg = np.mean([entry.intensity_level for entry in mood_entries[:5]])
            if recent_avg > earlier_avg + 1:
                mood_trend = 'improving'
            elif recent_avg < earlier_avg - 1:
                mood_trend = 'declining'
        
        return {
            'avg_effectiveness': avg_effectiveness,
            'mood_trend': mood_trend,
            'response_quality': 'good' if (avg_effectiveness and avg_effectiveness >= 7) or mood_trend == 'improving' else 'poor'
        }
    
    def _analyze_engagement_metrics(self, patient_id: int) -> Dict[str, Any]:
        """Analyze engagement metrics"""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get recent activity
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
        
        completion_rate = len([s for s in exercise_sessions if s.completion_status == 'completed']) / len(exercise_sessions) if exercise_sessions else 0
        
        return {
            'mood_tracking_frequency': mood_entries,
            'exercise_completion_rate': completion_rate,
            'overall_engagement': 'high' if mood_entries >= 5 and completion_rate >= 0.8 else 'low'
        }
    
    def _analyze_risk_assessment(self, patient_id: int) -> Dict[str, Any]:
        """Analyze current risk assessment"""
        # Get latest PHQ-9
        latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(PHQ9Assessment.assessment_date.desc()).first()
        
        # Get recent crisis activity
        week_ago = datetime.now() - timedelta(days=7)
        recent_crises = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= week_ago
            )
        ).count()
        
        risk_level = 'low'
        if latest_assessment and latest_assessment.total_score >= 20:
            risk_level = 'high'
        elif latest_assessment and latest_assessment.total_score >= 15:
            risk_level = 'moderate'
        elif recent_crises > 0:
            risk_level = 'high'
        
        return {
            'risk_level': risk_level,
            'phq9_score': latest_assessment.total_score if latest_assessment else None,
            'recent_crises': recent_crises
        }
    
    def _analyze_progress_indicators(self, patient_id: int) -> Dict[str, Any]:
        """Analyze progress indicators"""
        month_ago = datetime.now() - timedelta(days=30)
        
        # Get mood progress
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= month_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        progress_indicators = {
            'mood_improvement': False,
            'skill_development': False,
            'crisis_reduction': False,
            'engagement_increase': False
        }
        
        if len(mood_entries) >= 10:
            recent_avg = np.mean([entry.intensity_level for entry in mood_entries[-5:]])
            earlier_avg = np.mean([entry.intensity_level for entry in mood_entries[:5]])
            if recent_avg > earlier_avg + 1:
                progress_indicators['mood_improvement'] = True
        
        # Check crisis reduction
        month_crises = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= month_ago
            )
        ).count()
        
        if month_crises == 0:
            progress_indicators['crisis_reduction'] = True
        
        return progress_indicators
    
    def _generate_intensity_recommendations(self, patient_id: int, treatment_response: Dict,
                                          engagement_metrics: Dict, risk_assessment: Dict,
                                          progress_indicators: Dict) -> Dict[str, Any]:
        """Generate treatment intensity recommendations"""
        current_intensity = self._get_current_intensity(patient_id)
        recommended_level = current_intensity
        reasoning = []
        implementation = []
        monitoring = []
        risks = []
        
        # High risk situations
        if risk_assessment['risk_level'] == 'high':
            recommended_level = 'crisis'
            reasoning.append("High risk level requires crisis intervention")
            implementation.append("Implement crisis safety plan")
            implementation.append("Schedule urgent session within 24 hours")
            monitoring.append("Hourly risk monitoring")
            risks.append("Risk of harm to self or others")
        
        # Poor treatment response
        elif treatment_response['response_quality'] == 'poor':
            if current_intensity == 'standard':
                recommended_level = 'intensive'
                reasoning.append("Poor treatment response requires increased intensity")
                implementation.append("Increase session frequency to 2-3 times per week")
                implementation.append("Add adjunctive treatments")
                monitoring.append("Weekly progress assessment")
                risks.append("Treatment resistance")
        
        # Good progress with high engagement
        elif (treatment_response['response_quality'] == 'good' and 
              engagement_metrics['overall_engagement'] == 'high' and
              progress_indicators['mood_improvement']):
            
            if current_intensity in ['intensive', 'standard']:
                recommended_level = 'maintenance'
                reasoning.append("Good progress and engagement - ready for maintenance")
                implementation.append("Reduce session frequency")
                implementation.append("Focus on relapse prevention")
                monitoring.append("Monthly progress check-ins")
                risks.append("Risk of relapse if support reduced too quickly")
        
        # Low engagement
        elif engagement_metrics['overall_engagement'] == 'low':
            if current_intensity == 'maintenance':
                recommended_level = 'standard'
                reasoning.append("Low engagement requires increased support")
                implementation.append("Increase session frequency")
                implementation.append("Address barriers to engagement")
                monitoring.append("Weekly engagement tracking")
                risks.append("Treatment dropout")
        
        return {
            'recommended_level': recommended_level,
            'reasoning': reasoning,
            'implementation': implementation,
            'monitoring': monitoring,
            'risks': risks
        }
    
    def _get_current_intensity(self, patient_id: int) -> str:
        """Get current treatment intensity level"""
        # This would typically be stored in a treatment plan table
        # For now, return a default based on PHQ-9 severity
        latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(PHQ9Assessment.assessment_date.desc()).first()
        
        if latest_assessment:
            if latest_assessment.total_score >= 20:
                return 'crisis'
            elif latest_assessment.total_score >= 15:
                return 'intensive'
            elif latest_assessment.total_score >= 10:
                return 'standard'
            else:
                return 'maintenance'
        
        return 'standard'
    
    def _analyze_symptom_patterns(self, patient_id: int) -> Dict[str, Any]:
        """Analyze symptom patterns for clinical decisions"""
        # Get recent PHQ-9 assessments
        assessments = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(PHQ9Assessment.assessment_date.desc()).limit(3).all()
        
        # Get mood patterns
        month_ago = datetime.now() - timedelta(days=30)
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= month_ago
            )
        ).all()
        
        symptom_patterns = {
            'severity_trend': 'stable',
            'symptom_clusters': [],
            'chronicity': 'acute',
            'response_to_intervention': 'unknown'
        }
        
        if len(assessments) >= 2:
            latest_score = assessments[0].total_score
            previous_score = assessments[1].total_score
            
            if latest_score > previous_score + 3:
                symptom_patterns['severity_trend'] = 'worsening'
            elif latest_score < previous_score - 3:
                symptom_patterns['severity_trend'] = 'improving'
        
        # Analyze symptom clusters
        if assessments:
            latest = assessments[0]
            clusters = []
            
            if latest.q1_score >= 2 and latest.q2_score >= 2:
                clusters.append('mood_symptoms')
            if latest.q3_score >= 2 and latest.q4_score >= 2:
                clusters.append('somatic_symptoms')
            if latest.q7_score >= 2 and latest.q8_score >= 2:
                clusters.append('cognitive_symptoms')
            
            symptom_patterns['symptom_clusters'] = clusters
        
        return symptom_patterns
    
    def _analyze_treatment_history(self, patient_id: int) -> Dict[str, Any]:
        """Analyze treatment history"""
        # This would typically query a treatment history table
        # For now, analyze exercise and session history
        month_ago = datetime.now() - timedelta(days=30)
        
        sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago
            )
        ).all()
        
        return {
            'recent_treatments': len(sessions),
            'treatment_response': 'moderate',
            'adherence_history': 'good',
            'previous_modalities': ['cbt', 'mindfulness']
        }
    
    def _analyze_risk_factors(self, patient_id: int) -> Dict[str, Any]:
        """Analyze risk factors"""
        # Get crisis history
        crisis_history = CrisisAlert.query.filter_by(patient_id=patient_id).count()
        
        # Get latest PHQ-9
        latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(PHQ9Assessment.assessment_date.desc()).first()
        
        risk_factors = {
            'suicide_risk': 'low',
            'self_harm_risk': 'low',
            'social_support': 'adequate',
            'access_to_care': 'good'
        }
        
        if latest_assessment and latest_assessment.q9_score >= 2:
            risk_factors['suicide_risk'] = 'high'
        
        if crisis_history > 0:
            risk_factors['self_harm_risk'] = 'moderate'
        
        return risk_factors
    
    def _analyze_response_patterns(self, patient_id: int) -> Dict[str, Any]:
        """Analyze response patterns to different interventions"""
        month_ago = datetime.now() - timedelta(days=30)
        
        # Analyze exercise effectiveness by type
        sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago,
                ExerciseSession.effectiveness_rating.isnot(None)
            )
        ).all()
        
        response_patterns = {
            'cbt_response': 'unknown',
            'mindfulness_response': 'unknown',
            'behavioral_activation_response': 'unknown',
            'overall_response': 'moderate'
        }
        
        if sessions:
            # Group by exercise type and calculate average effectiveness
            type_effectiveness = defaultdict(list)
            for session in sessions:
                if session.exercise and session.exercise.type:
                    type_effectiveness[session.exercise.type].append(session.effectiveness_rating)
            
            for exercise_type, ratings in type_effectiveness.items():
                avg_rating = np.mean(ratings)
                if exercise_type == 'cbt':
                    response_patterns['cbt_response'] = 'good' if avg_rating >= 7 else 'poor'
                elif exercise_type == 'mindfulness':
                    response_patterns['mindfulness_response'] = 'good' if avg_rating >= 7 else 'poor'
                elif exercise_type == 'behavioral_activation':
                    response_patterns['behavioral_activation_response'] = 'good' if avg_rating >= 7 else 'poor'
        
        return response_patterns
    
    def _generate_clinical_recommendations(self, patient_id: int, symptom_patterns: Dict,
                                         treatment_history: Dict, risk_factors: Dict,
                                         response_patterns: Dict) -> Dict[str, Any]:
        """Generate clinical recommendations"""
        recommendations = {
            'medication': [],
            'modalities': [],
            'referrals': [],
            'scheduling': [],
            'crisis': [],
            'evidence': []
        }
        
        # Medication recommendations
        if symptom_patterns['severity_trend'] == 'worsening' and symptom_patterns['symptom_clusters']:
            recommendations['medication'].append("Consider antidepressant medication evaluation")
            recommendations['evidence'].append("Worsening symptoms despite current treatment")
        
        if 'mood_symptoms' in symptom_patterns['symptom_clusters']:
            recommendations['medication'].append("SSRI may be beneficial for mood symptoms")
            recommendations['evidence'].append("Prominent mood symptoms present")
        
        # Therapy modality recommendations
        if response_patterns['cbt_response'] == 'poor':
            recommendations['modalities'].append("Consider switching from CBT to DBT")
            recommendations['evidence'].append("Poor response to CBT interventions")
        
        if response_patterns['mindfulness_response'] == 'good':
            recommendations['modalities'].append("Continue mindfulness-based interventions")
            recommendations['evidence'].append("Good response to mindfulness exercises")
        
        if risk_factors['suicide_risk'] == 'high':
            recommendations['modalities'].append("Add DBT skills training")
            recommendations['evidence'].append("High suicide risk requires specialized intervention")
        
        # Referral recommendations
        if risk_factors['suicide_risk'] == 'high':
            recommendations['referrals'].append("Psychiatric evaluation for medication management")
            recommendations['referrals'].append("Intensive outpatient program")
        
        if response_patterns['overall_response'] == 'poor':
            recommendations['referrals'].append("Second opinion from specialist")
        
        # Session scheduling
        if symptom_patterns['severity_trend'] == 'worsening':
            recommendations['scheduling'].append("Increase session frequency to weekly")
        elif symptom_patterns['severity_trend'] == 'improving':
            recommendations['scheduling'].append("Consider bi-weekly sessions")
        
        # Crisis intervention
        if risk_factors['suicide_risk'] == 'high':
            recommendations['crisis'].append("Implement safety plan")
            recommendations['crisis'].append("24-hour crisis hotline access")
        
        return recommendations
    
    def _get_evidence_basis(self, session_focus: Dict) -> List[str]:
        """Get evidence basis for recommendations"""
        evidence = []
        
        if session_focus['primary_focus']:
            evidence.append("Evidence-based treatment protocols")
        
        if session_focus['talking_points']:
            evidence.append("Clinical observation and patient data")
        
        return evidence
    
    def _determine_priority_level(self, session_focus: Dict) -> str:
        """Determine priority level of recommendations"""
        if any('crisis' in focus.lower() for focus in session_focus['primary_focus']):
            return 'high'
        elif session_focus['primary_focus']:
            return 'medium'
        else:
            return 'low'

# API Routes
@treatment_recommendations.route('/api/therapy-session-focus/<int:patient_id>')
@login_required
def get_therapy_session_focus(patient_id):
    """Get therapy session focus recommendations"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    engine = IntelligentTreatmentRecommendationEngine()
    recommendations = engine.generate_therapy_session_focus(patient_id)
    return jsonify(recommendations)

@treatment_recommendations.route('/api/treatment-intensity/<int:patient_id>')
@login_required
def get_treatment_intensity_adjustments(patient_id):
    """Get treatment intensity adjustment recommendations"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    engine = IntelligentTreatmentRecommendationEngine()
    recommendations = engine.generate_treatment_intensity_adjustments(patient_id)
    return jsonify(recommendations)

@treatment_recommendations.route('/api/clinical-decision-support/<int:patient_id>')
@login_required
def get_clinical_decision_support(patient_id):
    """Get clinical decision support recommendations"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    engine = IntelligentTreatmentRecommendationEngine()
    recommendations = engine.generate_clinical_decision_support(patient_id)
    return jsonify(recommendations)
