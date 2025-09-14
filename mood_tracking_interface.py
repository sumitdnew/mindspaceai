#!/usr/bin/env python3
"""
Interactive Mood Tracking System with Gamification
Features: Emoji selection, intensity sliders, weather metaphors, gamification
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import random
from sqlalchemy import func, and_, desc
# Import will be done after models are defined
# from app_ml_complete import db, Patient, MoodEntry, ExerciseStreak, AchievementUnlocked

mood_tracking = Blueprint('mood_tracking', __name__)

# Mood emoji mapping with descriptions
MOOD_EMOJIS = {
    '😊': {'name': 'Happy', 'color': '#4CAF50', 'intensity_range': (7, 10)},
    '😌': {'name': 'Calm', 'color': '#8BC34A', 'intensity_range': (6, 8)},
    '😐': {'name': 'Neutral', 'color': '#FFC107', 'intensity_range': (4, 6)},
    '😔': {'name': 'Sad', 'color': '#FF9800', 'intensity_range': (2, 4)},
    '😢': {'name': 'Very Sad', 'color': '#F44336', 'intensity_range': (1, 3)},
    '😤': {'name': 'Frustrated', 'color': '#E91E63', 'intensity_range': (2, 5)},
    '😴': {'name': 'Tired', 'color': '#9C27B0', 'intensity_range': (3, 6)},
    '😰': {'name': 'Anxious', 'color': '#FF5722', 'intensity_range': (1, 4)},
    '🤗': {'name': 'Grateful', 'color': '#4CAF50', 'intensity_range': (7, 10)},
    '😌': {'name': 'Peaceful', 'color': '#00BCD4', 'intensity_range': (6, 9)}
}

# Weather metaphors for mood
WEATHER_METAPHORS = {
    '☀️': 'Sunny - Bright and positive',
    '⛅': 'Partly Cloudy - Mixed feelings',
    '☁️': 'Cloudy - A bit down',
    '🌧️': 'Rainy - Feeling sad',
    '⛈️': 'Stormy - Very difficult',
    '🌈': 'Rainbow - Hopeful after difficulty',
    '🌅': 'Sunrise - New beginnings',
    '🌙': 'Moonlit - Calm and reflective'
}

# Social contexts
SOCIAL_CONTEXTS = [
    'alone', 'family', 'work', 'with_friends', 'other'
]

# Achievement definitions
ACHIEVEMENTS = {
    'first_entry': {'name': 'First Step', 'description': 'Completed your first mood check-in'},
    'week_streak': {'name': 'Week Warrior', 'description': '7-day mood tracking streak'},
    'month_streak': {'name': 'Mood Master', 'description': '30-day consistency streak'},
    'pattern_detector': {'name': 'Mood Detective', 'description': 'Identified 5 mood patterns'},
    'improvement': {'name': 'Rising Star', 'description': 'Showed consistent mood improvement'},
    'consistency': {'name': 'Steady Soul', 'description': 'Maintained stable mood for 2 weeks'}
}

@mood_tracking.route('/mood_tracker')
@login_required
def mood_tracker():
    """Main mood tracking interface"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Get today's mood entry if exists
    today = datetime.now().date()
    today_entry = MoodEntry.query.filter(
        and_(
            MoodEntry.patient_id == patient.id,
            func.date(MoodEntry.timestamp) == today
        )
    ).first()
    
    # Get streak data
    streak_data = get_streak_data(patient.id)
    
    # Get recent mood trends
    recent_moods = get_recent_mood_trends(patient.id)
    
    return render_template('mood_tracker.html',
                         patient=patient,
                         today_entry=today_entry,
                         streak_data=streak_data,
                         recent_moods=recent_moods,
                         mood_emojis=MOOD_EMOJIS,
                         weather_metaphors=WEATHER_METAPHORS,
                         social_contexts=SOCIAL_CONTEXTS)

@mood_tracking.route('/api/mood-entry', methods=['POST'])
@login_required
def create_mood_entry():
    """Create a new mood entry with gamification"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['mood_emoji', 'intensity_level', 'energy_level', 'sleep_quality']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Convert energy level from 0-100 to 1-10 scale
    energy_level_1_10 = max(1, min(10, round(data['energy_level'] / 10)))
    
    # Map social context to database values
    social_context_mapping = {
        'Alone': 'alone',
        'With Family': 'family', 
        'At Work': 'work',
        'With Friends': 'with_friends',
        'In Therapy': 'other',
        'At School': 'other',
        'In Public': 'other',
        'At Home': 'alone'
    }
    social_context = social_context_mapping.get(data.get('social_context', 'Alone'), 'alone')
    
    # Create mood entry
    mood_entry = MoodEntry(
        mood_id=f"mood_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        patient_id=patient.id,
        timestamp=datetime.now(),
        mood_emoji=data['mood_emoji'],
        intensity_level=data['intensity_level'],
        energy_level=energy_level_1_10,
        sleep_quality=data['sleep_quality'],
        social_context=social_context,
        weather_mood_metaphor=data.get('weather_metaphor', '☀️'),
        color_selection=data.get('color_selection', '#4CAF50'),
        notes_brief=data.get('notes_brief', '')
    )
    
    db.session.add(mood_entry)
    db.session.commit()
    
    # Check for achievements and streaks
    achievements = check_achievements(patient.id)
    streak_update = update_streak(patient.id)
    
    # Generate personalized insights
    insights = generate_mood_insights(patient.id)
    
    return jsonify({
        'success': True,
        'mood_entry_id': mood_entry.mood_id,
        'achievements': achievements,
        'streak_update': streak_update,
        'insights': insights
    })

@mood_tracking.route('/api/mood-insights/<int:patient_id>')
@login_required
def get_mood_insights(patient_id):
    """Get personalized mood insights and patterns"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Verify user has access to this patient
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    insights = generate_mood_insights(patient_id)
    return jsonify(insights)

@mood_tracking.route('/api/mood-trends/<int:patient_id>')
@login_required
def get_mood_trends(patient_id):
    """Get mood trend data for visualization"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Verify user has access to this patient
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get last 30 days of mood data
    thirty_days_ago = datetime.now() - timedelta(days=30)
    mood_entries = MoodEntry.query.filter(
        and_(
            MoodEntry.patient_id == patient_id,
            MoodEntry.timestamp >= thirty_days_ago
        )
    ).order_by(MoodEntry.timestamp).all()
    
    trends = {
        'dates': [],
        'intensity_levels': [],
        'energy_levels': [],
        'sleep_quality': [],
        'mood_emojis': []
    }
    
    for entry in mood_entries:
        trends['dates'].append(entry.timestamp.strftime('%Y-%m-%d'))
        trends['intensity_levels'].append(entry.intensity_level)
        trends['energy_levels'].append(entry.energy_level)
        trends['sleep_quality'].append(entry.sleep_quality)
        trends['mood_emojis'].append(entry.mood_emoji)
    
    return jsonify(trends)

def get_streak_data(patient_id):
    """Calculate current mood tracking streak"""
    # Get all mood entries for this patient, ordered by date
    entries = MoodEntry.query.filter_by(patient_id=patient_id)\
        .order_by(desc(MoodEntry.timestamp)).all()
    
    if not entries:
        return {'current_streak': 0, 'longest_streak': 0, 'last_entry': None}
    
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
        'longest_streak': longest_streak,
        'last_entry': entries[0].timestamp if entries else None
    }

def get_recent_mood_trends(patient_id):
    """Get recent mood patterns for insights"""
    # Get last 7 days of mood entries
    week_ago = datetime.now() - timedelta(days=7)
    recent_entries = MoodEntry.query.filter(
        and_(
            MoodEntry.patient_id == patient_id,
            MoodEntry.timestamp >= week_ago
        )
    ).all()
    
    if not recent_entries:
        return {'avg_intensity': 5, 'avg_energy': 5, 'avg_sleep': 3, 'patterns': []}
    
    # Calculate averages
    avg_intensity = sum(e.intensity_level for e in recent_entries) / len(recent_entries)
    avg_energy = sum(e.energy_level for e in recent_entries) / len(recent_entries)
    avg_sleep = sum(e.sleep_quality for e in recent_entries) / len(recent_entries)
    
    # Identify patterns
    patterns = []
    mood_counts = {}
    for entry in recent_entries:
        mood_counts[entry.mood_emoji] = mood_counts.get(entry.mood_emoji, 0) + 1
    
    most_common_mood = max(mood_counts.items(), key=lambda x: x[1]) if mood_counts else None
    
    if most_common_mood:
        patterns.append(f"Most common mood: {most_common_mood[0]} ({most_common_mood[1]} times)")
    
    # Day of week patterns
    day_patterns = {}
    for entry in recent_entries:
        day = entry.timestamp.strftime('%A')
        if day not in day_patterns:
            day_patterns[day] = []
        day_patterns[day].append(entry.intensity_level)
    
    for day, levels in day_patterns.items():
        avg_level = sum(levels) / len(levels)
        if avg_level > 7:
            patterns.append(f"Your {day}s tend to be better!")
        elif avg_level < 4:
            patterns.append(f"Your {day}s are typically challenging")
    
    return {
        'avg_intensity': round(avg_intensity, 1),
        'avg_energy': round(avg_energy, 1),
        'avg_sleep': round(avg_sleep, 1),
        'patterns': patterns
    }

def check_achievements(patient_id):
    """Check and award new achievements"""
    new_achievements = []
    
    # Get all mood entries for this patient
    entries = MoodEntry.query.filter_by(patient_id=patient_id).all()
    
    if not entries:
        return new_achievements
    
    # Check first entry achievement
    if len(entries) == 1:
        achievement = AchievementUnlocked(
            patient_id=patient_id,
            achievement_type='first_entry',
            achievement_name=ACHIEVEMENTS['first_entry']['name'],
            achievement_description=ACHIEVEMENTS['first_entry']['description'],
            criteria_met='first_mood_entry',
            unlocked_at=datetime.now()
        )
        db.session.add(achievement)
        new_achievements.append(ACHIEVEMENTS['first_entry'])
    
    # Check streak achievements
    streak_data = get_streak_data(patient_id)
    
    if streak_data['current_streak'] >= 7:
        # Check if week streak achievement already exists
        existing = AchievementUnlocked.query.filter_by(
            patient_id=patient_id,
            achievement_type='week_streak'
        ).first()
        
        if not existing:
            achievement = AchievementUnlocked(
                patient_id=patient_id,
                achievement_type='week_streak',
                achievement_name=ACHIEVEMENTS['week_streak']['name'],
                achievement_description=ACHIEVEMENTS['week_streak']['description'],
                criteria_met='7_day_streak',
                unlocked_at=datetime.now()
            )
            db.session.add(achievement)
            new_achievements.append(ACHIEVEMENTS['week_streak'])
    
    if streak_data['current_streak'] >= 30:
        # Check if month streak achievement already exists
        existing = AchievementUnlocked.query.filter_by(
            patient_id=patient_id,
            achievement_type='month_streak'
        ).first()
        
        if not existing:
            achievement = AchievementUnlocked(
                patient_id=patient_id,
                achievement_type='month_streak',
                achievement_name=ACHIEVEMENTS['month_streak']['name'],
                achievement_description=ACHIEVEMENTS['month_streak']['description'],
                criteria_met='30_day_streak',
                unlocked_at=datetime.now()
            )
            db.session.add(achievement)
            new_achievements.append(ACHIEVEMENTS['month_streak'])
    
    # Check pattern detection achievement
    if len(entries) >= 20:
        # Check if pattern detector achievement already exists
        existing = AchievementUnlocked.query.filter_by(
            patient_id=patient_id,
            achievement_type='pattern_detector'
        ).first()
        
        if not existing:
            achievement = AchievementUnlocked(
                patient_id=patient_id,
                achievement_type='pattern_detector',
                achievement_name=ACHIEVEMENTS['pattern_detector']['name'],
                achievement_description=ACHIEVEMENTS['pattern_detector']['description'],
                criteria_met=f'{len(entries)}_entries_analyzed',
                unlocked_at=datetime.now()
            )
            db.session.add(achievement)
            new_achievements.append(ACHIEVEMENTS['pattern_detector'])
    
    if new_achievements:
        db.session.commit()
    
    return new_achievements

def update_streak(patient_id):
    """Update exercise streak for mood tracking"""
    # Get or create streak record
    streak = ExerciseStreak.query.filter_by(
        patient_id=patient_id,
        exercise_type='mood_tracking'
    ).first()
    
    if not streak:
        streak = ExerciseStreak(
            patient_id=patient_id,
            exercise_type='mood_tracking',
            current_streak=1,
            longest_streak=1,
            last_completion_date=datetime.now().date()
        )
        db.session.add(streak)
    else:
        # Check if today's entry is already counted
        if streak.last_completion_date != datetime.now().date():
            streak.current_streak += 1
            streak.longest_streak = max(streak.longest_streak, streak.current_streak)
            streak.last_completion_date = datetime.now().date()
    
    db.session.commit()
    
    return {
        'current_streak': streak.current_streak,
        'longest_streak': streak.longest_streak
    }

def generate_mood_insights(patient_id):
    """Generate personalized mood insights"""
    # Get recent mood data
    week_ago = datetime.now() - timedelta(days=7)
    recent_entries = MoodEntry.query.filter(
        and_(
            MoodEntry.patient_id == patient_id,
            MoodEntry.timestamp >= week_ago
        )
    ).all()
    
    if not recent_entries:
        return {
            'message': 'Keep up the great work with your mood tracking!',
            'suggestions': ['Try to check in at the same time each day', 'Notice any patterns in your mood']
        }
    
    insights = []
    suggestions = []
    
    # Analyze sleep-mood correlation
    sleep_mood_corr = []
    for entry in recent_entries:
        if entry.sleep_quality and entry.intensity_level:
            sleep_mood_corr.append((entry.sleep_quality, entry.intensity_level))
    
    if len(sleep_mood_corr) >= 3:
        avg_sleep = sum(s[0] for s in sleep_mood_corr) / len(sleep_mood_corr)
        avg_mood = sum(s[1] for s in sleep_mood_corr) / len(sleep_mood_corr)
        
        if avg_sleep < 3 and avg_mood < 5:
            insights.append("Better sleep might help improve your mood")
            suggestions.append("Try establishing a consistent bedtime routine")
        elif avg_sleep >= 4 and avg_mood >= 7:
            insights.append("Great job maintaining good sleep and mood!")
    
    # Analyze energy-mood correlation
    energy_mood_corr = []
    for entry in recent_entries:
        if entry.energy_level and entry.intensity_level:
            energy_mood_corr.append((entry.energy_level, entry.intensity_level))
    
    if len(energy_mood_corr) >= 3:
        avg_energy = sum(e[0] for e in energy_mood_corr) / len(energy_mood_corr)
        if avg_energy < 4:
            insights.append("Your energy levels have been low recently")
            suggestions.append("Consider light physical activity to boost energy")
        elif avg_energy >= 7:
            insights.append("You've been maintaining good energy levels!")
    
    # Pattern recognition
    mood_counts = {}
    for entry in recent_entries:
        mood_counts[entry.mood_emoji] = mood_counts.get(entry.mood_emoji, 0) + 1
    
    if mood_counts:
        most_common = max(mood_counts.items(), key=lambda x: x[1])
        if most_common[1] >= 3:
            insights.append(f"You've been feeling {most_common[0]} frequently")
    
    # Streak motivation
    streak_data = get_streak_data(patient_id)
    if streak_data['current_streak'] >= 3:
        insights.append(f"Amazing! You're on a {streak_data['current_streak']}-day streak!")
    
    if not insights:
        insights.append("Keep tracking to discover your mood patterns!")
    
    if not suggestions:
        suggestions.append("Try to check in at least once per day")
        suggestions.append("Notice what activities improve your mood")
    
    return {
        'insights': insights,
        'suggestions': suggestions
    }
