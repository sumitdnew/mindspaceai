#!/usr/bin/env python3
"""
Risk Detection System for Exercise Analytics
Identifies warning indicators and behavioral patterns
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

risk_detection = Blueprint('risk_detection', __name__)

class RiskDetectionSystem:
    """Risk detection and warning system for exercise analytics"""
    
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.analysis_period = 30  # days
        self.risk_thresholds = {
            'engagement_drop': 0.5,  # 50% drop in engagement
            'negative_rating_threshold': 3,  # Average rating below 3/10
            'crisis_usage_spike': 2,  # 2x increase in crisis exercises
            'avoidance_pattern': 0.8,  # 80% of sessions abandoned
            'isolation_indicator': 0.3  # 30% reduction in social activities
        }
    
    def get_risk_analysis(self):
        """4. RISK DETECTION SYSTEM"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.analysis_period)
        
        risk_analysis = {
            'engagement_drops': self._detect_engagement_drops(start_date, end_date),
            'negative_ratings': self._detect_negative_ratings(start_date, end_date),
            'crisis_usage_spikes': self._detect_crisis_usage_spikes(start_date, end_date),
            'avoidance_patterns': self._detect_avoidance_patterns(start_date, end_date),
            'isolation_indicators': self._detect_isolation_indicators(start_date, end_date),
            'overall_risk_level': 'low',
            'risk_alerts': []
        }
        
        # Calculate overall risk level
        risk_analysis['overall_risk_level'] = self._calculate_overall_risk_level(risk_analysis)
        risk_analysis['risk_alerts'] = self._generate_risk_alerts(risk_analysis)
        
        return risk_analysis
    
    def _detect_engagement_drops(self, start_date, end_date):
        """Sudden engagement drops as warning indicators"""
        # Get mindfulness sessions over time
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date
            )
        ).order_by(MindfulnessSession.start_time).all()
        
        if len(sessions) < 5:
            return {
                'detected': False,
                'drop_percentage': 0,
                'drop_duration': 0,
                'severity': 'none',
                'intervention_needed': False
            }
        
        # Group sessions by week
        sessions_by_week = defaultdict(int)
        for session in sessions:
            week_start = session.start_time - timedelta(days=session.start_time.weekday())
            week_key = week_start.strftime('%Y-%W')
            sessions_by_week[week_key] += 1
        
        # Calculate engagement trend
        weekly_counts = list(sessions_by_week.values())
        if len(weekly_counts) < 2:
            return {
                'detected': False,
                'drop_percentage': 0,
                'drop_duration': 0,
                'severity': 'none',
                'intervention_needed': False
            }
        
        # Detect significant drops
        recent_avg = np.mean(weekly_counts[-2:])  # Last 2 weeks
        earlier_avg = np.mean(weekly_counts[:-2]) if len(weekly_counts) > 2 else weekly_counts[0]
        
        if earlier_avg > 0:
            drop_percentage = (earlier_avg - recent_avg) / earlier_avg
        else:
            drop_percentage = 0
        
        # Determine severity and intervention need
        detected = drop_percentage > self.risk_thresholds['engagement_drop']
        severity = 'none'
        intervention_needed = False
        
        if detected:
            if drop_percentage > 0.8:
                severity = 'critical'
                intervention_needed = True
            elif drop_percentage > 0.6:
                severity = 'high'
                intervention_needed = True
            elif drop_percentage > 0.4:
                severity = 'moderate'
                intervention_needed = True
            else:
                severity = 'low'
        
        return {
            'detected': detected,
            'drop_percentage': round(drop_percentage, 3),
            'drop_duration': len(weekly_counts),
            'severity': severity,
            'intervention_needed': intervention_needed,
            'weekly_engagement': weekly_counts
        }
    
    def _detect_negative_ratings(self, start_date, end_date):
        """Consistent negative ratings across exercises"""
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
                'detected': False,
                'avg_rating': 0,
                'negative_sessions_count': 0,
                'severity': 'none',
                'intervention_needed': False
            }
        
        # Calculate average rating
        effectiveness_scores = [s.technique_effectiveness for s in sessions]
        avg_rating = np.mean(effectiveness_scores)
        
        # Count negative sessions (rating below threshold)
        negative_sessions = [s for s in sessions if s.technique_effectiveness < self.risk_thresholds['negative_rating_threshold']]
        negative_count = len(negative_sessions)
        negative_percentage = negative_count / len(sessions)
        
        # Determine severity
        detected = avg_rating < self.risk_thresholds['negative_rating_threshold'] or negative_percentage > 0.7
        severity = 'none'
        intervention_needed = False
        
        if detected:
            if avg_rating < 2 or negative_percentage > 0.9:
                severity = 'critical'
                intervention_needed = True
            elif avg_rating < 3 or negative_percentage > 0.8:
                severity = 'high'
                intervention_needed = True
            else:
                severity = 'moderate'
                intervention_needed = True
        
        return {
            'detected': detected,
            'avg_rating': round(avg_rating, 2),
            'negative_sessions_count': negative_count,
            'negative_percentage': round(negative_percentage, 3),
            'severity': severity,
            'intervention_needed': intervention_needed,
            'total_sessions_rated': len(sessions)
        }
    
    def _detect_crisis_usage_spikes(self, start_date, end_date):
        """Crisis exercise usage spike detection"""
        # Get sessions and identify crisis-related exercises
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date
            )
        ).all()
        
        if len(sessions) < 5:
            return {
                'detected': False,
                'spike_percentage': 0,
                'crisis_sessions_count': 0,
                'severity': 'none',
                'intervention_needed': False
            }
        
        # Define crisis-related exercises (exercises typically used during distress)
        crisis_exercises = ['4-7-8-breathing', 'box-breathing']  # Quick relief exercises
        
        # Group sessions by week
        sessions_by_week = defaultdict(lambda: {'total': 0, 'crisis': 0})
        for session in sessions:
            week_start = session.start_time - timedelta(days=session.start_time.weekday())
            week_key = week_start.strftime('%Y-%W')
            sessions_by_week[week_key]['total'] += 1
            if session.exercise_type in crisis_exercises:
                sessions_by_week[week_key]['crisis'] += 1
        
        # Calculate crisis usage trend
        weekly_data = list(sessions_by_week.values())
        if len(weekly_data) < 2:
            return {
                'detected': False,
                'spike_percentage': 0,
                'crisis_sessions_count': 0,
                'severity': 'none',
                'intervention_needed': False
            }
        
        # Calculate crisis usage percentage
        recent_crisis_usage = np.mean([w['crisis'] / max(w['total'], 1) for w in weekly_data[-2:]])
        earlier_crisis_usage = np.mean([w['crisis'] / max(w['total'], 1) for w in weekly_data[:-2]]) if len(weekly_data) > 2 else 0
        
        if earlier_crisis_usage > 0:
            spike_percentage = (recent_crisis_usage - earlier_crisis_usage) / earlier_crisis_usage
        else:
            spike_percentage = 0
        
        # Count total crisis sessions
        crisis_sessions_count = sum(w['crisis'] for w in weekly_data)
        
        # Determine severity
        detected = spike_percentage > self.risk_thresholds['crisis_usage_spike']
        severity = 'none'
        intervention_needed = False
        
        if detected:
            if spike_percentage > 5 or crisis_sessions_count > 10:
                severity = 'critical'
                intervention_needed = True
            elif spike_percentage > 3 or crisis_sessions_count > 7:
                severity = 'high'
                intervention_needed = True
            else:
                severity = 'moderate'
                intervention_needed = True
        
        return {
            'detected': detected,
            'spike_percentage': round(spike_percentage, 3),
            'crisis_sessions_count': crisis_sessions_count,
            'severity': severity,
            'intervention_needed': intervention_needed,
            'recent_crisis_usage': round(recent_crisis_usage, 3),
            'earlier_crisis_usage': round(earlier_crisis_usage, 3)
        }
    
    def _detect_avoidance_patterns(self, start_date, end_date):
        """Avoidance behavior pattern identification"""
        # Get sessions with completion status
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date
            )
        ).all()
        
        if not sessions:
            return {
                'detected': False,
                'avoidance_rate': 0,
                'abandoned_sessions_count': 0,
                'severity': 'none',
                'intervention_needed': False
            }
        
        # Calculate avoidance patterns
        abandoned_sessions = [s for s in sessions if s.completion_status == 'abandoned']
        avoidance_rate = len(abandoned_sessions) / len(sessions)
        
        # Analyze avoidance by exercise type
        avoidance_by_type = defaultdict(lambda: {'total': 0, 'abandoned': 0})
        for session in sessions:
            avoidance_by_type[session.exercise_type]['total'] += 1
            if session.completion_status == 'abandoned':
                avoidance_by_type[session.exercise_type]['abandoned'] += 1
        
        # Find most avoided exercise type
        most_avoided = None
        highest_avoidance = 0
        for exercise_type, data in avoidance_by_type.items():
            if data['total'] > 0:
                rate = data['abandoned'] / data['total']
                if rate > highest_avoidance:
                    highest_avoidance = rate
                    most_avoided = exercise_type
        
        # Determine severity
        detected = avoidance_rate > self.risk_thresholds['avoidance_pattern']
        severity = 'none'
        intervention_needed = False
        
        if detected:
            if avoidance_rate > 0.9:
                severity = 'critical'
                intervention_needed = True
            elif avoidance_rate > 0.8:
                severity = 'high'
                intervention_needed = True
            else:
                severity = 'moderate'
                intervention_needed = True
        
        return {
            'detected': detected,
            'avoidance_rate': round(avoidance_rate, 3),
            'abandoned_sessions_count': len(abandoned_sessions),
            'severity': severity,
            'intervention_needed': intervention_needed,
            'most_avoided_exercise': most_avoided,
            'avoidance_by_type': {k: {'rate': round(v['abandoned'] / v['total'], 3), 'count': v['abandoned']} 
                                 for k, v in avoidance_by_type.items() if v['total'] > 0}
        }
    
    def _detect_isolation_indicators(self, start_date, end_date):
        """Social isolation indicator tracking"""
        # This would typically integrate with social activity tracking
        # For now, we'll analyze session timing patterns as isolation indicators
        
        sessions = MindfulnessSession.query.filter(
            and_(
                MindfulnessSession.patient_id == self.patient_id,
                MindfulnessSession.start_time >= start_date,
                MindfulnessSession.start_time <= end_date
            )
        ).all()
        
        if not sessions:
            return {
                'detected': False,
                'isolation_score': 0,
                'night_sessions_percentage': 0,
                'severity': 'none',
                'intervention_needed': False
            }
        
        # Analyze session timing patterns
        night_sessions = [s for s in sessions if s.start_time.hour >= 22 or s.start_time.hour <= 6]
        night_sessions_percentage = len(night_sessions) / len(sessions)
        
        # Analyze session frequency patterns
        sessions_by_date = defaultdict(int)
        for session in sessions:
            date = session.start_time.date()
            sessions_by_date[date] += 1
        
        # Calculate isolation indicators
        isolation_indicators = []
        isolation_score = 0
        
        # High percentage of night sessions (potential isolation)
        if night_sessions_percentage > 0.5:
            isolation_indicators.append("High percentage of late-night sessions")
            isolation_score += night_sessions_percentage * 0.4
        
        # Irregular session patterns (potential social withdrawal)
        if len(sessions_by_date) > 0:
            avg_sessions_per_day = len(sessions) / len(sessions_by_date)
            if avg_sessions_per_day > 3:  # Multiple sessions per day might indicate isolation
                isolation_indicators.append("Multiple sessions per day pattern")
                isolation_score += min(avg_sessions_per_day / 5, 0.3)
        
        # Determine severity
        detected = isolation_score > self.risk_thresholds['isolation_indicator']
        severity = 'none'
        intervention_needed = False
        
        if detected:
            if isolation_score > 0.7:
                severity = 'critical'
                intervention_needed = True
            elif isolation_score > 0.5:
                severity = 'high'
                intervention_needed = True
            else:
                severity = 'moderate'
                intervention_needed = True
        
        return {
            'detected': detected,
            'isolation_score': round(isolation_score, 3),
            'night_sessions_percentage': round(night_sessions_percentage, 3),
            'severity': severity,
            'intervention_needed': intervention_needed,
            'isolation_indicators': isolation_indicators,
            'total_sessions_analyzed': len(sessions)
        }
    
    def _calculate_overall_risk_level(self, risk_analysis):
        """Calculate overall risk level based on all indicators"""
        risk_scores = {
            'engagement_drops': 0,
            'negative_ratings': 0,
            'crisis_usage_spikes': 0,
            'avoidance_patterns': 0,
            'isolation_indicators': 0
        }
        
        # Score each risk factor
        severity_scores = {'none': 0, 'low': 1, 'moderate': 2, 'high': 3, 'critical': 4}
        
        for risk_type, data in risk_analysis.items():
            if risk_type in risk_scores and isinstance(data, dict) and 'severity' in data:
                risk_scores[risk_type] = severity_scores.get(data['severity'], 0)
        
        # Calculate overall risk score
        total_risk_score = sum(risk_scores.values())
        max_possible_score = len(risk_scores) * 4  # 4 is max severity
        
        risk_percentage = total_risk_score / max_possible_score
        
        # Determine overall risk level
        if risk_percentage >= 0.6:
            return 'critical'
        elif risk_percentage >= 0.4:
            return 'high'
        elif risk_percentage >= 0.2:
            return 'moderate'
        else:
            return 'low'
    
    def _generate_risk_alerts(self, risk_analysis):
        """Generate actionable risk alerts"""
        alerts = []
        
        for risk_type, data in risk_analysis.items():
            if isinstance(data, dict) and data.get('intervention_needed', False):
                severity = data.get('severity', 'unknown')
                
                if risk_type == 'engagement_drops':
                    alerts.append({
                        'type': 'engagement_drop',
                        'severity': severity,
                        'message': f"Significant drop in exercise engagement detected ({data.get('drop_percentage', 0):.1%})",
                        'action': "Consider reaching out to understand barriers and provide support"
                    })
                
                elif risk_type == 'negative_ratings':
                    alerts.append({
                        'type': 'negative_ratings',
                        'severity': severity,
                        'message': f"Consistently low exercise effectiveness ratings (avg: {data.get('avg_rating', 0):.1f}/10)",
                        'action': "Review exercise difficulty and provide additional guidance"
                    })
                
                elif risk_type == 'crisis_usage_spikes':
                    alerts.append({
                        'type': 'crisis_usage_spike',
                        'severity': severity,
                        'message': f"Spike in crisis exercise usage detected ({data.get('spike_percentage', 0):.1%} increase)",
                        'action': "Assess current mental health status and crisis risk"
                    })
                
                elif risk_type == 'avoidance_patterns':
                    alerts.append({
                        'type': 'avoidance_pattern',
                        'severity': severity,
                        'message': f"High exercise avoidance rate ({data.get('avoidance_rate', 0):.1%})",
                        'action': "Address barriers and consider alternative approaches"
                    })
                
                elif risk_type == 'isolation_indicators':
                    alerts.append({
                        'type': 'isolation_indicator',
                        'severity': severity,
                        'message': f"Potential social isolation indicators detected (score: {data.get('isolation_score', 0):.1f})",
                        'action': "Assess social support and encourage social engagement"
                    })
        
        return alerts

# API Routes for Risk Detection
@risk_detection.route('/api/risk-detection/analysis/<int:patient_id>')
@login_required
def get_risk_analysis(patient_id):
    """Get comprehensive risk analysis"""
    # Verify user has access to this patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    risk_system = RiskDetectionSystem(patient_id)
    return jsonify(risk_system.get_risk_analysis())

if __name__ == '__main__':
    print("Risk Detection System Loaded")
