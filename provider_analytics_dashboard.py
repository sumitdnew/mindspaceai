#!/usr/bin/env python3
"""
Provider Analytics Dashboard
Comprehensive patient exercise analytics and clinical insights for providers
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import numpy as np
from sqlalchemy import func, and_, desc, extract
from collections import defaultdict
import pandas as pd

# Import will be done after models are defined
# from app_ml_complete import db, Patient, MindfulnessSession, MoodEntry, PHQ9Assessment

provider_analytics = Blueprint('provider_analytics', __name__)

class ProviderAnalyticsDashboard:
    """Provider dashboard for patient exercise analytics"""
    
    def __init__(self):
        self.analysis_period = 30  # days
    
    def get_provider_dashboard_data(self):
        """5. PROVIDER DASHBOARD"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.analysis_period)
        
        dashboard_data = {
            'patient_overview': self._get_patient_exercise_overview(start_date, end_date),
            'clinical_progress_indicators': self._get_clinical_progress_indicators(start_date, end_date),
            'risk_alert_system': self._get_risk_alert_system(start_date, end_date),
            'treatment_effectiveness': self._get_treatment_effectiveness_measurement(start_date, end_date),
            'evidence_based_recommendations': self._get_evidence_based_recommendations(start_date, end_date)
        }
        
        return dashboard_data
    
    def _get_patient_exercise_overview(self, start_date, end_date):
        """Patient exercise engagement overview"""
        # Get all patients with their exercise data
        patients = Patient.query.all()
        
        patient_overview = []
        for patient in patients:
            # Get patient's mindfulness sessions
            sessions = MindfulnessSession.query.filter(
                and_(
                    MindfulnessSession.patient_id == patient.id,
                    MindfulnessSession.start_time >= start_date,
                    MindfulnessSession.start_time <= end_date
                )
            ).all()
            
            # Calculate engagement metrics
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.completion_status == 'completed'])
            completion_rate = completed_sessions / total_sessions if total_sessions > 0 else 0
            
            # Calculate average session duration
            avg_duration = 0
            if completed_sessions > 0:
                durations = [s.duration_actual or s.duration_planned for s in sessions if s.completion_status == 'completed']
                avg_duration = np.mean(durations) if durations else 0
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(sessions)
            
            # Get recent activity
            last_session = sessions[-1] if sessions else None
            last_activity = last_session.start_time.strftime('%Y-%m-%d %H:%M') if last_session else 'No recent activity'
            
            # Determine engagement status
            if engagement_score >= 0.8:
                engagement_status = 'high'
            elif engagement_score >= 0.5:
                engagement_status = 'moderate'
            else:
                engagement_status = 'low'
            
            patient_overview.append({
                'patient_id': patient.id,
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'total_sessions': total_sessions,
                'completion_rate': round(completion_rate, 3),
                'avg_session_duration': round(avg_duration, 1),
                'engagement_score': round(engagement_score, 3),
                'engagement_status': engagement_status,
                'last_activity': last_activity,
                'days_since_last_session': (end_date - last_session.start_time).days if last_session else None
            })
        
        # Sort by engagement score
        patient_overview.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        return {
            'patients': patient_overview,
            'total_patients': len(patients),
            'high_engagement_count': len([p for p in patient_overview if p['engagement_status'] == 'high']),
            'moderate_engagement_count': len([p for p in patient_overview if p['engagement_status'] == 'moderate']),
            'low_engagement_count': len([p for p in patient_overview if p['engagement_status'] == 'low'])
        }
    
    def _calculate_engagement_score(self, sessions):
        """Calculate comprehensive engagement score"""
        if not sessions:
            return 0
        
        # Factors for engagement score
        completion_rate = len([s for s in sessions if s.completion_status == 'completed']) / len(sessions)
        
        # Frequency factor (sessions per week)
        if len(sessions) > 0:
            first_session = min(sessions, key=lambda x: x.start_time)
            last_session = max(sessions, key=lambda x: x.start_time)
            days_span = (last_session.start_time - first_session.start_time).days
            sessions_per_week = (len(sessions) * 7) / max(days_span, 1)
            frequency_factor = min(sessions_per_week / 5, 1)  # Normalize to 5 sessions per week
        else:
            frequency_factor = 0
        
        # Duration factor
        completed_sessions = [s for s in sessions if s.completion_status == 'completed']
        if completed_sessions:
            avg_duration = np.mean([s.duration_actual or s.duration_planned for s in completed_sessions])
            duration_factor = min(avg_duration / 10, 1)  # Normalize to 10 minutes
        else:
            duration_factor = 0
        
        # Effectiveness factor
        rated_sessions = [s for s in sessions if s.technique_effectiveness]
        if rated_sessions:
            avg_effectiveness = np.mean([s.technique_effectiveness for s in rated_sessions])
            effectiveness_factor = avg_effectiveness / 10
        else:
            effectiveness_factor = 0.5  # Default if no ratings
        
        # Calculate weighted engagement score
        engagement_score = (
            completion_rate * 0.3 +
            frequency_factor * 0.3 +
            duration_factor * 0.2 +
            effectiveness_factor * 0.2
        )
        
        return engagement_score
    
    def _get_clinical_progress_indicators(self, start_date, end_date):
        """Clinical progress indicators and trend analysis"""
        patients = Patient.query.all()
        
        clinical_progress = []
        for patient in patients:
            # Get patient's sessions and mood data
            sessions = MindfulnessSession.query.filter(
                and_(
                    MindfulnessSession.patient_id == patient.id,
                    MindfulnessSession.start_time >= start_date,
                    MindfulnessSession.start_time <= end_date
                )
            ).all()
            
            mood_entries = MoodEntry.query.filter(
                and_(
                    MoodEntry.patient_id == patient.id,
                    MoodEntry.timestamp >= start_date,
                    MoodEntry.timestamp <= end_date
                )
            ).all()
            
            # Calculate clinical indicators
            mood_stability = self._calculate_mood_stability(mood_entries)
            skill_progression = self._calculate_skill_progression(sessions)
            behavioral_consistency = self._calculate_behavioral_consistency(sessions)
            
            # Determine overall progress
            progress_score = (mood_stability + skill_progression + behavioral_consistency) / 3
            
            if progress_score >= 0.7:
                progress_status = 'excellent'
            elif progress_score >= 0.5:
                progress_status = 'good'
            elif progress_score >= 0.3:
                progress_status = 'moderate'
            else:
                progress_status = 'needs_attention'
            
            clinical_progress.append({
                'patient_id': patient.id,
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'mood_stability': round(mood_stability, 3),
                'skill_progression': round(skill_progression, 3),
                'behavioral_consistency': round(behavioral_consistency, 3),
                'progress_score': round(progress_score, 3),
                'progress_status': progress_status,
                'trend': self._determine_progress_trend(sessions, mood_entries)
            })
        
        # Sort by progress score
        clinical_progress.sort(key=lambda x: x['progress_score'], reverse=True)
        
        return {
            'patients': clinical_progress,
            'excellent_progress_count': len([p for p in clinical_progress if p['progress_status'] == 'excellent']),
            'good_progress_count': len([p for p in clinical_progress if p['progress_status'] == 'good']),
            'moderate_progress_count': len([p for p in clinical_progress if p['progress_status'] == 'moderate']),
            'needs_attention_count': len([p for p in clinical_progress if p['progress_status'] == 'needs_attention'])
        }
    
    def _calculate_mood_stability(self, mood_entries):
        """Calculate mood stability score"""
        if len(mood_entries) < 5:
            return 0.5  # Default if insufficient data
        
        mood_scores = [entry.intensity_level for entry in mood_entries]
        mood_variability = np.std(mood_scores)
        
        # Lower variability = higher stability
        stability_score = max(0, 1 - (mood_variability / 5))  # Normalize to 0-1
        return stability_score
    
    def _calculate_skill_progression(self, sessions):
        """Calculate skill progression score"""
        if len(sessions) < 3:
            return 0.5  # Default if insufficient data
        
        # Get effectiveness ratings over time
        rated_sessions = [s for s in sessions if s.technique_effectiveness]
        if len(rated_sessions) < 3:
            return 0.5
        
        # Calculate trend in effectiveness
        effectiveness_scores = [s.technique_effectiveness for s in rated_sessions]
        if len(effectiveness_scores) >= 3:
            trend_slope = np.polyfit(range(len(effectiveness_scores)), effectiveness_scores, 1)[0]
            # Normalize trend to 0-1 scale
            progression_score = max(0, min(1, (trend_slope + 2) / 4))
        else:
            progression_score = 0.5
        
        return progression_score
    
    def _calculate_behavioral_consistency(self, sessions):
        """Calculate behavioral consistency score"""
        if not sessions:
            return 0
        
        # Calculate consistency factors
        completion_rate = len([s for s in sessions if s.completion_status == 'completed']) / len(sessions)
        
        # Frequency consistency
        sessions_by_date = defaultdict(int)
        for session in sessions:
            date = session.start_time.date()
            sessions_by_date[date] += 1
        
        if len(sessions_by_date) > 0:
            frequency_variability = np.std(list(sessions_by_date.values()))
            frequency_consistency = max(0, 1 - (frequency_variability / 3))
        else:
            frequency_consistency = 0
        
        # Overall consistency score
        consistency_score = (completion_rate + frequency_consistency) / 2
        return consistency_score
    
    def _determine_progress_trend(self, sessions, mood_entries):
        """Determine overall progress trend"""
        if not sessions and not mood_entries:
            return 'stable'
        
        # Analyze session trend
        session_trend = 'stable'
        if len(sessions) >= 4:
            # Group by week and analyze trend
            sessions_by_week = defaultdict(int)
            for session in sessions:
                week_start = session.start_time - timedelta(days=session.start_time.weekday())
                week_key = week_start.strftime('%Y-%W')
                sessions_by_week[week_key] += 1
            
            weekly_counts = list(sessions_by_week.values())
            if len(weekly_counts) >= 2:
                recent_avg = np.mean(weekly_counts[-2:])
                earlier_avg = np.mean(weekly_counts[:-2]) if len(weekly_counts) > 2 else weekly_counts[0]
                
                if recent_avg > earlier_avg * 1.2:
                    session_trend = 'improving'
                elif recent_avg < earlier_avg * 0.8:
                    session_trend = 'declining'
        
        # Analyze mood trend
        mood_trend = 'stable'
        if len(mood_entries) >= 5:
            mood_scores = [entry.intensity_level for entry in mood_entries]
            if len(mood_scores) >= 3:
                mood_slope = np.polyfit(range(len(mood_scores)), mood_scores, 1)[0]
                if mood_slope > 0.1:
                    mood_trend = 'improving'
                elif mood_slope < -0.1:
                    mood_trend = 'declining'
        
        # Combine trends
        if session_trend == 'improving' and mood_trend == 'improving':
            return 'strongly_improving'
        elif session_trend == 'improving' or mood_trend == 'improving':
            return 'improving'
        elif session_trend == 'declining' and mood_trend == 'declining':
            return 'declining'
        elif session_trend == 'declining' or mood_trend == 'declining':
            return 'slightly_declining'
        else:
            return 'stable'
    
    def _get_risk_alert_system(self, start_date, end_date):
        """Risk alert system with severity levels"""
        patients = Patient.query.all()
        
        risk_alerts = []
        for patient in patients:
            # Get patient's sessions and mood data
            sessions = MindfulnessSession.query.filter(
                and_(
                    MindfulnessSession.patient_id == patient.id,
                    MindfulnessSession.start_time >= start_date,
                    MindfulnessSession.start_time <= end_date
                )
            ).all()
            
            mood_entries = MoodEntry.query.filter(
                and_(
                    MoodEntry.patient_id == patient.id,
                    MoodEntry.timestamp >= start_date,
                    MoodEntry.timestamp <= end_date
                )
            ).all()
            
            # Analyze risk factors
            risk_factors = self._analyze_risk_factors(sessions, mood_entries)
            
            # Calculate overall risk level
            overall_risk = self._calculate_overall_risk_level(risk_factors)
            
            if overall_risk['level'] != 'low':
                risk_alerts.append({
                    'patient_id': patient.id,
                    'patient_name': f"{patient.first_name} {patient.last_name}",
                    'risk_level': overall_risk['level'],
                    'risk_score': overall_risk['score'],
                    'risk_factors': risk_factors,
                    'recommended_actions': overall_risk['recommended_actions'],
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
                })
        
        # Sort by risk level (critical, high, moderate)
        risk_level_order = {'critical': 0, 'high': 1, 'moderate': 2}
        risk_alerts.sort(key=lambda x: risk_level_order.get(x['risk_level'], 3))
        
        return {
            'alerts': risk_alerts,
            'critical_count': len([a for a in risk_alerts if a['risk_level'] == 'critical']),
            'high_count': len([a for a in risk_alerts if a['risk_level'] == 'high']),
            'moderate_count': len([a for a in risk_alerts if a['risk_level'] == 'moderate'])
        }
    
    def _analyze_risk_factors(self, sessions, mood_entries):
        """Analyze individual risk factors"""
        risk_factors = {}
        
        # Engagement drop risk
        if len(sessions) >= 5:
            recent_sessions = sessions[-5:]
            earlier_sessions = sessions[:-5] if len(sessions) > 5 else []
            
            if earlier_sessions:
                recent_avg = len(recent_sessions) / 5  # Last 5 sessions
                earlier_avg = len(earlier_sessions) / max(len(earlier_sessions), 1)
                
                if recent_avg < earlier_avg * 0.5:  # 50% drop
                    risk_factors['engagement_drop'] = {
                        'severity': 'high' if recent_avg < earlier_avg * 0.3 else 'moderate',
                        'description': f"Engagement dropped by {((earlier_avg - recent_avg) / earlier_avg * 100):.1f}%"
                    }
        
        # Low mood risk
        if mood_entries:
            recent_mood_entries = mood_entries[-10:] if len(mood_entries) >= 10 else mood_entries
            avg_mood = np.mean([entry.intensity_level for entry in recent_mood_entries])
            
            if avg_mood < 4:
                risk_factors['low_mood'] = {
                    'severity': 'critical' if avg_mood < 2 else 'high' if avg_mood < 3 else 'moderate',
                    'description': f"Average mood: {avg_mood:.1f}/10"
                }
        
        # Session abandonment risk
        if sessions:
            abandoned_sessions = [s for s in sessions if s.completion_status == 'abandoned']
            abandonment_rate = len(abandoned_sessions) / len(sessions)
            
            if abandonment_rate > 0.5:
                risk_factors['session_abandonment'] = {
                    'severity': 'high' if abandonment_rate > 0.8 else 'moderate',
                    'description': f"Session abandonment rate: {abandonment_rate:.1%}"
                }
        
        return risk_factors
    
    def _calculate_overall_risk_level(self, risk_factors):
        """Calculate overall risk level and recommended actions"""
        if not risk_factors:
            return {'level': 'low', 'score': 0, 'recommended_actions': []}
        
        # Calculate risk score
        severity_scores = {'moderate': 1, 'high': 2, 'critical': 3}
        total_score = sum(severity_scores.get(factor['severity'], 0) for factor in risk_factors.values())
        max_possible_score = len(risk_factors) * 3
        
        risk_percentage = total_score / max_possible_score
        
        # Determine risk level
        if risk_percentage >= 0.7:
            risk_level = 'critical'
        elif risk_percentage >= 0.4:
            risk_level = 'high'
        else:
            risk_level = 'moderate'
        
        # Generate recommended actions
        recommended_actions = []
        for factor_type, factor_data in risk_factors.items():
            if factor_type == 'engagement_drop':
                recommended_actions.append("Reach out to understand barriers to engagement")
            elif factor_type == 'low_mood':
                recommended_actions.append("Assess current mental health status and crisis risk")
            elif factor_type == 'session_abandonment':
                recommended_actions.append("Review exercise difficulty and provide additional support")
        
        return {
            'level': risk_level,
            'score': round(risk_percentage, 3),
            'recommended_actions': recommended_actions
        }
    
    def _get_treatment_effectiveness_measurement(self, start_date, end_date):
        """Treatment effectiveness measurement"""
        patients = Patient.query.all()
        
        treatment_effectiveness = []
        for patient in patients:
            # Get patient's sessions and mood data
            sessions = MindfulnessSession.query.filter(
                and_(
                    MindfulnessSession.patient_id == patient.id,
                    MindfulnessSession.start_time >= start_date,
                    MindfulnessSession.start_time <= end_date
                )
            ).all()
            
            mood_entries = MoodEntry.query.filter(
                and_(
                    MoodEntry.patient_id == patient.id,
                    MoodEntry.timestamp >= start_date,
                    MoodEntry.timestamp <= end_date
                )
            ).all()
            
            # Calculate effectiveness metrics
            effectiveness_metrics = self._calculate_effectiveness_metrics(sessions, mood_entries)
            
            treatment_effectiveness.append({
                'patient_id': patient.id,
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'effectiveness_score': effectiveness_metrics['overall_score'],
                'mood_improvement': effectiveness_metrics['mood_improvement'],
                'skill_development': effectiveness_metrics['skill_development'],
                'behavioral_change': effectiveness_metrics['behavioral_change'],
                'recommendations': effectiveness_metrics['recommendations']
            })
        
        # Sort by effectiveness score
        treatment_effectiveness.sort(key=lambda x: x['effectiveness_score'], reverse=True)
        
        return {
            'patients': treatment_effectiveness,
            'avg_effectiveness_score': np.mean([p['effectiveness_score'] for p in treatment_effectiveness]) if treatment_effectiveness else 0,
            'high_effectiveness_count': len([p for p in treatment_effectiveness if p['effectiveness_score'] >= 0.7]),
            'moderate_effectiveness_count': len([p for p in treatment_effectiveness if 0.4 <= p['effectiveness_score'] < 0.7]),
            'low_effectiveness_count': len([p for p in treatment_effectiveness if p['effectiveness_score'] < 0.4])
        }
    
    def _calculate_effectiveness_metrics(self, sessions, mood_entries):
        """Calculate treatment effectiveness metrics"""
        # Mood improvement
        mood_improvement = 0
        if len(mood_entries) >= 10:
            early_mood = np.mean([entry.intensity_level for entry in mood_entries[:5]])
            recent_mood = np.mean([entry.intensity_level for entry in mood_entries[-5:]])
            mood_improvement = max(0, (recent_mood - early_mood) / 10)
        
        # Skill development
        skill_development = 0
        if len(sessions) >= 5:
            rated_sessions = [s for s in sessions if s.technique_effectiveness]
            if len(rated_sessions) >= 3:
                effectiveness_scores = [s.technique_effectiveness for s in rated_sessions]
                skill_development = np.mean(effectiveness_scores) / 10
        
        # Behavioral change
        behavioral_change = 0
        if sessions:
            completion_rate = len([s for s in sessions if s.completion_status == 'completed']) / len(sessions)
            behavioral_change = completion_rate
        
        # Overall effectiveness score
        overall_score = (mood_improvement + skill_development + behavioral_change) / 3
        
        # Generate recommendations
        recommendations = []
        if mood_improvement < 0.1:
            recommendations.append("Focus on mood stabilization techniques")
        if skill_development < 0.5:
            recommendations.append("Provide additional skill-building exercises")
        if behavioral_change < 0.6:
            recommendations.append("Address barriers to consistent practice")
        
        return {
            'overall_score': round(overall_score, 3),
            'mood_improvement': round(mood_improvement, 3),
            'skill_development': round(skill_development, 3),
            'behavioral_change': round(behavioral_change, 3),
            'recommendations': recommendations
        }
    
    def _get_evidence_based_recommendations(self, start_date, end_date):
        """Evidence-based recommendation updates"""
        # This would integrate with research database and clinical guidelines
        # For now, we'll provide general evidence-based recommendations
        
        recommendations = {
            'general_guidelines': [
                "Daily mindfulness practice of 10-20 minutes shows optimal benefits",
                "Consistent timing (same time each day) improves habit formation",
                "Progressive difficulty increases maintain engagement",
                "Combining breathing and meditation exercises enhances effectiveness"
            ],
            'clinical_insights': [
                "Patients with high anxiety benefit most from box breathing",
                "Depression symptoms improve with longer meditation sessions",
                "Stress reduction correlates with consistent daily practice",
                "Crisis exercises should be used sparingly to maintain effectiveness"
            ],
            'engagement_strategies': [
                "Personalized exercise recommendations increase completion rates",
                "Gamification elements improve long-term engagement",
                "Social support features enhance motivation",
                "Progress tracking and feedback boost adherence"
            ]
        }
        
        return recommendations

# Provider Dashboard Routes
@provider_analytics.route('/provider/dashboard')
@login_required
def provider_dashboard():
    """Provider analytics dashboard main page"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    dashboard = ProviderAnalyticsDashboard()
    dashboard_data = dashboard.get_provider_dashboard_data()
    
    return render_template('provider_analytics_dashboard.html', data=dashboard_data)

@provider_analytics.route('/api/provider/dashboard-data')
@login_required
def get_provider_dashboard_data():
    """Get provider dashboard data as JSON"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    dashboard = ProviderAnalyticsDashboard()
    return jsonify(dashboard.get_provider_dashboard_data())

if __name__ == '__main__':
    print("Provider Analytics Dashboard System Loaded")
