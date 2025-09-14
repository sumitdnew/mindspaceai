#!/usr/bin/env python3
"""
Clinical Progress Measurement Analytics
Tracks mood stability, skill acquisition, and behavioral changes
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import numpy as np
from sqlalchemy import func, and_, desc, extract
from collections import defaultdict
import pandas as pd

# Import will be done after models are defined
# from app_ml_complete import db, Patient, MindfulnessSession, MoodEntry, PHQ9Assessment

clinical_analytics = Blueprint('clinical_analytics', __name__)

class ClinicalProgressAnalytics:
    """Clinical progress measurement and analysis"""
    
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.analysis_period = 30  # days
    
    def get_clinical_progress_analytics(self):
        """2. CLINICAL PROGRESS MEASUREMENT"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.analysis_period)
        
        analytics = {
            'mood_stability': self._analyze_mood_stability(start_date, end_date),
            'skill_acquisition': self._analyze_skill_acquisition(start_date, end_date),
            'crisis_intervention': self._analyze_crisis_intervention_usage(start_date, end_date),
            'self_awareness': self._analyze_self_awareness_development(start_date, end_date),
            'behavioral_changes': self._analyze_behavioral_changes(start_date, end_date)
        }
        
        return analytics
    
    def _analyze_mood_stability(self, start_date, end_date):
        """Mood stability improvements correlated with exercise usage"""
        # Get mood entries
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == self.patient_id,
                MoodEntry.timestamp >= start_date,
                MoodEntry.timestamp <= end_date
            )
        ).order_by(MoodEntry.timestamp).all()
        
        # Get mindfulness sessions
        mindfulness_sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date
            )
        ).all()
        
        if not mood_entries:
            return {
                'mood_variability': 0,
                'mood_trend': 'stable',
                'exercise_correlation': 0,
                'stability_improvement': 0
            }
        
        # Calculate mood variability
        mood_scores = [entry.intensity_level for entry in mood_entries]
        mood_variability = np.std(mood_scores)
        
        # Calculate mood trend
        if len(mood_scores) >= 2:
            mood_trend_slope = np.polyfit(range(len(mood_scores)), mood_scores, 1)[0]
            if mood_trend_slope > 0.1:
                mood_trend = 'improving'
            elif mood_trend_slope < -0.1:
                mood_trend = 'declining'
            else:
                mood_trend = 'stable'
        else:
            mood_trend = 'stable'
        
        # Correlate with exercise usage
        exercise_correlation = self._calculate_exercise_mood_correlation(mood_entries, mindfulness_sessions)
        
        # Calculate stability improvement
        stability_improvement = self._calculate_stability_improvement(mood_entries)
        
        return {
            'mood_variability': round(mood_variability, 2),
            'mood_trend': mood_trend,
            'exercise_correlation': round(exercise_correlation, 3),
            'stability_improvement': round(stability_improvement, 2),
            'total_mood_entries': len(mood_entries),
            'avg_mood_score': round(np.mean(mood_scores), 2)
        }
    
    def _calculate_exercise_mood_correlation(self, mood_entries, mindfulness_sessions):
        """Calculate correlation between exercise usage and mood"""
        if not mood_entries or not mindfulness_sessions:
            return 0
        
        # Create daily exercise count
        exercise_by_date = defaultdict(int)
        for session in mindfulness_sessions:
            date = session.start_time.date()
            exercise_by_date[date] += 1
        
        # Create daily mood averages
        mood_by_date = defaultdict(list)
        for entry in mood_entries:
            date = entry.timestamp.date()
            mood_by_date[date].append(entry.intensity_level)
        
        # Calculate daily averages
        daily_mood_avg = {}
        for date, scores in mood_by_date.items():
            daily_mood_avg[date] = np.mean(scores)
        
        # Find common dates
        common_dates = set(exercise_by_date.keys()) & set(daily_mood_avg.keys())
        if len(common_dates) < 3:
            return 0
        
        # Calculate correlation
        exercise_counts = [exercise_by_date[date] for date in common_dates]
        mood_scores = [daily_mood_avg[date] for date in common_dates]
        
        try:
            correlation = np.corrcoef(exercise_counts, mood_scores)[0, 1]
            return correlation if not np.isnan(correlation) else 0
        except:
            return 0
    
    def _calculate_stability_improvement(self, mood_entries):
        """Calculate mood stability improvement over time"""
        if len(mood_entries) < 10:
            return 0
        
        # Split into two periods
        mid_point = len(mood_entries) // 2
        early_scores = [entry.intensity_level for entry in mood_entries[:mid_point]]
        late_scores = [entry.intensity_level for entry in mood_entries[mid_point:]]
        
        early_variability = np.std(early_scores)
        late_variability = np.std(late_scores)
        
        if early_variability == 0:
            return 0
        
        # Improvement is reduction in variability
        improvement = (early_variability - late_variability) / early_variability
        return improvement
    
    def _analyze_skill_acquisition(self, start_date, end_date):
        """Skill acquisition rates (CBT, mindfulness, etc.)"""
        # Get mindfulness sessions with effectiveness ratings
        mindfulness_sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date,
                MindfulnessSession.technique_effectiveness.isnot(None)
            )
        ).order_by(MindfulnessSession.start_time).all()
        
        if not mindfulness_sessions:
            return {
                'skill_progression': 'beginner',
                'effectiveness_trend': 'stable',
                'skill_mastery_level': 0,
                'learning_curve': []
            }
        
        # Analyze effectiveness progression
        effectiveness_scores = [s.technique_effectiveness for s in mindfulness_sessions]
        
        # Calculate learning curve
        if len(effectiveness_scores) >= 3:
            learning_curve_slope = np.polyfit(range(len(effectiveness_scores)), effectiveness_scores, 1)[0]
            
            if learning_curve_slope > 0.2:
                effectiveness_trend = 'improving'
            elif learning_curve_slope < -0.2:
                effectiveness_trend = 'declining'
            else:
                effectiveness_trend = 'stable'
        else:
            effectiveness_trend = 'stable'
        
        # Determine skill progression level
        avg_effectiveness = np.mean(effectiveness_scores)
        if avg_effectiveness >= 8:
            skill_progression = 'advanced'
        elif avg_effectiveness >= 6:
            skill_progression = 'intermediate'
        else:
            skill_progression = 'beginner'
        
        # Calculate skill mastery level (0-100%)
        skill_mastery_level = min(100, (avg_effectiveness / 10) * 100)
        
        # Create learning curve data
        learning_curve = []
        for i, score in enumerate(effectiveness_scores):
            learning_curve.append({
                'session_number': i + 1,
                'effectiveness': score,
                'date': mindfulness_sessions[i].start_time.strftime('%Y-%m-%d')
            })
        
        return {
            'skill_progression': skill_progression,
            'effectiveness_trend': effectiveness_trend,
            'skill_mastery_level': round(skill_mastery_level, 1),
            'learning_curve': learning_curve,
            'total_sessions_analyzed': len(mindfulness_sessions),
            'avg_effectiveness': round(avg_effectiveness, 2)
        }
    
    def _analyze_crisis_intervention_usage(self, start_date, end_date):
        """Crisis intervention usage reduction over time"""
        # Get PHQ-9 assessments with crisis flags
        phq9_assessments = PHQ9Assessment.query.filter(
            and_(
                PHQ9Assessment.patient_id == self.patient_id,
                PHQ9Assessment.assessment_date >= start_date,
                PHQ9Assessment.assessment_date <= end_date
            )
        ).order_by(PHQ9Assessment.assessment_date).all()
        
        if not phq9_assessments:
            return {
                'crisis_usage_trend': 'stable',
                'crisis_reduction_rate': 0,
                'risk_level_trend': 'stable',
                'intervention_effectiveness': 0
            }
        
        # Analyze crisis flags over time
        crisis_flags = [assessment.q9_risk_flag for assessment in phq9_assessments]
        crisis_count = sum(crisis_flags)
        
        # Calculate crisis reduction
        if len(crisis_flags) >= 2:
            early_crisis_rate = sum(crisis_flags[:len(crisis_flags)//2]) / (len(crisis_flags)//2)
            late_crisis_rate = sum(crisis_flags[len(crisis_flags)//2:]) / (len(crisis_flags)//2)
            
            if early_crisis_rate > 0:
                crisis_reduction_rate = (early_crisis_rate - late_crisis_rate) / early_crisis_rate
            else:
                crisis_reduction_rate = 0
        else:
            crisis_reduction_rate = 0
        
        # Analyze risk level trends
        risk_scores = [assessment.total_score for assessment in phq9_assessments]
        if len(risk_scores) >= 3:
            risk_trend_slope = np.polyfit(range(len(risk_scores)), risk_scores, 1)[0]
            if risk_trend_slope < -1:
                risk_level_trend = 'improving'
            elif risk_trend_slope > 1:
                risk_level_trend = 'worsening'
            else:
                risk_level_trend = 'stable'
        else:
            risk_level_trend = 'stable'
        
        # Determine crisis usage trend
        if crisis_reduction_rate > 0.2:
            crisis_usage_trend = 'decreasing'
        elif crisis_reduction_rate < -0.2:
            crisis_usage_trend = 'increasing'
        else:
            crisis_usage_trend = 'stable'
        
        return {
            'crisis_usage_trend': crisis_usage_trend,
            'crisis_reduction_rate': round(crisis_reduction_rate, 3),
            'risk_level_trend': risk_level_trend,
            'intervention_effectiveness': round((1 - crisis_reduction_rate) * 100, 1),
            'total_crisis_episodes': crisis_count,
            'total_assessments': len(phq9_assessments)
        }
    
    def _analyze_self_awareness_development(self, start_date, end_date):
        """Self-awareness development through exercise progression"""
        # Get mindfulness sessions with attention checks and breathing consistency
        mindfulness_sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date,
                MindfulnessSession.attention_checks_passed.isnot(None)
            )
        ).order_by(MindfulnessSession.start_time).all()
        
        if not mindfulness_sessions:
            return {
                'awareness_level': 'developing',
                'attention_improvement': 0,
                'mindfulness_depth': 0,
                'self_observation_skills': 0
            }
        
        # Analyze attention check progression
        attention_scores = [s.attention_checks_passed for s in mindfulness_sessions]
        breathing_scores = [s.breathing_consistency for s in mindfulness_sessions if s.breathing_consistency]
        
        # Calculate attention improvement
        if len(attention_scores) >= 2:
            early_attention = np.mean(attention_scores[:len(attention_scores)//2])
            late_attention = np.mean(attention_scores[len(attention_scores)//2:])
            attention_improvement = (late_attention - early_attention) / max(early_attention, 1)
        else:
            attention_improvement = 0
        
        # Calculate mindfulness depth
        avg_attention = np.mean(attention_scores)
        avg_breathing = np.mean(breathing_scores) if breathing_scores else 5
        
        mindfulness_depth = (avg_attention + avg_breathing) / 2
        
        # Determine awareness level
        if mindfulness_depth >= 8:
            awareness_level = 'advanced'
        elif mindfulness_depth >= 6:
            awareness_level = 'intermediate'
        else:
            awareness_level = 'developing'
        
        # Calculate self-observation skills
        self_observation_skills = min(100, (mindfulness_depth / 10) * 100)
        
        return {
            'awareness_level': awareness_level,
            'attention_improvement': round(attention_improvement, 3),
            'mindfulness_depth': round(mindfulness_depth, 2),
            'self_observation_skills': round(self_observation_skills, 1),
            'avg_attention_score': round(avg_attention, 2),
            'avg_breathing_consistency': round(avg_breathing, 2)
        }
    
    def _analyze_behavioral_changes(self, start_date, end_date):
        """Behavioral change evidence through activity tracking"""
        # This would integrate with activity tracking data
        # For now, we'll analyze mindfulness session patterns as behavioral indicators
        
        mindfulness_sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date
            )
        ).order_by(MindfulnessSession.start_time).all()
        
        if not mindfulness_sessions:
            return {
                'behavioral_consistency': 0,
                'habit_formation': 'early_stages',
                'lifestyle_integration': 0,
                'behavioral_improvements': []
            }
        
        # Analyze behavioral consistency
        sessions_by_date = defaultdict(int)
        for session in mindfulness_sessions:
            date = session.start_time.date()
            sessions_by_date[date] += 1
        
        consistency_score = len(sessions_by_date) / self.analysis_period
        
        # Determine habit formation stage
        if consistency_score >= 0.7:
            habit_formation = 'established'
        elif consistency_score >= 0.4:
            habit_formation = 'developing'
        else:
            habit_formation = 'early_stages'
        
        # Calculate lifestyle integration
        lifestyle_integration = min(100, consistency_score * 100)
        
        # Identify behavioral improvements
        behavioral_improvements = []
        if consistency_score > 0.5:
            behavioral_improvements.append("Consistent daily practice")
        
        if len(mindfulness_sessions) >= 10:
            behavioral_improvements.append("Sustained engagement over time")
        
        completed_sessions = [s for s in mindfulness_sessions if s.completion_status == 'completed']
        if len(completed_sessions) / len(mindfulness_sessions) > 0.8:
            behavioral_improvements.append("High completion rate")
        
        return {
            'behavioral_consistency': round(consistency_score, 3),
            'habit_formation': habit_formation,
            'lifestyle_integration': round(lifestyle_integration, 1),
            'behavioral_improvements': behavioral_improvements,
            'total_practice_days': len(sessions_by_date),
            'avg_sessions_per_day': round(len(mindfulness_sessions) / len(sessions_by_date), 2) if sessions_by_date else 0
        }

# API Routes for Clinical Analytics
@clinical_analytics.route('/api/analytics/clinical-progress/<int:patient_id>')
@login_required
def get_clinical_progress_analytics(patient_id):
    """Get comprehensive clinical progress analytics"""
    # Verify user has access to this patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    analytics = ClinicalProgressAnalytics(patient_id)
    return jsonify(analytics.get_clinical_progress_analytics())

if __name__ == '__main__':
    print("Clinical Progress Analytics System Loaded")
