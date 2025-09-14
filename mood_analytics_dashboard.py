#!/usr/bin/env python3
"""
Mood Analytics Dashboard
Real-time mood trend visualization, pattern recognition, and engagement metrics
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import numpy as np
from sqlalchemy import func, and_, desc, extract
# Import will be done after models are defined
# from app_ml_complete import db, Patient, MoodEntry, ExerciseStreak, AchievementUnlocked

mood_analytics = Blueprint('mood_analytics', __name__)

@mood_analytics.route('/mood-analytics')
@login_required
def mood_analytics_dashboard():
    """Main mood analytics dashboard"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Get analytics data
    analytics_data = generate_analytics_data(patient.id)
    
    return render_template('mood_analytics.html',
                         patient=patient,
                         analytics_data=analytics_data)

@mood_analytics.route('/api/mood-analytics/<int:patient_id>')
@login_required
def get_mood_analytics(patient_id):
    """Get comprehensive mood analytics data"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Verify user has access to this patient
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    analytics_data = generate_analytics_data(patient_id)
    return jsonify(analytics_data)

@mood_analytics.route('/api/mood-patterns/<int:patient_id>')
@login_required
def get_mood_patterns(patient_id):
    """Get mood pattern analysis"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Verify user has access to this patient
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    patterns = analyze_mood_patterns(patient_id)
    return jsonify(patterns)

@mood_analytics.route('/api/engagement-metrics/<int:patient_id>')
@login_required
def get_engagement_metrics(patient_id):
    """Get engagement metrics"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Verify user has access to this patient
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    metrics = calculate_engagement_metrics(patient_id)
    return jsonify(metrics)

def generate_analytics_data(patient_id):
    """Generate comprehensive analytics data"""
    # Get date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Get mood entries
    mood_entries = MoodEntry.query.filter(
        and_(
            MoodEntry.patient_id == patient_id,
            MoodEntry.timestamp >= start_date
        )
    ).order_by(MoodEntry.timestamp).all()
    
    if not mood_entries:
        return {
            'trends': {'dates': [], 'intensity': [], 'energy': [], 'sleep': []},
            'patterns': {},
            'engagement': {},
            'insights': [],
            'alerts': []
        }
    
    # Time series data
    trends = {
        'dates': [],
        'intensity': [],
        'energy': [],
        'sleep': [],
        'mood_emojis': []
    }
    
    for entry in mood_entries:
        trends['dates'].append(entry.timestamp.strftime('%Y-%m-%d'))
        trends['intensity'].append(entry.intensity_level)
        trends['energy'].append(entry.energy_level)
        trends['sleep'].append(entry.sleep_quality)
        trends['mood_emojis'].append(entry.mood_emoji)
    
    # Pattern analysis
    patterns = analyze_mood_patterns(patient_id)
    
    # Engagement metrics
    engagement = calculate_engagement_metrics(patient_id)
    
    # Generate insights
    insights = generate_analytics_insights(mood_entries, patterns, engagement)
    
    # Generate alerts
    alerts = generate_analytics_alerts(mood_entries, patterns)
    
    return {
        'trends': trends,
        'patterns': patterns,
        'engagement': engagement,
        'insights': insights,
        'alerts': alerts
    }

def analyze_mood_patterns(patient_id):
    """Analyze mood patterns and correlations"""
    # Get last 30 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    mood_entries = MoodEntry.query.filter(
        and_(
            MoodEntry.patient_id == patient_id,
            MoodEntry.timestamp >= start_date
        )
    ).all()
    
    if not mood_entries:
        return {}
    
    patterns = {
        'day_of_week': {},
        'time_of_day': {},
        'sleep_correlation': {},
        'energy_correlation': {},
        'social_context': {},
        'weather_patterns': {},
        'mood_stability': {}
    }
    
    # Day of week patterns
    day_patterns = {}
    for entry in mood_entries:
        day = entry.timestamp.strftime('%A')
        if day not in day_patterns:
            day_patterns[day] = []
        day_patterns[day].append(entry.intensity_level)
    
    for day, levels in day_patterns.items():
        patterns['day_of_week'][day] = {
            'avg_intensity': round(sum(levels) / len(levels), 2),
            'count': len(levels),
            'trend': 'improving' if sum(levels) / len(levels) > 6 else 'challenging' if sum(levels) / len(levels) < 4 else 'stable'
        }
    
    # Time of day patterns
    time_patterns = {}
    for entry in mood_entries:
        hour = entry.timestamp.hour
        time_slot = 'morning' if 6 <= hour < 12 else 'afternoon' if 12 <= hour < 18 else 'evening' if 18 <= hour < 22 else 'night'
        
        if time_slot not in time_patterns:
            time_patterns[time_slot] = []
        time_patterns[time_slot].append(entry.intensity_level)
    
    for time_slot, levels in time_patterns.items():
        patterns['time_of_day'][time_slot] = {
            'avg_intensity': round(sum(levels) / len(levels), 2),
            'count': len(levels)
        }
    
    # Sleep correlation
    sleep_mood_pairs = [(entry.sleep_quality, entry.intensity_level) for entry in mood_entries 
                       if entry.sleep_quality and entry.intensity_level]
    
    if len(sleep_mood_pairs) >= 5:
        sleep_values = [pair[0] for pair in sleep_mood_pairs]
        mood_values = [pair[1] for pair in sleep_mood_pairs]
        
        # Calculate correlation coefficient
        correlation = np.corrcoef(sleep_values, mood_values)[0, 1] if len(sleep_values) > 1 else 0
        
        patterns['sleep_correlation'] = {
            'correlation': round(correlation, 3),
            'strength': 'strong' if abs(correlation) > 0.7 else 'moderate' if abs(correlation) > 0.4 else 'weak',
            'direction': 'positive' if correlation > 0 else 'negative',
            'sample_size': len(sleep_mood_pairs)
        }
    
    # Energy correlation
    energy_mood_pairs = [(entry.energy_level, entry.intensity_level) for entry in mood_entries 
                        if entry.energy_level and entry.intensity_level]
    
    if len(energy_mood_pairs) >= 5:
        energy_values = [pair[0] for pair in energy_mood_pairs]
        mood_values = [pair[1] for pair in energy_mood_pairs]
        
        correlation = np.corrcoef(energy_values, mood_values)[0, 1] if len(energy_values) > 1 else 0
        
        patterns['energy_correlation'] = {
            'correlation': round(correlation, 3),
            'strength': 'strong' if abs(correlation) > 0.7 else 'moderate' if abs(correlation) > 0.4 else 'weak',
            'direction': 'positive' if correlation > 0 else 'negative',
            'sample_size': len(energy_mood_pairs)
        }
    
    # Social context patterns
    context_patterns = {}
    for entry in mood_entries:
        context = entry.social_context
        if context not in context_patterns:
            context_patterns[context] = []
        context_patterns[context].append(entry.intensity_level)
    
    for context, levels in context_patterns.items():
        patterns['social_context'][context] = {
            'avg_intensity': round(sum(levels) / len(levels), 2),
            'count': len(levels)
        }
    
    # Weather patterns
    weather_patterns = {}
    for entry in mood_entries:
        weather = entry.weather_mood_metaphor
        if weather not in weather_patterns:
            weather_patterns[weather] = []
        weather_patterns[weather].append(entry.intensity_level)
    
    for weather, levels in weather_patterns.items():
        patterns['weather_patterns'][weather] = {
            'avg_intensity': round(sum(levels) / len(levels), 2),
            'count': len(levels)
        }
    
    # Mood stability analysis
    if len(mood_entries) >= 7:
        intensities = [entry.intensity_level for entry in mood_entries]
        std_dev = np.std(intensities)
        mean_intensity = np.mean(intensities)
        
        patterns['mood_stability'] = {
            'std_deviation': round(std_dev, 2),
            'mean_intensity': round(mean_intensity, 2),
            'stability_score': round(max(0, 10 - std_dev), 2),  # Higher score = more stable
            'stability_level': 'very_stable' if std_dev < 1.5 else 'stable' if std_dev < 2.5 else 'variable' if std_dev < 3.5 else 'unstable'
        }
    
    return patterns

def calculate_engagement_metrics(patient_id):
    """Calculate engagement metrics"""
    # Get date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Total entries in last 30 days
    total_entries = MoodEntry.query.filter(
        and_(
            MoodEntry.patient_id == patient_id,
            MoodEntry.timestamp >= start_date
        )
    ).count()
    
    # Completion rate (entries vs days)
    days_in_period = 30
    completion_rate = round((total_entries / days_in_period) * 100, 1)
    
    # Current streak
    streak_data = get_current_streak(patient_id)
    
    # Achievement count
    achievements = AchievementUnlocked.query.filter_by(patient_id=patient_id).count()
    
    # Average time spent (estimated)
    avg_time_spent = 2.5  # minutes per entry
    
    # Engagement score (0-100)
    engagement_score = min(100, (
        completion_rate * 0.4 +  # 40% weight for completion rate
        min(streak_data['current_streak'] * 5, 30) +  # 30% weight for streak (max 6 days)
        min(achievements * 10, 30)  # 30% weight for achievements (max 3 achievements)
    ))
    
    # Engagement level
    if engagement_score >= 80:
        engagement_level = 'excellent'
    elif engagement_score >= 60:
        engagement_level = 'good'
    elif engagement_score >= 40:
        engagement_level = 'moderate'
    else:
        engagement_level = 'needs_improvement'
    
    return {
        'total_entries': total_entries,
        'completion_rate': completion_rate,
        'current_streak': streak_data['current_streak'],
        'longest_streak': streak_data['longest_streak'],
        'achievements': achievements,
        'avg_time_spent': avg_time_spent,
        'engagement_score': round(engagement_score, 1),
        'engagement_level': engagement_level
    }

def get_current_streak(patient_id):
    """Get current mood tracking streak"""
    entries = MoodEntry.query.filter_by(patient_id=patient_id)\
        .order_by(desc(MoodEntry.timestamp)).all()
    
    if not entries:
        return {'current_streak': 0, 'longest_streak': 0}
    
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    current_date = datetime.now().date()
    
    # Check if there's an entry today
    if entries[0].timestamp.date() == current_date:
        current_streak = 1
        temp_streak = 1
        current_date -= timedelta(days=1)
    
    # Count consecutive days
    for entry in entries:
        entry_date = entry.timestamp.date()
        
        if entry_date == current_date:
            temp_streak += 1
            current_streak = temp_streak
            current_date -= timedelta(days=1)
        elif entry_date < current_date:
            # Gap in streak
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 0
            current_date = entry_date - timedelta(days=1)
    
    longest_streak = max(longest_streak, temp_streak)
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak
    }

def generate_analytics_insights(mood_entries, patterns, engagement):
    """Generate actionable insights from analytics data"""
    insights = []
    
    if not mood_entries:
        insights.append("Start tracking your mood to discover patterns and insights!")
        return insights
    
    # Mood stability insights
    if 'mood_stability' in patterns:
        stability = patterns['mood_stability']
        if 'stability_level' in stability:
            if stability['stability_level'] == 'very_stable':
                insights.append("Your mood has been very stable recently - great emotional regulation!")
            elif stability['stability_level'] == 'stable':
                insights.append("Your mood has been relatively stable - good emotional balance!")
            elif stability['stability_level'] == 'variable':
                insights.append("Your mood has been somewhat variable. Consider stress management techniques.")
            elif stability['stability_level'] == 'unstable':
                insights.append("Your mood has been quite variable. Consider discussing this with your provider.")
    
    # Day of week insights
    if 'day_of_week' in patterns and patterns['day_of_week']:
        try:
            best_day = max(patterns['day_of_week'].items(), key=lambda x: x[1].get('avg_intensity', 0))
            worst_day = min(patterns['day_of_week'].items(), key=lambda x: x[1].get('avg_intensity', 0))
            
            if best_day[1].get('avg_intensity', 0) > 7:
                insights.append(f"Your {best_day[0]}s tend to be your best days!")
            
            if worst_day[1].get('avg_intensity', 0) < 4:
                insights.append(f"Your {worst_day[0]}s are typically challenging. Plan self-care activities.")
        except (ValueError, KeyError):
            pass  # Skip if there's an issue with the data
    
    # Sleep correlation insights
    if 'sleep_correlation' in patterns and 'strength' in patterns['sleep_correlation'] and patterns['sleep_correlation']['strength'] in ['strong', 'moderate']:
        sleep_corr = patterns['sleep_correlation']
        if 'direction' in sleep_corr and sleep_corr['direction'] == 'positive':
            insights.append("Better sleep quality correlates with improved mood. Focus on sleep hygiene!")
        elif 'direction' in sleep_corr and sleep_corr['direction'] == 'negative':
            insights.append("Poor sleep quality may be affecting your mood. Consider sleep strategies.")
    
    # Energy correlation insights
    if 'energy_correlation' in patterns and 'strength' in patterns['energy_correlation'] and patterns['energy_correlation']['strength'] in ['strong', 'moderate']:
        energy_corr = patterns['energy_correlation']
        if 'direction' in energy_corr and energy_corr['direction'] == 'positive':
            insights.append("Higher energy levels correlate with better mood. Try light physical activity!")
    
    # Engagement insights
    if engagement.get('engagement_level') == 'excellent':
        insights.append("Excellent engagement! You're making great progress with mood tracking.")
    elif engagement.get('engagement_level') == 'needs_improvement':
        insights.append("Consider setting daily reminders to improve your mood tracking consistency.")
    
    # Streak motivation
    current_streak = engagement.get('current_streak', 0)
    if current_streak >= 7:
        insights.append(f"Amazing! You're on a {current_streak}-day streak!")
    elif current_streak >= 3:
        insights.append(f"Great job! You're on a {current_streak}-day streak. Keep it up!")
    
    # Social context insights
    if 'social_context' in patterns and patterns['social_context']:
        try:
            best_context = max(patterns['social_context'].items(), key=lambda x: x[1].get('avg_intensity', 0))
            if best_context[1].get('avg_intensity', 0) > 7:
                insights.append(f"You tend to feel better when {best_context[0].lower()}. Plan more of these activities!")
        except (ValueError, KeyError):
            pass  # Skip if there's an issue with the data
    
    if not insights:
        insights.append("Keep tracking to discover more patterns in your mood!")
    
    return insights

def generate_analytics_alerts(mood_entries, patterns):
    """Generate alerts for providers based on patterns"""
    alerts = []
    
    if not mood_entries:
        return alerts
    
    # Recent entries (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_entries = [entry for entry in mood_entries if entry.timestamp >= week_ago]
    
    if recent_entries:
        recent_intensities = [entry.intensity_level for entry in recent_entries]
        avg_recent_intensity = sum(recent_intensities) / len(recent_intensities)
        
        # Low mood alert
        if avg_recent_intensity < 3:
            alerts.append({
                'type': 'low_mood',
                'severity': 'moderate',
                'message': f'Average mood intensity is {round(avg_recent_intensity, 1)}/10 over the last 7 days',
                'recommendation': 'Consider checking in with the patient about recent challenges'
            })
        
        # Declining trend alert
        if len(recent_entries) >= 3:
            first_half = recent_entries[:len(recent_entries)//2]
            second_half = recent_entries[len(recent_entries)//2:]
            
            first_avg = sum(entry.intensity_level for entry in first_half) / len(first_half)
            second_avg = sum(entry.intensity_level for entry in second_half) / len(second_half)
            
            if second_avg < first_avg - 2:  # Significant decline
                alerts.append({
                    'type': 'declining_trend',
                    'severity': 'moderate',
                    'message': 'Mood appears to be declining over the last week',
                    'recommendation': 'Monitor closely and consider intervention if trend continues'
                })
    
    # Mood stability alert
    if 'mood_stability' in patterns:
        stability = patterns['mood_stability']
        if 'stability_level' in stability and stability['stability_level'] in ['unstable', 'variable']:
            stability_score = stability.get('stability_score', 'N/A')
            alerts.append({
                'type': 'mood_instability',
                'severity': 'moderate',
                'message': f'Mood stability score is {stability_score}/10',
                'recommendation': 'Consider mood stabilization strategies or medication review'
            })
    
    # Engagement alert
    if len(mood_entries) < 10:  # Less than 10 entries in 30 days
        alerts.append({
            'type': 'low_engagement',
            'severity': 'low',
            'message': 'Patient has low engagement with mood tracking',
            'recommendation': 'Encourage daily mood check-ins and explain benefits'
        })
    
    return alerts
