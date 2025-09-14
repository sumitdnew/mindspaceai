#!/usr/bin/env python3
"""
Personalization Algorithms for Exercise Recommendations
Individual exercise effectiveness scoring and adaptive recommendations
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import numpy as np
from sqlalchemy import func, and_, desc, extract
from collections import defaultdict
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle

# Import will be done after models are defined
# from app_ml_complete import db, Patient, MindfulnessSession, MoodEntry, PersonalizationData

personalization = Blueprint('personalization', __name__)

class PersonalizationEngine:
    """Personalization algorithms for exercise recommendations"""
    
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.analysis_period = 30  # days
        self.model_cache = {}
    
    def get_personalized_recommendations(self):
        """3. PERSONALIZATION ALGORITHMS"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.analysis_period)
        
        recommendations = {
            'exercise_effectiveness_scores': self._calculate_exercise_effectiveness_scores(start_date, end_date),
            'optimal_timing': self._calculate_optimal_timing_recommendations(start_date, end_date),
            'difficulty_adaptation': self._calculate_difficulty_adaptation(start_date, end_date),
            'exercise_type_recommendations': self._calculate_exercise_type_recommendations(start_date, end_date),
            'intervention_timing': self._optimize_intervention_timing(start_date, end_date)
        }
        
        return recommendations
    
    def _calculate_exercise_effectiveness_scores(self, start_date, end_date):
        """Individual exercise effectiveness scoring"""
        # Get all mindfulness sessions with effectiveness ratings
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date,
                MindfulnessSession.technique_effectiveness.isnot(None)
            )
        ).all()
        
        if not sessions:
            return {
                'overall_effectiveness': 0,
                'by_exercise_type': {},
                'effectiveness_trend': 'stable',
                'recommended_focus_areas': []
            }
        
        # Calculate overall effectiveness
        effectiveness_scores = [s.technique_effectiveness for s in sessions]
        overall_effectiveness = np.mean(effectiveness_scores)
        
        # Calculate effectiveness by exercise type
        effectiveness_by_type = defaultdict(list)
        for session in sessions:
            effectiveness_by_type[session.exercise_type].append(session.technique_effectiveness)
        
        by_exercise_type = {}
        for exercise_type, scores in effectiveness_by_type.items():
            by_exercise_type[exercise_type] = {
                'avg_effectiveness': round(np.mean(scores), 2),
                'consistency': round(1 - np.std(scores) / np.mean(scores), 2) if np.mean(scores) > 0 else 0,
                'session_count': len(scores)
            }
        
        # Calculate effectiveness trend
        if len(effectiveness_scores) >= 3:
            trend_slope = np.polyfit(range(len(effectiveness_scores)), effectiveness_scores, 1)[0]
            if trend_slope > 0.1:
                effectiveness_trend = 'improving'
            elif trend_slope < -0.1:
                effectiveness_trend = 'declining'
            else:
                effectiveness_trend = 'stable'
        else:
            effectiveness_trend = 'stable'
        
        # Identify recommended focus areas
        recommended_focus_areas = []
        for exercise_type, data in by_exercise_type.items():
            if data['avg_effectiveness'] < 6:
                recommended_focus_areas.append(f"Improve {exercise_type} technique")
            if data['consistency'] < 0.7:
                recommended_focus_areas.append(f"Practice {exercise_type} more consistently")
        
        return {
            'overall_effectiveness': round(overall_effectiveness, 2),
            'by_exercise_type': by_exercise_type,
            'effectiveness_trend': effectiveness_trend,
            'recommended_focus_areas': recommended_focus_areas,
            'total_sessions_analyzed': len(sessions)
        }
    
    def _calculate_optimal_timing_recommendations(self, start_date, end_date):
        """Optimal timing recommendations for each person"""
        # Get sessions with effectiveness ratings
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date,
                MindfulnessSession.technique_effectiveness.isnot(None)
            )
        ).all()
        
        if not sessions:
            return {
                'optimal_hours': [],
                'optimal_days': [],
                'timing_effectiveness': {},
                'recommendations': []
            }
        
        # Analyze effectiveness by hour of day
        effectiveness_by_hour = defaultdict(list)
        for session in sessions:
            hour = session.start_time.hour
            effectiveness_by_hour[hour].append(session.technique_effectiveness)
        
        # Find optimal hours (hours with highest average effectiveness)
        optimal_hours = []
        timing_effectiveness = {}
        
        for hour, scores in effectiveness_by_hour.items():
            avg_effectiveness = np.mean(scores)
            timing_effectiveness[hour] = round(avg_effectiveness, 2)
            
            if avg_effectiveness >= 7:  # High effectiveness threshold
                optimal_hours.append(hour)
        
        # Analyze effectiveness by day of week
        effectiveness_by_day = defaultdict(list)
        for session in sessions:
            day = session.start_time.weekday()
            effectiveness_by_day[day].append(session.technique_effectiveness)
        
        optimal_days = []
        for day, scores in effectiveness_by_day.items():
            if np.mean(scores) >= 7:
                optimal_days.append(day)
        
        # Generate timing recommendations
        recommendations = []
        if optimal_hours:
            hour_names = {6: 'morning', 12: 'midday', 18: 'evening', 21: 'night'}
            for hour in optimal_hours:
                time_name = hour_names.get(hour, f'{hour}:00')
                recommendations.append(f"Practice during {time_name} hours for best results")
        
        if optimal_days:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in optimal_days:
                recommendations.append(f"Schedule sessions on {day_names[day]}s")
        
        if not optimal_hours and not optimal_days:
            recommendations.append("Try different times to find your optimal practice window")
        
        return {
            'optimal_hours': sorted(optimal_hours),
            'optimal_days': sorted(optimal_days),
            'timing_effectiveness': timing_effectiveness,
            'recommendations': recommendations
        }
    
    def _calculate_difficulty_adaptation(self, start_date, end_date):
        """Difficulty level adaptation based on success rates"""
        # Get sessions with completion status and effectiveness
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date
            )
        ).all()
        
        if not sessions:
            return {
                'current_difficulty_level': 'beginner',
                'recommended_difficulty': 'beginner',
                'success_rate': 0,
                'adaptation_recommendations': []
            }
        
        # Define difficulty mapping
        difficulty_mapping = {
            'mindful-breathing': 1,
            'box-breathing': 2,
            '4-7-8-breathing': 3,
            'meditation': 4
        }
        
        # Calculate success rates by difficulty
        success_by_difficulty = defaultdict(lambda: {'total': 0, 'successful': 0})
        for session in sessions:
            difficulty = difficulty_mapping.get(session.exercise_type, 2)
            success_by_difficulty[difficulty]['total'] += 1
            if session.completion_status == 'completed':
                success_by_difficulty[difficulty]['successful'] += 1
        
        # Calculate success rates
        difficulty_success_rates = {}
        for difficulty, data in success_by_difficulty.items():
            if data['total'] > 0:
                success_rate = data['successful'] / data['total']
                difficulty_success_rates[difficulty] = round(success_rate, 2)
        
        # Determine current and recommended difficulty
        current_difficulty = max(difficulty_success_rates.keys()) if difficulty_success_rates else 1
        current_success_rate = difficulty_success_rates.get(current_difficulty, 0)
        
        # Determine recommended difficulty
        if current_success_rate >= 0.8:
            recommended_difficulty = min(5, current_difficulty + 1)
        elif current_success_rate <= 0.4:
            recommended_difficulty = max(1, current_difficulty - 1)
        else:
            recommended_difficulty = current_difficulty
        
        # Generate adaptation recommendations
        adaptation_recommendations = []
        if recommended_difficulty > current_difficulty:
            adaptation_recommendations.append("You're ready to try more challenging exercises")
        elif recommended_difficulty < current_difficulty:
            adaptation_recommendations.append("Consider easier exercises to build confidence")
        else:
            adaptation_recommendations.append("Current difficulty level is appropriate")
        
        difficulty_names = {1: 'beginner', 2: 'intermediate', 3: 'advanced', 4: 'expert', 5: 'master'}
        
        return {
            'current_difficulty_level': difficulty_names.get(current_difficulty, 'beginner'),
            'recommended_difficulty': difficulty_names.get(recommended_difficulty, 'beginner'),
            'success_rate': round(current_success_rate, 2),
            'adaptation_recommendations': adaptation_recommendations,
            'difficulty_success_rates': difficulty_success_rates
        }
    
    def _calculate_exercise_type_recommendations(self, start_date, end_date):
        """Exercise type recommendations based on clinical needs"""
        # Get sessions and mood data
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date
            )
        ).all()
        
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == self.patient_id,
                MoodEntry.timestamp >= start_date,
                MoodEntry.timestamp <= end_date
            )
        ).all()
        
        # Analyze clinical needs based on mood patterns
        clinical_needs = self._analyze_clinical_needs(mood_entries)
        
        # Map exercises to clinical needs
        exercise_clinical_mapping = {
            'mindful-breathing': ['anxiety', 'stress'],
            'box-breathing': ['anxiety', 'focus'],
            '4-7-8-breathing': ['anxiety', 'sleep'],
            'meditation': ['depression', 'stress', 'self_awareness']
        }
        
        # Calculate exercise effectiveness for each clinical need
        exercise_recommendations = {}
        for exercise_type, needs in exercise_clinical_mapping.items():
            exercise_sessions = [s for s in sessions if s.exercise_type == exercise_type]
            
            if exercise_sessions:
                avg_effectiveness = np.mean([s.technique_effectiveness for s in exercise_sessions if s.technique_effectiveness])
                completion_rate = len([s for s in exercise_sessions if s.completion_status == 'completed']) / len(exercise_sessions)
                
                # Calculate clinical relevance score
                clinical_relevance = 0
                for need in needs:
                    if need in clinical_needs:
                        clinical_relevance += clinical_needs[need]
                
                exercise_recommendations[exercise_type] = {
                    'effectiveness': round(avg_effectiveness, 2),
                    'completion_rate': round(completion_rate, 2),
                    'clinical_relevance': round(clinical_relevance, 2),
                    'recommended_for': needs,
                    'priority_score': round((avg_effectiveness + completion_rate + clinical_relevance) / 3, 2)
                }
        
        # Sort by priority score
        sorted_recommendations = sorted(
            exercise_recommendations.items(),
            key=lambda x: x[1]['priority_score'],
            reverse=True
        )
        
        return {
            'clinical_needs': clinical_needs,
            'exercise_recommendations': dict(sorted_recommendations),
            'top_recommendation': sorted_recommendations[0][0] if sorted_recommendations else None
        }
    
    def _analyze_clinical_needs(self, mood_entries):
        """Analyze clinical needs based on mood patterns"""
        if not mood_entries:
            return {'anxiety': 0, 'depression': 0, 'stress': 0, 'sleep': 0}
        
        # Calculate mood statistics
        mood_scores = [entry.intensity_level for entry in mood_entries]
        avg_mood = np.mean(mood_scores)
        mood_variability = np.std(mood_scores)
        
        # Analyze mood patterns for clinical needs
        clinical_needs = {
            'anxiety': 0,
            'depression': 0,
            'stress': 0,
            'sleep': 0
        }
        
        # High mood variability suggests anxiety
        if mood_variability > 2:
            clinical_needs['anxiety'] = min(10, mood_variability * 2)
        
        # Low average mood suggests depression
        if avg_mood < 5:
            clinical_needs['depression'] = min(10, (5 - avg_mood) * 2)
        
        # High variability and low mood suggest stress
        if mood_variability > 1.5 and avg_mood < 6:
            clinical_needs['stress'] = min(10, (mood_variability + (6 - avg_mood)))
        
        # Analyze timing patterns for sleep issues
        night_entries = [entry for entry in mood_entries if entry.timestamp.hour >= 22 or entry.timestamp.hour <= 6]
        if night_entries:
            night_mood_avg = np.mean([entry.intensity_level for entry in night_entries])
            if night_mood_avg < 5:
                clinical_needs['sleep'] = min(10, (5 - night_mood_avg) * 2)
        
        return clinical_needs
    
    def _optimize_intervention_timing(self, start_date, end_date):
        """Intervention timing optimization using pattern recognition"""
        # Get mood entries and sessions
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == self.patient_id,
                MoodEntry.timestamp >= start_date,
                MoodEntry.timestamp <= end_date
            )
        ).order_by(MoodEntry.timestamp).all()
        
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date
            )
        ).all()
        
        if not mood_entries:
            return {
                'optimal_intervention_times': [],
                'risk_periods': [],
                'intervention_effectiveness': {},
                'timing_strategies': []
            }
        
        # Analyze mood patterns to identify optimal intervention times
        mood_by_hour = defaultdict(list)
        for entry in mood_entries:
            hour = entry.timestamp.hour
            mood_by_hour[hour].append(entry.intensity_level)
        
        # Find optimal intervention times (when mood is typically low)
        optimal_intervention_times = []
        risk_periods = []
        
        for hour, scores in mood_by_hour.items():
            avg_mood = np.mean(scores)
            if avg_mood < 4:  # Low mood threshold
                risk_periods.append(hour)
            elif avg_mood < 6:  # Moderate mood threshold
                optimal_intervention_times.append(hour)
        
        # Analyze intervention effectiveness by timing
        intervention_effectiveness = {}
        for session in sessions:
            if session.technique_effectiveness:
                hour = session.start_time.hour
                if hour not in intervention_effectiveness:
                    intervention_effectiveness[hour] = []
                intervention_effectiveness[hour].append(session.technique_effectiveness)
        
        # Calculate average effectiveness by hour
        for hour in intervention_effectiveness:
            intervention_effectiveness[hour] = round(np.mean(intervention_effectiveness[hour]), 2)
        
        # Generate timing strategies
        timing_strategies = []
        if risk_periods:
            timing_strategies.append(f"Schedule proactive sessions during hours: {', '.join(map(str, risk_periods))}")
        
        if optimal_intervention_times:
            timing_strategies.append(f"Optimal intervention windows: {', '.join(map(str, optimal_intervention_times))}")
        
        if not risk_periods and not optimal_intervention_times:
            timing_strategies.append("Mood patterns are stable - maintain regular practice schedule")
        
        return {
            'optimal_intervention_times': sorted(optimal_intervention_times),
            'risk_periods': sorted(risk_periods),
            'intervention_effectiveness': intervention_effectiveness,
            'timing_strategies': timing_strategies
        }

# API Routes for Personalization
@personalization.route('/api/personalization/recommendations/<int:patient_id>')
@login_required
def get_personalized_recommendations(patient_id):
    """Get personalized exercise recommendations"""
    # Verify user has access to this patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    engine = PersonalizationEngine(patient_id)
    return jsonify(engine.get_personalized_recommendations())

if __name__ == '__main__':
    print("Personalization Algorithms System Loaded")
