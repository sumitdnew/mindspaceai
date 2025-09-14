#!/usr/bin/env python3
"""
Comprehensive Exercise Analytics System
Tracks exercise effectiveness and provides personalized recommendations
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
# from app_ml_complete import db, Patient, MindfulnessSession, ExerciseStreak, AchievementUnlocked, MoodEntry

exercise_analytics = Blueprint('exercise_analytics', __name__)

class ExerciseAnalytics:
    """Comprehensive analytics for exercise effectiveness tracking"""
    
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.analysis_period = 30  # days
    
    def get_engagement_analytics(self):
        """1. ENGAGEMENT ANALYTICS SYSTEM"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.analysis_period)
        
        # Get all sessions in analysis period
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date
            )
        ).all()
        
        analytics = {
            'completion_rates': self._analyze_completion_rates(sessions),
            'time_spent_analysis': self._analyze_time_spent(sessions),
            'drop_off_analysis': self._analyze_drop_off_points(sessions),
            'timing_patterns': self._analyze_timing_patterns(sessions),
            'interface_interactions': self._analyze_interface_interactions(sessions)
        }
        
        return analytics
    
    def _analyze_completion_rates(self, sessions):
        """Exercise completion rates by type and difficulty"""
        if not sessions:
            return {'overall_rate': 0, 'by_type': {}, 'by_difficulty': {}}
        
        total_sessions = len(sessions)
        completed_sessions = [s for s in sessions if s.completion_status == 'completed']
        overall_rate = len(completed_sessions) / total_sessions
        
        # By exercise type
        by_type = defaultdict(lambda: {'total': 0, 'completed': 0, 'rate': 0})
        for session in sessions:
            by_type[session.exercise_type]['total'] += 1
            if session.completion_status == 'completed':
                by_type[session.exercise_type]['completed'] += 1
        
        # Calculate rates
        for exercise_type, data in by_type.items():
            data['rate'] = data['completed'] / data['total'] if data['total'] > 0 else 0
        
        # By difficulty (estimated based on exercise type)
        difficulty_mapping = {
            'mindful-breathing': 1,
            'box-breathing': 2,
            '4-7-8-breathing': 3,
            'meditation': 4
        }
        
        by_difficulty = defaultdict(lambda: {'total': 0, 'completed': 0, 'rate': 0})
        for session in sessions:
            difficulty = difficulty_mapping.get(session.exercise_type, 2)
            by_difficulty[difficulty]['total'] += 1
            if session.completion_status == 'completed':
                by_difficulty[difficulty]['completed'] += 1
        
        # Calculate rates
        for difficulty, data in by_difficulty.items():
            data['rate'] = data['completed'] / data['total'] if data['total'] > 0 else 0
        
        return {
            'overall_rate': overall_rate,
            'by_type': dict(by_type),
            'by_difficulty': dict(by_difficulty)
        }
    
    def _analyze_time_spent(self, sessions):
        """Time spent per exercise and optimal session lengths"""
        if not sessions:
            return {'avg_duration': 0, 'optimal_length': 0, 'duration_distribution': {}}
        
        completed_sessions = [s for s in sessions if s.completion_status == 'completed']
        if not completed_sessions:
            return {'avg_duration': 0, 'optimal_length': 0, 'duration_distribution': {}}
        
        durations = [s.duration_actual or s.duration_planned for s in completed_sessions]
        avg_duration = np.mean(durations)
        
        # Find optimal length (duration with highest effectiveness)
        effectiveness_by_duration = defaultdict(list)
        for session in completed_sessions:
            if session.technique_effectiveness:
                duration = session.duration_actual or session.duration_planned
                effectiveness_by_duration[duration].append(session.technique_effectiveness)
        
        optimal_length = 0
        max_avg_effectiveness = 0
        for duration, effectiveness_scores in effectiveness_by_duration.items():
            avg_effectiveness = np.mean(effectiveness_scores)
            if avg_effectiveness > max_avg_effectiveness:
                max_avg_effectiveness = avg_effectiveness
                optimal_length = duration
        
        # Duration distribution
        duration_distribution = defaultdict(int)
        for duration in durations:
            if duration <= 5:
                duration_distribution['0-5min'] += 1
            elif duration <= 10:
                duration_distribution['5-10min'] += 1
            elif duration <= 15:
                duration_distribution['10-15min'] += 1
            else:
                duration_distribution['15+min'] += 1
        
        return {
            'avg_duration': round(avg_duration, 1),
            'optimal_length': optimal_length,
            'duration_distribution': dict(duration_distribution)
        }
    
    def _analyze_drop_off_points(self, sessions):
        """Drop-off point identification and intervention strategies"""
        if not sessions:
            return {'drop_off_rate': 0, 'common_points': [], 'interventions': []}
        
        abandoned_sessions = [s for s in sessions if s.completion_status == 'abandoned']
        drop_off_rate = len(abandoned_sessions) / len(sessions)
        
        # Analyze drop-off points by duration
        drop_off_by_duration = defaultdict(int)
        for session in abandoned_sessions:
            duration = session.duration_actual or 0
            if duration <= 2:
                drop_off_by_duration['0-2min'] += 1
            elif duration <= 5:
                drop_off_by_duration['2-5min'] += 1
            elif duration <= 10:
                drop_off_by_duration['5-10min'] += 1
            else:
                drop_off_by_duration['10+min'] += 1
        
        # Generate intervention strategies
        interventions = []
        if drop_off_rate > 0.3:
            interventions.append("High drop-off rate detected - consider shorter sessions")
        if drop_off_by_duration.get('0-2min', 0) > len(abandoned_sessions) * 0.5:
            interventions.append("Many early drop-offs - improve onboarding experience")
        if drop_off_by_duration.get('5-10min', 0) > len(abandoned_sessions) * 0.3:
            interventions.append("Mid-session drop-offs - add engagement checkpoints")
        
        return {
            'drop_off_rate': drop_off_rate,
            'common_points': dict(drop_off_by_duration),
            'interventions': interventions
        }
    
    def _analyze_timing_patterns(self, sessions):
        """Preferred exercise timing and frequency patterns"""
        if not sessions:
            return {'time_of_day': {}, 'frequency': {}, 'optimal_times': []}
        
        # Time of day analysis
        time_of_day = defaultdict(int)
        for session in sessions:
            hour = session.start_time.hour
            if 6 <= hour < 12:
                time_of_day['morning'] += 1
            elif 12 <= hour < 17:
                time_of_day['afternoon'] += 1
            elif 17 <= hour < 21:
                time_of_day['evening'] += 1
            else:
                time_of_day['night'] += 1
        
        # Frequency analysis
        sessions_by_date = defaultdict(int)
        for session in sessions:
            date = session.start_time.date()
            sessions_by_date[date] += 1
        
        daily_frequency = list(sessions_by_date.values())
        avg_daily_sessions = np.mean(daily_frequency) if daily_frequency else 0
        
        # Find optimal times (times with highest effectiveness)
        effectiveness_by_time = defaultdict(list)
        for session in sessions:
            if session.technique_effectiveness:
                hour = session.start_time.hour
                effectiveness_by_time[hour].append(session.technique_effectiveness)
        
        optimal_times = []
        for hour, effectiveness_scores in effectiveness_by_time.items():
            avg_effectiveness = np.mean(effectiveness_scores)
            if avg_effectiveness >= 7:  # High effectiveness threshold
                optimal_times.append(hour)
        
        return {
            'time_of_day': dict(time_of_day),
            'frequency': {
                'avg_daily_sessions': round(avg_daily_sessions, 1),
                'total_days_active': len(sessions_by_date)
            },
            'optimal_times': sorted(optimal_times)
        }
    
    def _analyze_interface_interactions(self, sessions):
        """User interface interaction heatmaps (simulated)"""
        # This would typically come from frontend tracking
        # For now, we'll simulate based on session data
        interaction_patterns = {
            'start_button_clicks': len(sessions),
            'pause_button_usage': len([s for s in sessions if s.interruption_count and s.interruption_count > 0]),
            'exercise_selection_patterns': self._get_exercise_selection_patterns(sessions),
            'session_completion_flow': self._analyze_completion_flow(sessions)
        }
        
        return interaction_patterns
    
    def _get_exercise_selection_patterns(self, sessions):
        """Analyze exercise selection patterns"""
        exercise_counts = defaultdict(int)
        for session in sessions:
            exercise_counts[session.exercise_type] += 1
        
        total = len(sessions)
        patterns = {}
        for exercise, count in exercise_counts.items():
            patterns[exercise] = {
                'count': count,
                'percentage': round((count / total) * 100, 1) if total > 0 else 0
            }
        
        return patterns
    
    def _analyze_completion_flow(self, sessions):
        """Analyze how users flow through sessions"""
        flow_data = {
            'started': len(sessions),
            'completed': len([s for s in sessions if s.completion_status == 'completed']),
            'abandoned': len([s for s in sessions if s.completion_status == 'abandoned']),
            'interrupted': len([s for s in sessions if s.interruption_count and s.interruption_count > 0])
        }
        
        return flow_data

# API Routes for Analytics
@exercise_analytics.route('/api/analytics/engagement/<int:patient_id>')
@login_required
def get_engagement_analytics(patient_id):
    """Get comprehensive engagement analytics"""
    # Verify user has access to this patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    analytics = ExerciseAnalytics(patient_id)
    return jsonify(analytics.get_engagement_analytics())

if __name__ == '__main__':
    print("Exercise Analytics System Loaded")
