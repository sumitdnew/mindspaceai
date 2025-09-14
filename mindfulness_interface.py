#!/usr/bin/env python3
"""
Mindfulness and Breathing Exercises Interface
Features: Guided breathing, meditation, biofeedback, session tracking
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import random
from sqlalchemy import func, and_, desc
# Import will be done after models are defined
# from app_ml_complete import db, Patient, MindfulnessSession, ExerciseStreak, AchievementUnlocked

mindfulness_exercises = Blueprint('mindfulness_exercises', __name__)

# Breathing exercise patterns
BREATHING_PATTERNS = {
    'box-breathing': {
        'name': 'Box Breathing',
        'description': 'Inhale for 4, hold for 4, exhale for 4, hold for 4',
        'pattern': {'inhale': 4, 'hold1': 4, 'exhale': 4, 'hold2': 4},
        'benefits': ['Stress relief', 'Improved focus', 'Better sleep'],
        'difficulty': 'Beginner'
    },
    '4-7-8-breathing': {
        'name': '4-7-8 Breathing',
        'description': 'Inhale for 4, hold for 7, exhale for 8',
        'pattern': {'inhale': 4, 'hold1': 7, 'exhale': 8, 'hold2': 0},
        'benefits': ['Anxiety reduction', 'Sleep preparation', 'Emotional regulation'],
        'difficulty': 'Intermediate'
    },
    'mindful-breathing': {
        'name': 'Mindful Breathing',
        'description': 'Natural breathing with awareness',
        'pattern': {'inhale': 4, 'hold1': 0, 'exhale': 4, 'hold2': 0},
        'benefits': ['Present moment awareness', 'Stress reduction', 'Mental clarity'],
        'difficulty': 'Beginner'
    },
    'coherent-breathing': {
        'name': 'Coherent Breathing',
        'description': '5-5 breathing pattern for nervous system balance',
        'pattern': {'inhale': 5, 'hold1': 0, 'exhale': 5, 'hold2': 0},
        'benefits': ['Nervous system balance', 'Heart rate variability', 'Stress reduction'],
        'difficulty': 'Intermediate'
    }
}

# Meditation sessions
MEDITATION_SESSIONS = {
    'beginner': {
        'name': 'Beginner Meditation',
        'duration': 300,  # 5 minutes
        'steps': [
            'Find a comfortable position and close your eyes',
            'Take three deep breaths to settle in',
            'Focus on your natural breath',
            'Notice thoughts without judgment',
            'Gently return to your breath'
        ]
    },
    'intermediate': {
        'name': 'Mindfulness Meditation',
        'duration': 600,  # 10 minutes
        'steps': [
            'Find a comfortable seated position',
            'Take several deep breaths to center yourself',
            'Focus on the sensation of breathing',
            'When your mind wanders, gently return to the breath',
            'Practice non-judgmental awareness',
            'Expand awareness to body sensations',
            'Notice thoughts and emotions with curiosity',
            'Return to the present moment'
        ]
    },
    'advanced': {
        'name': 'Deep Meditation',
        'duration': 900,  # 15 minutes
        'steps': [
            'Settle into a comfortable meditation posture',
            'Take time to arrive in the present moment',
            'Establish a steady, natural breathing rhythm',
            'Focus attention on the breath with gentle precision',
            'When distracted, acknowledge and return to breath',
            'Expand awareness to include body sensations',
            'Observe thoughts and emotions with equanimity',
            'Cultivate a sense of spacious awareness',
            'Rest in natural awareness',
            'Gently conclude the session'
        ]
    }
}

# Achievement definitions
MINDFULNESS_ACHIEVEMENTS = {
    'first_session': {
        'name': 'First Steps',
        'description': 'Completed your first mindfulness session',
        'icon': '🧘',
        'criteria': 'first_mindfulness_session'
    },
    'breathing_master': {
        'name': 'Breathing Master',
        'description': 'Completed 10 breathing exercises',
        'icon': '🫁',
        'criteria': '10_breathing_sessions'
    },
    'meditation_streak': {
        'name': 'Meditation Warrior',
        'description': '7-day meditation streak',
        'icon': '🔥',
        'criteria': '7_day_meditation_streak'
    },
    'stress_reduction': {
        'name': 'Stress Buster',
        'description': 'Reduced stress levels by 50%',
        'icon': '😌',
        'criteria': 'stress_reduction_50_percent'
    },
    'mindfulness_expert': {
        'name': 'Mindfulness Expert',
        'description': 'Completed 50 total sessions',
        'icon': '🌟',
        'criteria': '50_total_sessions'
    }
}

@mindfulness_exercises.route('/mindfulness')
@login_required
def mindfulness_dashboard():
    """Main mindfulness exercises dashboard"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Get recent sessions
    recent_sessions = get_recent_sessions(patient.id)
    
    # Get session statistics
    session_stats = get_session_statistics(patient.id)
    
    # Get current streak
    streak_data = get_mindfulness_streak(patient.id)
    
    return render_template('mindfulness_exercises.html',
                         patient=patient,
                         recent_sessions=recent_sessions,
                         session_stats=session_stats,
                         streak_data=streak_data,
                         breathing_patterns=BREATHING_PATTERNS,
                         meditation_sessions=MEDITATION_SESSIONS)

@mindfulness_exercises.route('/api/mindfulness-session', methods=['POST'])
@login_required
def create_mindfulness_session():
    """Create a new mindfulness session"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['duration', 'exercise_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create mindfulness session
    session_entry = MindfulnessSession(
        session_id=f"mindfulness_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        patient_id=patient.id,
        start_time=datetime.now(),
        exercise_type=data['exercise_type'],  # specific exercise name
        duration_planned=data['duration'] // 60,  # convert seconds to minutes
        completion_status='completed'
    )
    
    db.session.add(session_entry)
    db.session.commit()
    
    # Check for achievements
    achievements = check_mindfulness_achievements(patient.id)
    
    # Update streak
    streak_update = update_mindfulness_streak(patient.id)
    
    # Generate insights
    insights = generate_mindfulness_insights(patient.id)
    
    return jsonify({
        'success': True,
        'session_id': session_entry.session_id,
        'achievements': achievements,
        'streak_update': streak_update,
        'insights': insights
    })

@mindfulness_exercises.route('/api/mindfulness-stats/<int:patient_id>')
@login_required
def get_mindfulness_statistics(patient_id):
    """Get mindfulness practice statistics"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Verify user has access to this patient
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    stats = get_session_statistics(patient_id)
    return jsonify(stats)

@mindfulness_exercises.route('/api/mindfulness-trends/<int:patient_id>')
@login_required
def get_mindfulness_trends(patient_id):
    """Get mindfulness practice trends"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Verify user has access to this patient
    if patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get last 30 days of sessions
    thirty_days_ago = datetime.now() - timedelta(days=30)
    sessions = MindfulnessSession.query.filter(
        and_(
            MindfulnessSession.patient_id == patient_id,
            MindfulnessSession.start_time >= thirty_days_ago
        )
    ).order_by(MindfulnessSession.start_time).all()
    
    trends = {
        'dates': [],
        'session_durations': [],
        'exercise_types': []
    }
    
    for session in sessions:
        trends['dates'].append(session.start_time.strftime('%Y-%m-%d'))
        trends['session_durations'].append(session.duration_planned)  # Already in minutes
        trends['exercise_types'].append(session.exercise_type)
    
    return jsonify(trends)

def get_recent_sessions(patient_id):
    """Get recent mindfulness sessions"""
    # Get last 7 sessions
    recent_sessions = MindfulnessSession.query.filter_by(patient_id=patient_id)\
        .order_by(desc(MindfulnessSession.start_time))\
        .limit(7).all()
    
    sessions_data = []
    for session in recent_sessions:
        sessions_data.append({
            'session_id': session.session_id,
            'timestamp': session.start_time.strftime('%Y-%m-%d %H:%M'),
            'exercise_type': session.exercise_type,
            'duration_minutes': session.duration_planned,
            'completion_status': session.completion_status
        })
    
    return sessions_data

def get_session_statistics(patient_id):
    """Calculate mindfulness session statistics"""
    # Get all sessions for this patient
    all_sessions = MindfulnessSession.query.filter_by(patient_id=patient_id).all()
    
    if not all_sessions:
        return {
            'total_sessions': 0,
            'total_minutes': 0,
            'avg_session_length': 0,
            'favorite_exercise': None,
            'current_streak': 0
        }
    
    # Calculate basic stats
    total_sessions = len(all_sessions)
    total_minutes = sum(s.duration_planned for s in all_sessions)
    avg_session_length = total_minutes / total_sessions if total_sessions > 0 else 0
    
    # Find favorite exercise
    exercise_counts = {}
    for session in all_sessions:
        exercise_counts[session.exercise_type] = exercise_counts.get(session.exercise_type, 0) + 1
    
    favorite_exercise = max(exercise_counts.items(), key=lambda x: x[1])[0] if exercise_counts else None
    
    # Get current streak
    streak_data = get_mindfulness_streak(patient_id)
    
    return {
        'total_sessions': total_sessions,
        'total_minutes': round(total_minutes, 1),
        'avg_session_length': round(avg_session_length, 1),
        'favorite_exercise': favorite_exercise,
        'current_streak': streak_data['current_streak']
    }

def get_mindfulness_streak(patient_id):
    """Calculate current mindfulness practice streak"""
    # Get all sessions for this patient, ordered by date
    sessions = MindfulnessSession.query.filter_by(patient_id=patient_id)\
        .order_by(desc(MindfulnessSession.start_time)).all()
    
    if not sessions:
        return {'current_streak': 0, 'longest_streak': 0, 'last_session': None}
    
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    current_date = datetime.now().date()
    
    # Check if there's a session today
    if sessions[0].start_time.date() == current_date:
        current_streak = 1
        temp_streak = 1
        current_date -= timedelta(days=1)
    
    # Count consecutive days
    for session in sessions:
        session_date = session.start_time.date()
        
        if session_date == current_date:
            temp_streak += 1
            current_streak = temp_streak
            current_date -= timedelta(days=1)
        elif session_date < current_date:
            # Gap in streak
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 0
            current_date = session_date - timedelta(days=1)
    
    longest_streak = max(longest_streak, temp_streak)
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'last_session': sessions[0].start_time if sessions else None
    }

def check_mindfulness_achievements(patient_id):
    """Check and award new mindfulness achievements"""
    new_achievements = []
    
    # Get all mindfulness sessions for this patient
    sessions = MindfulnessSession.query.filter_by(patient_id=patient_id).all()
    
    if not sessions:
        return new_achievements
    
    # Check first session achievement
    if len(sessions) == 1:
        achievement = AchievementUnlocked(
            patient_id=patient_id,
            achievement_type='first_session',
            achievement_name=MINDFULNESS_ACHIEVEMENTS['first_session']['name'],
            achievement_description=MINDFULNESS_ACHIEVEMENTS['first_session']['description'],
            criteria_met='first_mindfulness_session',
            unlocked_at=datetime.now()
        )
        db.session.add(achievement)
        new_achievements.append(MINDFULNESS_ACHIEVEMENTS['first_session'])
    
    # Check breathing master achievement
    breathing_sessions = [s for s in sessions if s.exercise_type == 'breathing']
    if len(breathing_sessions) >= 10:
        # Check if achievement already exists
        existing = AchievementUnlocked.query.filter_by(
            patient_id=patient_id,
            achievement_type='breathing_master'
        ).first()
        
        if not existing:
            achievement = AchievementUnlocked(
                patient_id=patient_id,
                achievement_type='breathing_master',
                achievement_name=MINDFULNESS_ACHIEVEMENTS['breathing_master']['name'],
                achievement_description=MINDFULNESS_ACHIEVEMENTS['breathing_master']['description'],
                criteria_met=f'{len(breathing_sessions)}_breathing_sessions',
                unlocked_at=datetime.now()
            )
            db.session.add(achievement)
            new_achievements.append(MINDFULNESS_ACHIEVEMENTS['breathing_master'])
    
    # Check meditation streak achievement
    streak_data = get_mindfulness_streak(patient_id)
    if streak_data['current_streak'] >= 7:
        # Check if achievement already exists
        existing = AchievementUnlocked.query.filter_by(
            patient_id=patient_id,
            achievement_type='meditation_streak'
        ).first()
        
        if not existing:
            achievement = AchievementUnlocked(
                patient_id=patient_id,
                achievement_type='meditation_streak',
                achievement_name=MINDFULNESS_ACHIEVEMENTS['meditation_streak']['name'],
                achievement_description=MINDFULNESS_ACHIEVEMENTS['meditation_streak']['description'],
                criteria_met='7_day_meditation_streak',
                unlocked_at=datetime.now()
            )
            db.session.add(achievement)
            new_achievements.append(MINDFULNESS_ACHIEVEMENTS['meditation_streak'])
    
    # Check mindfulness expert achievement
    if len(sessions) >= 50:
        # Check if achievement already exists
        existing = AchievementUnlocked.query.filter_by(
            patient_id=patient_id,
            achievement_type='mindfulness_expert'
        ).first()
        
        if not existing:
            achievement = AchievementUnlocked(
                patient_id=patient_id,
                achievement_type='mindfulness_expert',
                achievement_name=MINDFULNESS_ACHIEVEMENTS['mindfulness_expert']['name'],
                achievement_description=MINDFULNESS_ACHIEVEMENTS['mindfulness_expert']['description'],
                criteria_met=f'{len(sessions)}_total_sessions',
                unlocked_at=datetime.now()
            )
            db.session.add(achievement)
            new_achievements.append(MINDFULNESS_ACHIEVEMENTS['mindfulness_expert'])
    
    if new_achievements:
        db.session.commit()
    
    return new_achievements

def update_mindfulness_streak(patient_id):
    """Update mindfulness practice streak"""
    # Get or create streak record
    streak = ExerciseStreak.query.filter_by(
        patient_id=patient_id,
        exercise_type='mindfulness'
    ).first()
    
    if not streak:
        streak = ExerciseStreak(
            patient_id=patient_id,
            exercise_type='mindfulness',
            current_streak=1,
            longest_streak=1,
            last_completion_date=datetime.now().date()
        )
        db.session.add(streak)
    else:
        # Check if today's session is already counted
        if streak.last_completion_date != datetime.now().date():
            streak.current_streak += 1
            streak.longest_streak = max(streak.longest_streak, streak.current_streak)
            streak.last_completion_date = datetime.now().date()
    
    db.session.commit()
    
    return {
        'current_streak': streak.current_streak,
        'longest_streak': streak.longest_streak
    }

def generate_mindfulness_insights(patient_id):
    """Generate personalized mindfulness insights"""
    # Get recent sessions
    week_ago = datetime.now() - timedelta(days=7)
    recent_sessions = MindfulnessSession.query.filter(
        and_(
            MindfulnessSession.patient_id == patient_id,
            MindfulnessSession.start_time >= week_ago
        )
    ).all()
    
    if not recent_sessions:
        return {
            'message': 'Welcome to your mindfulness journey!',
            'suggestions': ['Start with 5-minute sessions', 'Try different breathing techniques', 'Practice regularly for best results']
        }
    
    insights = []
    suggestions = []
    
    # Analyze session patterns
    total_sessions = len(recent_sessions)
    total_minutes = sum(s.duration_planned for s in recent_sessions)
    avg_session_length = total_minutes / total_sessions if total_sessions > 0 else 0
    
    if total_sessions >= 5:
        insights.append(f"Great consistency! You've practiced {total_sessions} times this week.")
    elif total_sessions >= 3:
        insights.append(f"Good progress! You've practiced {total_sessions} times this week.")
    else:
        insights.append(f"You've practiced {total_sessions} times this week. Keep it up!")
    
    # Analyze session length
    if avg_session_length >= 10:
        insights.append("You're engaging in longer sessions - excellent for deep practice!")
    elif avg_session_length >= 5:
        insights.append("Good session length! Consider trying longer sessions for deeper benefits.")
    else:
        suggestions.append("Try extending your sessions to 5-10 minutes for better results.")
    
    # Analyze session completion
    completed_sessions = [s for s in recent_sessions if s.completion_status == 'completed']
    completion_rate = len(completed_sessions) / len(recent_sessions) if recent_sessions else 0
    
    if completion_rate >= 0.8:
        insights.append("Excellent completion rate! You're very consistent with your practice.")
    elif completion_rate >= 0.6:
        insights.append("Good completion rate! Try to finish more sessions for better results.")
    else:
        suggestions.append("Try to complete more sessions to build a consistent practice.")
    
    # Session type analysis
    breathing_sessions = [s for s in recent_sessions if s.exercise_type == 'breathing']
    meditation_sessions = [s for s in recent_sessions if s.exercise_type == 'meditation']
    
    if breathing_sessions and meditation_sessions:
        insights.append("Great balance! You're practicing both breathing and meditation.")
    elif breathing_sessions:
        suggestions.append("Consider trying guided meditation for variety.")
    elif meditation_sessions:
        suggestions.append("Try breathing exercises for quick stress relief.")
    
    # Streak motivation
    streak_data = get_mindfulness_streak(patient_id)
    if streak_data['current_streak'] >= 3:
        insights.append(f"Amazing! You're on a {streak_data['current_streak']}-day streak!")
    
    if not insights:
        insights.append("Keep practicing to discover your mindfulness patterns!")
    
    if not suggestions:
        suggestions.append("Try to practice at least once per day")
        suggestions.append("Experiment with different techniques")
    
    return {
        'insights': insights,
        'suggestions': suggestions
    }
