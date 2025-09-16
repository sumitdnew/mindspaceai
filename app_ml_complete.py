#!/usr/bin/env python3
"""
MindSpace ML App - PHQ-9 Focused Mental Health Assessment System
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import numpy as np
import logging
import os
import json
import anthropic
from dotenv import load_dotenv
from sqlalchemy import desc

# Import dashboard systems
from comprehensive_provider_dashboard import provider_dashboard as comprehensive_dashboard_blueprint
print(f"DEBUG: comprehensive_dashboard_blueprint type: {type(comprehensive_dashboard_blueprint)}")
print(f"DEBUG: comprehensive_dashboard_blueprint value: {comprehensive_dashboard_blueprint}")

# Import crisis detection system
from crisis_detector_xgboost import XGBoostCrisisDetector

# Provider feedback system will be imported after models are defined

# Import mood tracking blueprints (will be imported after models are defined)
# from mood_tracking_interface import mood_tracking
# from mood_analytics_dashboard import mood_analytics

# Load environment variables (optional)
try:
    load_dotenv()
    print("✅ Environment variables loaded successfully")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")
    print("📝 Continuing without environment variables...")

# Initialize Claude client
try:
    claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    print("✅ Claude API client initialized successfully")
except Exception as e:
    print(f"⚠️ Could not initialize Claude API client: {e}")
    print("📝 Claude features will be disabled...")
    claude_client = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mindspace_ml_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Crisis Detection System
crisis_detector = XGBoostCrisisDetector()
print("🔍 Initializing Crisis Detection System...")
if crisis_detector.load_model():
    print("✅ Crisis Detection Model loaded successfully")
else:
    print("⚠️ No trained crisis detection model found - will need training")

# Database Models - PHQ-9 Focused Only
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='patient')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Patient(db.Model):
    """Patient model for PHQ-9 assessments"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    current_phq9_severity = db.Column(db.String(30), default='minimal')
    last_assessment_date = db.Column(db.DateTime)
    total_assessments = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PHQ9Assessment(db.Model):
    """PHQ-9 assessment with all 9 questions and scoring"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # Individual question scores (0-3 scale)
    q1_score = db.Column(db.Integer, nullable=False)  # Little interest or pleasure
    q2_score = db.Column(db.Integer, nullable=False)  # Feeling down, depressed, or hopeless
    q3_score = db.Column(db.Integer, nullable=False)  # Trouble falling/staying asleep, sleeping too much
    q4_score = db.Column(db.Integer, nullable=False)  # Feeling tired or having little energy
    q5_score = db.Column(db.Integer, nullable=False)  # Poor appetite or overeating
    q6_score = db.Column(db.Integer, nullable=False)  # Feeling bad about yourself
    q7_score = db.Column(db.Integer, nullable=False)  # Trouble concentrating
    q8_score = db.Column(db.Integer, nullable=False)  # Moving or speaking slowly/being fidgety
    q9_score = db.Column(db.Integer, nullable=False)  # Thoughts of self-harm or being better off dead
    
    # Calculated scores
    total_score = db.Column(db.Integer, nullable=False)  # 0-27 range
    severity_level = db.Column(db.String(30), nullable=False)  # minimal, mild, moderate, moderately_severe, severe
    
    # Risk flags
    q9_risk_flag = db.Column(db.Boolean, default=False)  # Special flag for suicidal ideation
    crisis_alert_triggered = db.Column(db.Boolean, default=False)
    
    # Metadata
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def calculate_severity(self):
        """Calculate severity level based on total score"""
        if self.total_score <= 4:
            return 'minimal'
        elif self.total_score <= 9:
            return 'mild'
        elif self.total_score <= 14:
            return 'moderate'
        elif self.total_score <= 19:
            return 'moderately_severe'
        else:
            return 'severe'
    
    # Relationships
    patient = db.relationship('Patient', backref='phq9_assessments')

class RecommendationResult(db.Model):
    """AI-generated recommendations based on PHQ-9 scores"""
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('phq9_assessment.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    recommendation_type = db.Column(db.String(50), nullable=False)  # immediate, short_term, long_term
    recommendation_text = db.Column(db.Text, nullable=False)
    priority_level = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    ai_generated = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CrisisAlert(db.Model):
    """Automated alerts for high-risk PHQ-9 scores"""
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('phq9_assessment.id'), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    alert_type = db.Column(db.String(50), nullable=False)  # q9_risk, high_score, rapid_decline
    alert_message = db.Column(db.Text, nullable=False)
    severity_level = db.Column(db.String(20), nullable=False)  # warning, urgent, critical
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by = db.Column(db.String(50))
    acknowledged_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='crisis_alerts')
    assessment = db.relationship('PHQ9Assessment', backref='crisis_alerts')

# Interactive Mental Health Exercise Models
class Exercise(db.Model):
    """Master list of available mental health exercises"""
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False, index=True)  # cbt, mindfulness, breathing, journaling, mood_tracking
    difficulty_level = db.Column(db.Integer, nullable=False)  # 1-5 scale
    estimated_duration = db.Column(db.Integer, nullable=False)  # minutes
    clinical_focus_areas = db.Column(db.String(200), nullable=False)  # comma-separated: depression, anxiety, stress
    engagement_mechanics = db.Column(db.String(100), nullable=False)  # interactive, guided, self-paced
    data_points_collected = db.Column(db.String(200), nullable=False)  # comma-separated: mood, thoughts, engagement
    description = db.Column(db.String(500), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('difficulty_level >= 1 AND difficulty_level <= 5', name='check_difficulty_level'),
        db.CheckConstraint('estimated_duration > 0', name='check_duration_positive'),
    )

class ExerciseSession(db.Model):
    """Individual exercise completion sessions"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False, index=True)
    
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    completion_time = db.Column(db.DateTime, nullable=True)
    completion_status = db.Column(db.String(20), nullable=False, default='started')  # started, completed, abandoned
    engagement_score = db.Column(db.Integer, nullable=True)  # 1-10 scale
    effectiveness_rating = db.Column(db.Integer, nullable=True)  # 1-10 scale
    collected_data = db.Column(db.JSON, nullable=True)  # Exercise-specific metrics
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='exercise_sessions')
    exercise = db.relationship('Exercise', backref='sessions')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('engagement_score >= 1 AND engagement_score <= 10', name='check_engagement_score'),
        db.CheckConstraint('effectiveness_rating >= 1 AND effectiveness_rating <= 10', name='check_effectiveness_rating'),
        db.CheckConstraint("completion_status IN ('started', 'completed', 'abandoned')", name='check_completion_status'),
    )

class MoodEntry(db.Model):
    """Enhanced mood tracking with structured data collection"""
    id = db.Column(db.Integer, primary_key=True)
    mood_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    mood_emoji = db.Column(db.String(10), nullable=False)  # 😊, 😢, 😡, etc.
    intensity_level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    energy_level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    sleep_quality = db.Column(db.Integer, nullable=True)  # 1-10 scale
    social_context = db.Column(db.String(50), nullable=True)  # alone, with_friends, family, work
    weather_mood_metaphor = db.Column(db.String(50), nullable=True)  # sunny, cloudy, stormy, calm
    color_selection = db.Column(db.String(20), nullable=True)  # red, blue, green, yellow, etc.
    notes_brief = db.Column(db.String(200), nullable=True)  # Structured brief notes only
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='mood_entries')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('intensity_level >= 1 AND intensity_level <= 10', name='check_intensity_level'),
        db.CheckConstraint('energy_level >= 1 AND energy_level <= 10', name='check_energy_level'),
        db.CheckConstraint('sleep_quality >= 1 AND sleep_quality <= 10', name='check_sleep_quality'),
        db.CheckConstraint("social_context IN ('alone', 'with_friends', 'family', 'work', 'other')", name='check_social_context'),
    )

class ThoughtRecord(db.Model):
    """Enhanced CBT thought challenging and cognitive restructuring"""
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    
    # Situation
    situation_category = db.Column(db.String(50), nullable=False)  # work, social, health, family, relationships, academic, financial, other
    situation_description = db.Column(db.Text, nullable=False)
    
    # Emotions
    primary_emotion = db.Column(db.String(50), nullable=False)
    emotion_intensity = db.Column(db.Integer, nullable=False)  # 1-10 scale
    secondary_emotions = db.Column(db.String(200), nullable=True)  # JSON array of additional emotions
    
    # Initial Thought
    initial_thought = db.Column(db.Text, nullable=False)
    thought_confidence = db.Column(db.Integer, nullable=False)  # 1-10 scale
    
    # Cognitive Distortions
    distortions_identified = db.Column(db.Text)  # JSON array of distortion types
    
    # Evidence Analysis
    supporting_evidence = db.Column(db.Text)  # JSON array of evidence items
    contradicting_evidence = db.Column(db.Text)  # JSON array of evidence items
    
    # Balanced Thought
    balanced_thought = db.Column(db.Text, nullable=True)
    balanced_confidence = db.Column(db.Integer, nullable=True)  # 1-10 scale
    
    # Outcome
    outcome_rating = db.Column(db.Integer)  # 1-10 scale for effectiveness
    mood_improvement = db.Column(db.Integer)  # 1-10 scale
    
    # Metadata
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    completion_time = db.Column(db.Integer)  # seconds to complete
    ai_assisted = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='thought_records')
    evidence_items = db.relationship(lambda: EvidenceItem, backref='thought_record', lazy=True, cascade='all, delete-orphan')
    distortion_analysis = db.relationship(lambda: DistortionAnalysis, backref='thought_record', lazy=True, cascade='all, delete-orphan')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('emotion_intensity >= 1 AND emotion_intensity <= 10', name='check_emotion_intensity'),
        db.CheckConstraint('thought_confidence >= 1 AND thought_confidence <= 10', name='check_thought_confidence'),
        db.CheckConstraint('balanced_confidence >= 1 AND balanced_confidence <= 10', name='check_balanced_confidence'),
        db.CheckConstraint('outcome_rating >= 1 AND outcome_rating <= 10', name='check_outcome_rating'),
        db.CheckConstraint('mood_improvement >= 1 AND mood_improvement <= 10', name='check_mood_improvement'),
        db.CheckConstraint("situation_category IN ('work', 'social', 'health', 'family', 'relationships', 'academic', 'financial', 'other')", name='check_situation_category'),
        db.CheckConstraint("difficulty_level IN ('beginner', 'intermediate', 'advanced')", name='check_difficulty_level'),
    )

class EvidenceItem(db.Model):
    """Individual evidence items for thought challenging"""
    id = db.Column(db.Integer, primary_key=True)
    thought_record_id = db.Column(db.Integer, db.ForeignKey('thought_record.id'), nullable=False)
    
    evidence_text = db.Column(db.Text, nullable=False)
    evidence_type = db.Column(db.String(20), nullable=False)  # supporting, contradicting
    strength_rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    category = db.Column(db.String(50))  # facts, past_experience, others_opinions, etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('strength_rating >= 1 AND strength_rating <= 5', name='check_strength_rating'),
        db.CheckConstraint("evidence_type IN ('supporting', 'contradicting')", name='check_evidence_type'),
    )

class DistortionAnalysis(db.Model):
    """Analysis of cognitive distortions in thoughts"""
    id = db.Column(db.Integer, primary_key=True)
    thought_record_id = db.Column(db.Integer, db.ForeignKey('thought_record.id'), nullable=False)
    
    distortion_type = db.Column(db.String(50), nullable=False)  # all_or_nothing, overgeneralization, etc.
    confidence_level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    explanation = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('confidence_level >= 1 AND confidence_level <= 10', name='check_confidence_level'),
    )

class CognitiveDistortion(db.Model):
    """Reference table for cognitive distortion types"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    examples = db.Column(db.Text)  # JSON array of examples
    difficulty_level = db.Column(db.String(20), default='beginner')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ThoughtRecordProgress(db.Model):
    """Track user progress in thought record skills"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # Skill metrics
    total_records_completed = db.Column(db.Integer, default=0)
    average_completion_time = db.Column(db.Float, default=0.0)
    distortion_identification_accuracy = db.Column(db.Float, default=0.0)
    balanced_thinking_score = db.Column(db.Float, default=0.0)
    
    # Achievement tracking
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.String(20), default='novice')  # novice, apprentice, detective, expert
    
    # Weekly metrics
    weekly_records_count = db.Column(db.Integer, default=0)
    weekly_cognitive_flexibility_score = db.Column(db.Float, default=0.0)
    
    # Metadata
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='thought_progress')

class ThoughtRecordTemplate(db.Model):
    """Templates for guided thought records"""
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    
    # Template structure
    situation_prompts = db.Column(db.Text)  # JSON array of prompts
    emotion_prompts = db.Column(db.Text)  # JSON array of prompts
    thought_prompts = db.Column(db.Text)  # JSON array of prompts
    evidence_prompts = db.Column(db.Text)  # JSON array of prompts
    
    # Usage tracking
    times_used = db.Column(db.Integer, default=0)
    average_effectiveness = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MindfulnessSession(db.Model):
    """Meditation and breathing exercise sessions"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    
    exercise_type = db.Column(db.String(50), nullable=False)  # meditation, breathing, body_scan, loving_kindness
    duration_planned = db.Column(db.Integer, nullable=False)  # minutes
    duration_actual = db.Column(db.Integer, nullable=True)  # minutes
    attention_checks_passed = db.Column(db.Integer, nullable=True)  # count of attention checks passed
    breathing_consistency = db.Column(db.Integer, nullable=True)  # 1-10 scale
    post_session_calm_rating = db.Column(db.Integer, nullable=True)  # 1-10 scale
    interruption_count = db.Column(db.Integer, nullable=True, default=0)  # number of interruptions
    technique_effectiveness = db.Column(db.Integer, nullable=True)  # 1-10 scale
    
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=True)
    completion_status = db.Column(db.String(20), nullable=False, default='started')  # started, completed, interrupted
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='mindfulness_sessions')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('duration_planned > 0', name='check_duration_planned'),
        db.CheckConstraint('duration_actual >= 0', name='check_duration_actual'),
        db.CheckConstraint('breathing_consistency >= 1 AND breathing_consistency <= 10', name='check_breathing_consistency'),
        db.CheckConstraint('post_session_calm_rating >= 1 AND post_session_calm_rating <= 10', name='check_calm_rating'),
        db.CheckConstraint('technique_effectiveness >= 1 AND technique_effectiveness <= 10', name='check_technique_effectiveness'),
    )

# Behavioral Activation Models
class ActivityCategory(db.Model):
    """Activity categories for behavioral activation"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # social, physical, creative, self-care, work, learning
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)  # emoji or icon class
    color = db.Column(db.String(20), nullable=False)  # hex color
    energy_level = db.Column(db.Integer, nullable=False)  # 1-10 scale for typical energy requirement
    social_factor = db.Column(db.Float, nullable=False)  # 0-1 scale (0=solo, 1=highly social)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Activity(db.Model):
    """Individual activities for behavioral activation"""
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('activity_category.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Activity characteristics
    estimated_duration = db.Column(db.Integer, nullable=False)  # minutes
    energy_cost = db.Column(db.Integer, nullable=False)  # 1-10 scale
    typical_enjoyment = db.Column(db.Integer, nullable=False)  # 1-10 scale
    social_level = db.Column(db.Float, nullable=False)  # 0-1 scale
    weather_dependent = db.Column(db.Boolean, default=False)
    indoor_outdoor = db.Column(db.String(20), nullable=False)  # indoor, outdoor, both
    cost_level = db.Column(db.String(20), nullable=False)  # free, low, medium, high
    
    # Seasonal and contextual factors
    seasonal_availability = db.Column(db.String(100))  # JSON array of seasons
    time_of_day_preference = db.Column(db.String(50))  # morning, afternoon, evening, any
    accessibility_requirements = db.Column(db.Text)  # JSON array of requirements
    
    # AI recommendation factors
    mood_boost_potential = db.Column(db.Integer, nullable=False)  # 1-10 scale
    anxiety_reduction_potential = db.Column(db.Integer, nullable=False)  # 1-10 scale
    depression_combat_potential = db.Column(db.Integer, nullable=False)  # 1-10 scale
    
    # Usage tracking
    times_suggested = db.Column(db.Integer, default=0)
    times_completed = db.Column(db.Integer, default=0)
    average_enjoyment_rating = db.Column(db.Float, default=0.0)
    average_energy_impact = db.Column(db.Float, default=0.0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    category = db.relationship('ActivityCategory', backref='activities')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('energy_cost >= 1 AND energy_cost <= 10', name='check_energy_cost'),
        db.CheckConstraint('typical_enjoyment >= 1 AND typical_enjoyment <= 10', name='check_typical_enjoyment'),
        db.CheckConstraint('social_level >= 0 AND social_level <= 1', name='check_social_level'),
        db.CheckConstraint('mood_boost_potential >= 1 AND mood_boost_potential <= 10', name='check_mood_boost'),
        db.CheckConstraint('anxiety_reduction_potential >= 1 AND anxiety_reduction_potential <= 10', name='check_anxiety_reduction'),
        db.CheckConstraint('depression_combat_potential >= 1 AND depression_combat_potential <= 10', name='check_depression_combat'),
        db.CheckConstraint("indoor_outdoor IN ('indoor', 'outdoor', 'both')", name='check_indoor_outdoor'),
        db.CheckConstraint("cost_level IN ('free', 'low', 'medium', 'high')", name='check_cost_level'),
    )

class ActivityPlan(db.Model):
    """Weekly activity planning for behavioral activation"""
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    
    # Plan metadata
    week_start_date = db.Column(db.Date, nullable=False, index=True)
    week_end_date = db.Column(db.Date, nullable=False, index=True)
    plan_status = db.Column(db.String(20), nullable=False, default='draft')  # draft, active, completed, archived
    
    # Plan characteristics
    total_activities_planned = db.Column(db.Integer, default=0)
    activities_completed = db.Column(db.Integer, default=0)
    completion_rate = db.Column(db.Float, default=0.0)
    
    # Balance metrics
    social_activities_count = db.Column(db.Integer, default=0)
    physical_activities_count = db.Column(db.Integer, default=0)
    creative_activities_count = db.Column(db.Integer, default=0)
    self_care_activities_count = db.Column(db.Integer, default=0)
    
    # Energy management
    average_daily_energy_cost = db.Column(db.Float, default=0.0)
    energy_distribution_score = db.Column(db.Float, default=0.0)  # How well energy is distributed
    
    # AI insights
    ai_recommendations_count = db.Column(db.Integer, default=0)
    user_customizations_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='activity_plans')
    scheduled_activities = db.relationship('ScheduledActivity', backref='plan', lazy=True, cascade='all, delete-orphan')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint("plan_status IN ('draft', 'active', 'completed', 'archived')", name='check_plan_status'),
        db.CheckConstraint('completion_rate >= 0 AND completion_rate <= 100', name='check_completion_rate'),
    )

class ScheduledActivity(db.Model):
    """Individual activities scheduled in a weekly plan"""
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('activity_plan.id'), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False, index=True)
    
    # Scheduling
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    scheduled_time = db.Column(db.Time, nullable=True)
    duration_planned = db.Column(db.Integer, nullable=False)  # minutes
    
    # Pre-activity predictions
    predicted_enjoyment = db.Column(db.Integer, nullable=True)  # 1-10 scale
    predicted_energy_cost = db.Column(db.Integer, nullable=True)  # 1-10 scale
    predicted_mood_boost = db.Column(db.Integer, nullable=True)  # 1-10 scale
    
    # Completion tracking
    completion_status = db.Column(db.String(20), nullable=False, default='scheduled')  # scheduled, in_progress, completed, skipped, rescheduled
    actual_start_time = db.Column(db.DateTime, nullable=True)
    actual_end_time = db.Column(db.DateTime, nullable=True)
    actual_duration = db.Column(db.Integer, nullable=True)  # minutes
    
    # Post-activity ratings
    actual_enjoyment = db.Column(db.Integer, nullable=True)  # 1-10 scale
    actual_energy_cost = db.Column(db.Integer, nullable=True)  # 1-10 scale
    actual_mood_boost = db.Column(db.Integer, nullable=True)  # 1-10 scale
    actual_energy_after = db.Column(db.Integer, nullable=True)  # 1-10 scale
    
    # Avoidance tracking
    avoidance_reason = db.Column(db.String(200), nullable=True)
    rescheduled_to = db.Column(db.Date, nullable=True)
    
    # AI and customization
    ai_recommended = db.Column(db.Boolean, default=False)
    user_customized = db.Column(db.Boolean, default=False)
    customization_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activity = db.relationship('Activity', backref='scheduled_instances')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('predicted_enjoyment >= 1 AND predicted_enjoyment <= 10', name='check_predicted_enjoyment'),
        db.CheckConstraint('predicted_energy_cost >= 1 AND predicted_energy_cost <= 10', name='check_predicted_energy_cost'),
        db.CheckConstraint('predicted_mood_boost >= 1 AND predicted_mood_boost <= 10', name='check_predicted_mood_boost'),
        db.CheckConstraint('actual_enjoyment >= 1 AND actual_enjoyment <= 10', name='check_actual_enjoyment'),
        db.CheckConstraint('actual_energy_cost >= 1 AND actual_energy_cost <= 10', name='check_actual_energy_cost'),
        db.CheckConstraint('actual_mood_boost >= 1 AND actual_mood_boost <= 10', name='check_actual_mood_boost'),
        db.CheckConstraint('actual_energy_after >= 1 AND actual_energy_after <= 10', name='check_actual_energy_after'),
        db.CheckConstraint("completion_status IN ('scheduled', 'in_progress', 'completed', 'skipped', 'rescheduled')", name='check_completion_status'),
    )

class ActivityMoodCorrelation(db.Model):
    """Track correlations between activities and mood changes"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False, index=True)
    
    # Correlation data
    correlation_strength = db.Column(db.Float, nullable=False)  # -1 to 1
    sample_size = db.Column(db.Integer, nullable=False)  # number of data points
    confidence_level = db.Column(db.Float, nullable=False)  # 0-1 scale
    
    # Mood impact metrics
    average_mood_before = db.Column(db.Float, nullable=False)  # 1-10 scale
    average_mood_after = db.Column(db.Float, nullable=False)  # 1-10 scale
    average_mood_change = db.Column(db.Float, nullable=False)  # difference
    
    # Energy impact metrics
    average_energy_before = db.Column(db.Float, nullable=False)  # 1-10 scale
    average_energy_after = db.Column(db.Float, nullable=False)  # 1-10 scale
    average_energy_change = db.Column(db.Float, nullable=False)  # difference
    
    # Consistency metrics
    completion_rate = db.Column(db.Float, nullable=False)  # 0-1 scale
    enjoyment_consistency = db.Column(db.Float, nullable=False)  # standard deviation of enjoyment ratings
    
    # Temporal patterns
    best_time_of_day = db.Column(db.String(20), nullable=True)  # morning, afternoon, evening
    best_day_of_week = db.Column(db.String(20), nullable=True)  # monday, tuesday, etc.
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='activity_mood_correlations')
    activity = db.relationship('Activity', backref='mood_correlations')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('correlation_strength >= -1 AND correlation_strength <= 1', name='check_correlation_strength'),
        db.CheckConstraint('confidence_level >= 0 AND confidence_level <= 1', name='check_confidence_level'),
        db.CheckConstraint('completion_rate >= 0 AND completion_rate <= 1', name='check_completion_rate'),
    )

class BehavioralActivationProgress(db.Model):
    """Track user progress in behavioral activation skills"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # Achievement tracking
    total_activities_completed = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.String(20), default='novice')  # novice, explorer, adventurer, master
    
    # Skill development
    prediction_accuracy_score = db.Column(db.Float, default=0.0)  # How well they predict enjoyment/energy
    variety_score = db.Column(db.Float, default=0.0)  # Activity variety bonus
    social_connection_score = db.Column(db.Float, default=0.0)  # Social activity engagement
    energy_management_score = db.Column(db.Float, default=0.0)  # Energy balance skills
    
    # Weekly metrics
    weekly_activities_count = db.Column(db.Integer, default=0)
    weekly_completion_rate = db.Column(db.Float, default=0.0)
    weekly_mood_improvement = db.Column(db.Float, default=0.0)
    
    # Avoidance tracking
    avoidance_patterns_identified = db.Column(db.Integer, default=0)
    last_avoidance_date = db.Column(db.Date, nullable=True)
    
    # Metadata
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='behavioral_progress')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('prediction_accuracy_score >= 0 AND prediction_accuracy_score <= 100', name='check_prediction_accuracy'),
        db.CheckConstraint('variety_score >= 0 AND variety_score <= 100', name='check_variety_score'),
        db.CheckConstraint('social_connection_score >= 0 AND social_connection_score <= 100', name='check_social_score'),
        db.CheckConstraint('energy_management_score >= 0 AND energy_management_score <= 100', name='check_energy_score'),
        db.CheckConstraint('weekly_completion_rate >= 0 AND weekly_completion_rate <= 100', name='check_weekly_completion'),
    )

class ActivityAchievement(db.Model):
    """Achievement system for behavioral activation"""
    id = db.Column(db.Integer, primary_key=True)
    achievement_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # explorer, predictor, social, energy, variety
    icon = db.Column(db.String(50), nullable=False)  # emoji or icon
    points = db.Column(db.Integer, nullable=False)  # points awarded
    requirements = db.Column(db.Text, nullable=False)  # JSON object with requirements
    is_hidden = db.Column(db.Boolean, default=False)  # Hidden until unlocked
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAchievement(db.Model):
    """User's earned achievements"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('activity_achievement.id'), nullable=False, index=True)
    
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='earned_achievements')
    achievement = db.relationship('ActivityAchievement', backref='earned_by')
    
    # Ensure unique combination
    __table_args__ = (
        db.UniqueConstraint('patient_id', 'achievement_id', name='unique_user_achievement'),
    )

# Engagement and Gamification Models

# Engagement and Gamification Models
class ExerciseStreak(db.Model):
    """Gamification data for exercise completion streaks"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    exercise_type = db.Column(db.String(50), nullable=False, index=True)  # cbt, mindfulness, mood_tracking
    
    current_streak = db.Column(db.Integer, nullable=False, default=0)
    longest_streak = db.Column(db.Integer, nullable=False, default=0)
    last_completion_date = db.Column(db.Date, nullable=True, index=True)
    streak_start_date = db.Column(db.Date, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='exercise_streaks')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('current_streak >= 0', name='check_current_streak'),
        db.CheckConstraint('longest_streak >= 0', name='check_longest_streak'),
        db.CheckConstraint("exercise_type IN ('cbt', 'mindfulness', 'mood_tracking', 'journaling')", name='check_streak_exercise_type'),
    )

class AchievementUnlocked(db.Model):
    """Progress milestones and achievements"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    achievement_type = db.Column(db.String(50), nullable=False)  # streak, completion, improvement
    
    achievement_name = db.Column(db.String(100), nullable=False)
    achievement_description = db.Column(db.String(200), nullable=False)
    criteria_met = db.Column(db.String(100), nullable=False)  # e.g., "7_day_streak", "10_exercises_completed"
    unlocked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    patient = db.relationship('Patient', backref='achievements')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint("achievement_type IN ('streak', 'completion', 'improvement', 'consistency')", name='check_achievement_type'),
    )

class PersonalizationData(db.Model):
    """Learned patient preferences and personalization data"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    
    preferred_exercise_types = db.Column(db.String(200), nullable=True)  # comma-separated: cbt, mindfulness
    preferred_duration_range = db.Column(db.String(20), nullable=True)  # e.g., "5-15_minutes"
    preferred_difficulty_level = db.Column(db.Integer, nullable=True)  # 1-5 scale
    best_time_of_day = db.Column(db.String(20), nullable=True)  # morning, afternoon, evening, night
    engagement_patterns = db.Column(db.JSON, nullable=True)  # JSON data about engagement patterns
    effectiveness_insights = db.Column(db.JSON, nullable=True)  # JSON data about what works best
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='personalization_data')
    
    # Validation
    __table_args__ = (
        db.CheckConstraint('preferred_difficulty_level >= 1 AND preferred_difficulty_level <= 5', name='check_preferred_difficulty'),
        db.CheckConstraint("best_time_of_day IN ('morning', 'afternoon', 'evening', 'night')", name='check_best_time'),
    )

# Smart Micro-Assessment System Models
class MicroAssessment(db.Model):
    """Real-time micro mood and context assessments"""
    __tablename__ = 'micro_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.String(100), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    mood_rating = db.Column(db.Integer, nullable=False)  # 1-10 scale
    mood_emoji = db.Column(db.String(10), nullable=False)
    energy_level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    stress_level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    context_data_id = db.Column(db.Integer, db.ForeignKey('context_data.id'), nullable=True)
    coping_skill_used = db.Column(db.String(50), nullable=True)
    coping_effectiveness = db.Column(db.Integer, nullable=True)  # 1-10 scale
    crisis_risk_level = db.Column(db.String(20), default='low')  # low, medium, high
    needs_immediate_support = db.Column(db.Boolean, default=False)
    response_time_seconds = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='micro_assessments')
    context_data = db.relationship('ContextData', backref='assessments')

class ContextData(db.Model):
    """Comprehensive context information for assessments"""
    __tablename__ = 'context_data'
    
    id = db.Column(db.Integer, primary_key=True)
    context_id = db.Column(db.String(100), unique=True, nullable=False)
    location_type = db.Column(db.String(50), nullable=True)  # home, work, social, outdoors, transit, other
    activity_type = db.Column(db.String(50), nullable=True)  # working, relaxing, socializing, exercising, eating, other
    social_situation = db.Column(db.String(50), nullable=True)  # alone, with_family, with_friends, with_colleagues, in_group
    environment_type = db.Column(db.String(50), nullable=True)  # indoors, outdoors, mixed
    noise_level = db.Column(db.String(50), nullable=True)  # quiet, moderate, loud, very_loud
    physical_state = db.Column(db.String(50), nullable=True)  # tired, energized, hungry, comfortable, stressed
    time_of_day = db.Column(db.String(50), nullable=True)  # morning, afternoon, evening, night
    day_of_week = db.Column(db.String(20), nullable=True)  # monday, tuesday, etc.
    is_weekend = db.Column(db.Boolean, default=False)
    weather_condition = db.Column(db.String(50), nullable=True)  # sunny, rainy, cloudy, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class NotificationSettings(db.Model):
    """Smart notification configuration for patients"""
    __tablename__ = 'notification_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), unique=True, nullable=False)
    frequency_type = db.Column(db.String(20), default='adaptive')  # fixed, adaptive, smart
    min_interval_hours = db.Column(db.Integer, default=1)
    max_interval_hours = db.Column(db.Integer, default=8)
    preferred_times = db.Column(db.JSON, nullable=True)  # Array of preferred hours
    avoid_times = db.Column(db.JSON, nullable=True)  # Array of hours to avoid
    avoid_meetings = db.Column(db.Boolean, default=True)
    avoid_sleep_hours = db.Column(db.Boolean, default=True)
    avoid_social_events = db.Column(db.Boolean, default=False)
    avoid_work_focus = db.Column(db.Boolean, default=True)
    show_coping_suggestions = db.Column(db.Boolean, default=True)
    show_progress_insights = db.Column(db.Boolean, default=True)
    emergency_contact_visible = db.Column(db.Boolean, default=True)
    crisis_mode_enabled = db.Column(db.Boolean, default=False)
    high_risk_frequency_multiplier = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='notification_settings')

class PatternAnalysis(db.Model):
    """AI-driven pattern recognition results"""
    __tablename__ = 'pattern_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.String(100), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    pattern_type = db.Column(db.String(50), nullable=False)  # mood_fluctuation, trigger_identification, etc.
    pattern_description = db.Column(db.Text, nullable=True)
    confidence_level = db.Column(db.Float, nullable=False)  # 0.0-1.0 scale
    trigger_context = db.Column(db.JSON, nullable=True)  # Mapping contexts to mood changes
    optimal_intervention_times = db.Column(db.JSON, nullable=True)  # Array of optimal hours
    escalation_risk_score = db.Column(db.Float, nullable=True)  # 0.0-1.0 scale
    early_warning_signals = db.Column(db.JSON, nullable=True)  # Array of warning signs
    intervention_recommendations = db.Column(db.JSON, nullable=True)  # Array of suggestions
    data_points_analyzed = db.Column(db.Integer, nullable=True)
    time_period_days = db.Column(db.Integer, nullable=True)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='pattern_analyses')

class EngagementMetrics(db.Model):
    """User engagement tracking and metrics"""
    __tablename__ = 'engagement_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), unique=True, nullable=False)
    current_streak_days = db.Column(db.Integer, default=0)
    longest_streak_days = db.Column(db.Integer, default=0)
    total_check_ins = db.Column(db.Integer, default=0)
    missed_check_ins = db.Column(db.Integer, default=0)
    avg_response_time_seconds = db.Column(db.Float, nullable=True)
    completion_rate = db.Column(db.Float, default=0.0)  # 0.0-1.0 scale
    engagement_score = db.Column(db.Float, default=0.0)  # 0.0-1.0 scale
    achievements_earned = db.Column(db.JSON, nullable=True)  # Array of achievements
    feature_usage_frequency = db.Column(db.JSON, nullable=True)  # Mapping feature to usage count
    last_check_in_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='engagement_metrics')

class ProviderExerciseFeedback(db.Model):
    """Provider feedback on exercise recommendations"""
    __tablename__ = 'provider_exercise_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recommendation_id = db.Column(db.String(100))
    exercise_type = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # approve, reject, modify, add, remove
    feedback_category = db.Column(db.String(50))
    feedback_text = db.Column(db.Text)
    modified_recommendations = db.Column(db.Text)  # JSON string
    clinical_rationale = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='provider_feedback')
    provider = db.relationship('User', backref='exercise_feedback')

# PHQ-9 Analysis System
class PHQ9AnalysisSystem:
    """Core PHQ-9 analysis and recommendation system"""
    
    def __init__(self):
        self.severity_levels = {
            'minimal': {'range': (0, 4), 'color': '#28a745', 'description': 'Minimal depression'},
            'mild': {'range': (5, 9), 'color': '#ffc107', 'description': 'Mild depression'},
            'moderate': {'range': (10, 14), 'color': '#fd7e14', 'description': 'Moderate depression'},
            'moderately_severe': {'range': (15, 19), 'color': '#dc3545', 'description': 'Moderately severe depression'},
            'severe': {'range': (20, 27), 'color': '#6f42c1', 'description': 'Severe depression'}
        }
    
    def analyze_assessment(self, scores):
        """Analyze PHQ-9 assessment and return comprehensive results"""
        total_score = sum(scores)
        severity = self.calculate_severity(total_score)
        q9_risk = scores[8] >= 2  # Question 9 (suicidal ideation)
        crisis_alert = q9_risk or total_score >= 20
        
        analysis = {
            'total_score': total_score,
            'severity_level': severity,
            'severity_info': self.severity_levels[severity],
            'q9_risk_flag': q9_risk,
            'crisis_alert': crisis_alert,
            'question_breakdown': self.get_question_breakdown(scores),
            'recommendations': self.generate_recommendations(severity, q9_risk, total_score),
            'risk_assessment': self.assess_risk(severity, q9_risk, total_score)
        }
        
        return analysis
    
    def calculate_severity(self, total_score):
        """Calculate severity level from total score"""
        if total_score <= 4:
            return 'minimal'
        elif total_score <= 9:
            return 'mild'
        elif total_score <= 14:
            return 'moderate'
        elif total_score <= 19:
            return 'moderately_severe'
        else:
            return 'severe'
    
    def get_question_breakdown(self, scores):
        """Get detailed breakdown of each question"""
        questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling/staying asleep, sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself",
            "Trouble concentrating",
            "Moving or speaking slowly/being fidgety",
            "Thoughts of self-harm or being better off dead"
        ]
        
        breakdown = []
        for i, (question, score) in enumerate(zip(questions, scores)):
            severity = self.get_question_severity(score)
            breakdown.append({
                'question_number': i + 1,
                'question_text': question,
                'score': score,
                'severity': severity,
                'is_high_risk': i == 8 and score >= 2  # Question 9 special handling
            })
        
        return breakdown
    
    def get_question_severity(self, score):
        """Get severity level for individual question score"""
        if score == 0:
            return 'none'
        elif score == 1:
            return 'mild'
        elif score == 2:
            return 'moderate'
        else:
            return 'severe'
    
    def generate_recommendations(self, severity, q9_risk, total_score):
        """Generate recommendations based on assessment results"""
        recommendations = {
            'immediate': [],
            'short_term': [],
            'long_term': []
        }
        
        # Immediate recommendations (crisis situations)
        if q9_risk:
            recommendations['immediate'].append({
                'text': '🚨 CRISIS ALERT: Please contact a mental health professional immediately or call a crisis hotline.',
                'priority': 'critical',
                'type': 'crisis_intervention'
            })
        
        if total_score >= 20:
            recommendations['immediate'].append({
                'text': '⚠️ High depression score detected. Consider speaking with a healthcare provider.',
                'priority': 'high',
                'type': 'professional_help'
            })
        
        # Short-term recommendations based on severity
        if severity in ['moderately_severe', 'severe']:
            recommendations['short_term'].append({
                'text': 'Consider scheduling an appointment with a mental health professional.',
                'priority': 'high',
                'type': 'professional_help'
            })
        
        if severity in ['moderate', 'moderately_severe', 'severe']:
            recommendations['short_term'].extend([
                {
                    'text': 'Practice daily breathing exercises for 5-10 minutes.',
                    'priority': 'medium',
                    'type': 'self_care'
                },
                {
                    'text': 'Try to maintain a regular sleep schedule.',
                    'priority': 'medium',
                    'type': 'lifestyle'
                },
                {
                    'text': 'Engage in light physical activity for 15-30 minutes daily.',
                    'priority': 'medium',
                    'type': 'exercise'
                }
            ])
        
        # Long-term recommendations
            recommendations['long_term'].extend([
            {
                'text': 'Consider regular therapy sessions for ongoing support.',
                'priority': 'medium',
                'type': 'therapy'
            },
            {
                'text': 'Build a support network of friends and family.',
                'priority': 'medium',
                'type': 'social_support'
            },
            {
                'text': 'Develop healthy coping mechanisms and stress management techniques.',
                'priority': 'medium',
                'type': 'coping_skills'
            }
            ])
        
        return recommendations
    
    def assess_risk(self, severity, q9_risk, total_score):
        """Assess overall risk level"""
        risk_level = 'low'
        risk_factors = []
        
        if q9_risk:
            risk_level = 'critical'
            risk_factors.append('Suicidal ideation detected')
        
        if total_score >= 20:
            risk_level = 'high'
            risk_factors.append('Severe depression score')
        elif total_score >= 15:
            risk_level = 'moderate'
            risk_factors.append('Moderately severe depression')
        elif total_score >= 10:
            risk_level = 'moderate'
            risk_factors.append('Moderate depression')
        
        if severity in ['moderately_severe', 'severe']:
            risk_factors.append('High severity level')
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'requires_immediate_attention': q9_risk or total_score >= 20
        }

# Initialize analysis system
phq9_analyzer = PHQ9AnalysisSystem()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'provider':
            return redirect(url_for('provider_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            if user.role == 'provider':
                return redirect(url_for('provider_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'patient')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('Access denied. Patient role required.', 'error')
        return redirect(url_for('index'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        # Create patient record if it doesn't exist
        patient = Patient(
            user_id=current_user.id,
            first_name=current_user.username,
            last_name='',
            age=25,
            gender='Unknown'
        )
        db.session.add(patient)
        db.session.commit()
    
    # Get recent assessments
    recent_assessments = PHQ9Assessment.query.filter_by(patient_id=patient.id)\
        .order_by(PHQ9Assessment.assessment_date.desc()).limit(5).all()
    
    # Get recent crisis alerts
    recent_alerts = CrisisAlert.query.filter_by(patient_id=patient.id)\
        .order_by(CrisisAlert.created_at.desc()).limit(5).all()
    
    # Get recent recommendations
    recent_recommendations = RecommendationResult.query.filter_by(patient_id=patient.id)\
        .order_by(RecommendationResult.created_at.desc()).limit(5).all()
    
    # Get placeholder data for other features
    journals = []
    moods = []
    goals = []
    
    return render_template('patient_dashboard.html', 
                         patient=patient,
                         assessments=recent_assessments,
                         alerts=recent_alerts,
                         recommendations=recent_recommendations,
                         journals=journals,
                         moods=moods,
                         goals=goals)

@app.route('/provider_dashboard')
@login_required
def provider_dashboard():
    if current_user.role != 'provider':
        flash('Access denied. Provider role required.', 'error')
        return redirect(url_for('index'))
    
    # Redirect to comprehensive dashboard by default
    return redirect('/provider/comprehensive_dashboard')

@app.route('/provider_dashboard_basic')
@login_required
def provider_dashboard_basic():
    if current_user.role != 'provider':
        flash('Access denied. Provider role required.', 'error')
        return redirect(url_for('index'))
    
    # Get all patients
    patients = Patient.query.all()
    
    # Get recent crisis alerts
    recent_alerts = CrisisAlert.query.filter_by(acknowledged=False)\
        .order_by(CrisisAlert.created_at.desc()).limit(10).all()
    
    # Get ML crisis detection alerts specifically
    ml_crisis_alerts = CrisisAlert.query.filter(
        CrisisAlert.alert_type.like('%ml_crisis_detection%'),
        CrisisAlert.acknowledged == False
    ).order_by(CrisisAlert.created_at.desc()).limit(5).all()
    
    # Get recent assessments
    recent_assessments = PHQ9Assessment.query\
        .order_by(PHQ9Assessment.assessment_date.desc()).limit(10).all()
    
    # Get crisis detection model status
    model_status = {
        'is_trained': crisis_detector.is_trained,
        'feature_count': len(crisis_detector.feature_names) if crisis_detector.feature_names else 0
    }
    
    # Add ML predictions for each patient
    patient_predictions = []
    for patient in patients:
        prediction_data = {
            'patient_id': patient.id,
            'rule_based_prediction': get_rule_based_prediction(patient),
            'ml_prediction': None,
            'combined_prediction': None,
            'ml_confidence': None
        }
        
        # Get ML prediction if model is trained
        if crisis_detector.is_trained:
            try:
                # Get latest assessment for this patient
                latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient.id)\
                    .order_by(PHQ9Assessment.assessment_date.desc()).first()
                
                if latest_assessment:
                    # Prepare patient data for ML prediction
                    patient_data = prepare_patient_data_for_crisis_detection(patient, latest_assessment)
                    ml_risk_assessment = crisis_detector.predict_crisis_risk(patient_data)
                    
                    prediction_data['ml_prediction'] = {
                        'risk_level': ml_risk_assessment['risk_level'],
                        'risk_probability': ml_risk_assessment['crisis_risk'],
                        'confidence': ml_risk_assessment['confidence']
                    }
                    
                    # Calculate combined prediction (70% ML, 30% rule-based)
                    combined_prediction = calculate_combined_prediction(
                        prediction_data['rule_based_prediction'],
                        ml_risk_assessment
                    )
                    prediction_data['combined_prediction'] = combined_prediction
                    prediction_data['ml_confidence'] = ml_risk_assessment['confidence']
                    
            except Exception as e:
                print(f"❌ Error getting ML prediction for patient {patient.id}: {str(e)}")
                prediction_data['ml_error'] = str(e)
        
        patient_predictions.append(prediction_data)
    
    return render_template('provider_dashboard.html',
                         patients=patients,
                         alerts=recent_alerts,
                         ml_crisis_alerts=ml_crisis_alerts,
                         assessments=recent_assessments,
                         model_status=model_status,
                         patient_predictions=patient_predictions)

@app.route('/api/ai_briefing/<int:patient_id>')
@login_required
def get_ai_briefing(patient_id):
    """Get AI-powered session briefing for a patient - Basic Dashboard Version"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied. Provider role required.'}), 403
    
    try:
        print(f"AI Briefing requested for patient {patient_id}")
        
        # Get patient data from database (this works in basic dashboard)
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        patient_name = f"{patient.first_name} {patient.last_name}"
        
        # Get recent data (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Query recent data
        mood_entries = MoodEntry.query.filter(
            MoodEntry.patient_id == patient_id,
            MoodEntry.timestamp >= thirty_days_ago
        ).order_by(MoodEntry.timestamp.desc()).limit(10).all()
        
        exercise_sessions = ExerciseSession.query.filter(
            ExerciseSession.patient_id == patient_id,
            ExerciseSession.completion_time >= thirty_days_ago
        ).order_by(ExerciseSession.completion_time.desc()).limit(10).all()
        
        phq9_assessments = PHQ9Assessment.query.filter(
            PHQ9Assessment.patient_id == patient_id,
            PHQ9Assessment.assessment_date >= thirty_days_ago
        ).order_by(PHQ9Assessment.assessment_date.desc()).limit(5).all()
        
        thought_records = []  # Add if you have this model
        crisis_alerts = CrisisAlert.query.filter(
            CrisisAlert.patient_id == patient_id,
            CrisisAlert.created_at >= thirty_days_ago
        ).all()
        
        # Prepare data summary
        data_summary = {
            'mood_entries_count': len(mood_entries),
            'exercise_sessions_count': len(exercise_sessions),
            'phq9_assessments_count': len(phq9_assessments),
            'thought_records_count': len(thought_records),
            'crisis_alerts_count': len(crisis_alerts)
        }
        
        # Create detailed prompt with real patient data
        mood_summary = []
        for entry in mood_entries[:5]:
            mood_summary.append(f"Date: {entry.timestamp.strftime('%Y-%m-%d')}, Intensity: {entry.intensity_level}/10, Energy: {entry.energy_level}/10, Notes: {entry.notes_brief[:100] if entry.notes_brief else 'No notes'}")
        
        exercise_summary = []
        for session in exercise_sessions[:5]:
            # Calculate duration if both start and completion times exist
            duration_minutes = None
            if session.completion_time and session.start_time:
                duration = session.completion_time - session.start_time
                duration_minutes = int(duration.total_seconds() / 60)
            
            # Get exercise type from the related exercise
            exercise_type = session.exercise.type if session.exercise else 'Unknown'
            
            # Use completion_time if available, otherwise start_time
            session_date = session.completion_time if session.completion_time else session.start_time
            
            exercise_summary.append(f"Date: {session_date.strftime('%Y-%m-%d')}, Type: {exercise_type}, Duration: {duration_minutes or 'N/A'}min, Status: {session.completion_status}")
        
        phq9_summary = []
        for assessment in phq9_assessments:
            phq9_summary.append(f"Date: {assessment.assessment_date.strftime('%Y-%m-%d')}, Score: {assessment.total_score}/27, Severity: {assessment.severity_level}")
        
        prompt = f"""
        Generate a clinical briefing for Patient {patient_id} ({patient_name}).
        
        PATIENT DATA SUMMARY (Last 30 days):
        
        MOOD ENTRIES ({len(mood_entries)} total):
        {chr(10).join(mood_summary) if mood_summary else "No recent mood entries"}
        
        EXERCISE SESSIONS ({len(exercise_sessions)} total):
        {chr(10).join(exercise_summary) if exercise_summary else "No recent exercise sessions"}
        
        PHQ-9 ASSESSMENTS ({len(phq9_assessments)} total):
        {chr(10).join(phq9_summary) if phq9_summary else "No recent PHQ-9 assessments"}
        
        THOUGHT RECORDS ({len(thought_records)} total):
        {"Recent thought records available" if thought_records else "No recent thought records"}
        
        CRISIS ALERTS ({len(crisis_alerts)} total):
        {"Recent crisis alerts detected" if crisis_alerts else "No recent crisis alerts"}
        
        Please provide a comprehensive clinical briefing including:
        
        1. Key clinical insights (3-5 bullet points based on the actual data)
        2. Treatment recommendations (3-4 recommendations based on patient's specific patterns)  
        3. A detailed briefing summary
        
        Focus on:
        - Depression assessment and monitoring trends
        - Mood tracking patterns and changes
        - Exercise and activity engagement levels
        - Crisis risk assessment based on data
        - Treatment adherence and progress
        - Provider action items specific to this patient
        
        Format as JSON with: key_insights (array), recommendations (array), briefing_text (string)
        """
        
        # Send to OpenAI
        import requests
        import os
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            print(f"Making API request to OpenAI...")
            response = requests.post(url, headers=headers, json=data, timeout=60, verify=False)
            print(f"API response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API error response: {response.text}")
                raise Exception(f"API returned status {response.status_code}: {response.text}")
            
            response_data = response.json()
            print(f"API response received successfully")
            ai_content = response_data['choices'][0]['message']['content']
            
            # Try to parse as JSON, fallback to text
            try:
                ai_data = json.loads(ai_content)
                key_insights = ai_data.get('key_insights', ['AI analysis completed'])
                recommendations = ai_data.get('recommendations', ['Continue current treatment'])
                briefing_text = ai_data.get('briefing_text', ai_content)
            except:
                key_insights = ['AI analysis completed']
                recommendations = ['Continue current treatment'] 
                briefing_text = ai_content
            
            print(f"✅ Successfully generated AI briefing for {patient_name}")
            
            return jsonify({
                'success': True,
                'patient_name': patient_name,
                'data_summary': data_summary,
                'briefing_text': briefing_text,
                'key_insights': key_insights,
                'recommendations': recommendations,
                'generated_at': datetime.now().isoformat(),
                'is_mock': False
            })
            
        except Exception as openai_error:
            print(f"OpenAI API error: {str(openai_error)}")
            # Fallback to a simple briefing if API fails
            return jsonify({
                'success': True,
                'patient_name': patient_name,
                'data_summary': data_summary,
                'briefing_text': f"Clinical Briefing for {patient_name}\n\nDue to API connectivity issues, this is a fallback briefing. The patient is being monitored in our PHQ-9 depression assessment system with regular mood tracking, exercise sessions, and assessments.\n\nNote: AI analysis temporarily unavailable. Please check OpenAI API configuration.",
                'key_insights': [
                    "Patient is actively engaged in treatment",
                    "Regular monitoring indicates good adherence",
                    "System is functioning for basic clinical needs"
                ],
                'recommendations': [
                    "Continue current treatment plan",
                    "Monitor patient progress weekly",
                    "Schedule follow-up assessment",
                    "Check API configuration for AI features"
                ],
                'generated_at': datetime.now().isoformat(),
                'is_mock': True
            })
        
    except Exception as e:
        print(f"Error generating AI briefing: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate briefing: {str(e)}'
        }), 500

@app.route('/phq9_assessment', methods=['GET', 'POST'])
@login_required
def phq9_assessment():
    if current_user.role != 'patient':
        flash('Access denied. Patient role required.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get form data
        scores = []
        for i in range(1, 10):
            score = int(request.form.get(f'q{i}', 0))
            scores.append(score)
        
        # Analyze assessment
        analysis = phq9_analyzer.analyze_assessment(scores)
        
        # Get or create patient
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            patient = Patient(
                user_id=current_user.id,
                first_name=current_user.username,
                last_name='',
                age=25,
                gender='Unknown'
            )
            db.session.add(patient)
            db.session.commit()
        
        # Create assessment record
        assessment = PHQ9Assessment(
            patient_id=patient.id,
            q1_score=scores[0], q2_score=scores[1], q3_score=scores[2],
            q4_score=scores[3], q5_score=scores[4], q6_score=scores[5],
            q7_score=scores[6], q8_score=scores[7], q9_score=scores[8],
            total_score=analysis['total_score'],
            severity_level=analysis['severity_level'],
            q9_risk_flag=analysis['q9_risk_flag'],
            crisis_alert_triggered=analysis['crisis_alert'],
            notes=f"PHQ-9 Assessment - {analysis['severity_level']} severity"
        )
        db.session.add(assessment)
        db.session.flush()  # Get the assessment ID
        
        # Run ML Crisis Detection
        try:
            if crisis_detector.is_trained:
                patient_data = prepare_patient_data_for_crisis_detection(patient, assessment)
                ml_risk_assessment = crisis_detector.predict_crisis_risk(patient_data)
                
                # Add ML risk assessment to analysis
                analysis['ml_crisis_risk'] = ml_risk_assessment['crisis_risk']
                analysis['ml_risk_level'] = ml_risk_assessment['risk_level']
                analysis['ml_confidence'] = ml_risk_assessment['confidence']
                
                # Create ML crisis alert if risk is high
                if ml_risk_assessment['risk_level'] in ['CRITICAL', 'HIGH']:
                    ml_crisis_alert = CrisisAlert(
                        assessment_id=assessment.id,
                        patient_id=patient.id,
                        alert_type='ml_crisis_detection',
                        alert_message=f"ML Crisis Detection: {ml_risk_assessment['risk_level']} risk detected (probability: {ml_risk_assessment['crisis_risk']:.3f})",
                        severity_level='critical' if ml_risk_assessment['risk_level'] == 'CRITICAL' else 'urgent',
                        acknowledged=False
                    )
                    db.session.add(ml_crisis_alert)
                    
                    # Update crisis alert flag if ML detects higher risk
                    if ml_risk_assessment['risk_level'] == 'CRITICAL':
                        analysis['crisis_alert'] = True
                        assessment.crisis_alert_triggered = True
            else:
                analysis['ml_crisis_risk'] = 0.0
                analysis['ml_risk_level'] = 'UNKNOWN'
                analysis['ml_confidence'] = 'LOW'
                analysis['ml_error'] = 'Model not trained'
        except Exception as e:
            print(f"❌ Error in ML crisis detection: {str(e)}")
            analysis['ml_crisis_risk'] = 0.0
            analysis['ml_risk_level'] = 'ERROR'
            analysis['ml_confidence'] = 'LOW'
            analysis['ml_error'] = str(e)
        
        # Create crisis alert if needed (original logic)
        if analysis['crisis_alert']:
            crisis_alert = CrisisAlert(
                assessment_id=assessment.id,
                patient_id=patient.id,
                alert_type='high_risk_phq9',
                alert_message=f"High-risk PHQ-9 assessment: Total score {analysis['total_score']}/27, Q9 score {scores[8]}/3",
                severity_level='critical' if analysis['q9_risk_flag'] else 'urgent',
                acknowledged=False
            )
            db.session.add(crisis_alert)
        
        # Create recommendations
        for rec_type, recommendations in analysis['recommendations'].items():
            for rec in recommendations:
                recommendation = RecommendationResult(
                    assessment_id=assessment.id,
                    patient_id=patient.id,
                    recommendation_type=rec_type,
                    recommendation_text=rec['text'],
                    priority_level=rec['priority'],
                    ai_generated=True
                )
                db.session.add(recommendation)
        
        # Update patient summary
        patient.total_assessments += 1
        patient.current_phq9_severity = analysis['severity_level']
        patient.last_assessment_date = datetime.utcnow()
        
        db.session.commit()
        
        flash('Assessment completed successfully!', 'success')
        return render_template('assessment_results.html', analysis=analysis, assessment=assessment)
    
    return render_template('phq9_assessment.html')

@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    if request.method == 'POST':
        # Create journal entry (placeholder - you can add a Journal model later)
        flash('Journal entry saved!', 'success')
        return redirect(url_for('journal'))
    
    return render_template('journal.html')

# Mood tracker route is now handled by the mood_tracking blueprint
# @app.route('/mood_tracker', methods=['GET', 'POST'])
# @login_required
# def mood_tracker():
#     if request.method == 'POST':
#         # Create mood entry (placeholder - you can add a MoodEntry model later)
#         flash('Mood entry saved!', 'success')
#         return redirect(url_for('mood_tracker'))
#     
#     return render_template('mood_tracker.html')

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    if request.method == 'POST':
        # Create goal (placeholder - you can add a Goal model later)
        flash('Goal saved!', 'success')
        return redirect(url_for('goals'))
    
    return render_template('goals.html')

@app.route('/insights')
@login_required
def insights():
    if current_user.role != 'patient':
        flash('Access denied. Patient role required.', 'error')
        return redirect(url_for('index'))
    
    # Get patient data
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Get PHQ-9 assessment data
    assessments = PHQ9Assessment.query.filter_by(patient_id=patient.id)\
        .order_by(PHQ9Assessment.assessment_date.desc()).all()
    
    # Calculate insights
    if assessments:
        # Calculate average PHQ-9 score
        avg_phq9_score = sum(assessment.total_score for assessment in assessments) / len(assessments)
        
        # Get severity distribution
        severity_counts = {}
        for assessment in assessments:
            severity = assessment.severity_level
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Get recent risk levels (last 5 assessments)
        recent_risk_levels = []
        for assessment in assessments[:5]:
            if assessment.total_score >= 20:
                risk_level = 'HIGH'
            elif assessment.total_score >= 15:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            recent_risk_levels.append(risk_level)
        
        # Get trend analysis
        if len(assessments) >= 2:
            latest_score = assessments[0].total_score
            previous_score = assessments[1].total_score
            trend = 'improving' if latest_score < previous_score else 'worsening' if latest_score > previous_score else 'stable'
        else:
            trend = 'insufficient_data'
    else:
        avg_phq9_score = 0
        severity_counts = {}
        recent_risk_levels = []
        trend = 'no_data'
    
    insights_data = {
        'avg_phq9_score': round(avg_phq9_score, 1),
        'total_assessments': len(assessments),
        'severity_distribution': severity_counts,
        'recent_risk_levels': recent_risk_levels,
        'trend': trend,
        'current_severity': patient.current_phq9_severity if patient else 'unknown',
        'last_assessment_date': patient.last_assessment_date if patient else None
    }
    
    return render_template('insights.html', insights=insights_data, assessments=assessments)

@app.route('/analytics')
@login_required
def analytics_dashboard():
    """Analytics dashboard for PHQ-9 assessment data"""
    if current_user.role != 'provider':
        flash('Access denied. Provider role required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get analytics data
    total_patients = Patient.query.count()
    total_assessments = PHQ9Assessment.query.count()
    total_crisis_alerts = CrisisAlert.query.filter_by(acknowledged=False).count()
    
    # Get severity distribution
    severity_counts = db.session.query(
        PHQ9Assessment.severity_level,
        db.func.count(PHQ9Assessment.id)
    ).group_by(PHQ9Assessment.severity_level).all()
    
    analytics_data = {
        'total_patients': total_patients,
        'total_assessments': total_assessments,
        'total_crisis_alerts': total_crisis_alerts,
        'severity_distribution': dict(severity_counts)
    }
    
    return render_template('analytics.html', analytics=analytics_data)

# CBT Thought Record Routes
@app.route('/thought_record')
@login_required
def thought_record_dashboard():
    """Main thought record dashboard"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Get user's thought record progress
    progress = ThoughtRecordProgress.query.filter_by(patient_id=patient.id).first()
    if not progress:
        progress = ThoughtRecordProgress(patient_id=patient.id)
        db.session.add(progress)
        db.session.commit()
    
    # Get recent thought records
    recent_records = ThoughtRecord.query.filter_by(patient_id=patient.id).order_by(ThoughtRecord.created_at.desc()).limit(5).all()
    
    # Get cognitive distortion patterns
    distortion_patterns = db.session.query(
        DistortionAnalysis.distortion_type,
        db.func.count(DistortionAnalysis.id)
    ).join(ThoughtRecord).filter(ThoughtRecord.patient_id == patient.id).group_by(DistortionAnalysis.distortion_type).all()
    
    dashboard_data = {
        'progress': progress,
        'recent_records': recent_records,
        'distortion_patterns': dict(distortion_patterns),
        'total_records': len(recent_records)
    }
    
    return render_template('thought_record_dashboard.html', data=dashboard_data)

@app.route('/thought_record/new', methods=['GET', 'POST'])
@login_required
def new_thought_record():
    """Create a new thought record"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('patient_dashboard'))
    
    if request.method == 'POST':
        # Get form data
        situation_category = request.form.get('situation_category')
        situation_description = request.form.get('situation_description')
        primary_emotion = request.form.get('primary_emotion')
        emotion_intensity = int(request.form.get('emotion_intensity', 5))
        initial_thought = request.form.get('initial_thought')
        thought_confidence = int(request.form.get('thought_confidence', 5))
        
        # Create thought record
        thought_record = ThoughtRecord(
            record_id=f"TR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            patient_id=patient.id,
            situation_category=situation_category,
            situation_description=situation_description,
            primary_emotion=primary_emotion,
            emotion_intensity=emotion_intensity,
            initial_thought=initial_thought,
            thought_confidence=thought_confidence,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(thought_record)
        db.session.commit()
        
        flash('Thought record created successfully!', 'success')
        return redirect(url_for('thought_record_evidence', record_id=thought_record.id))
    
    # Get available templates
    templates = ThoughtRecordTemplate.query.filter_by(difficulty_level='beginner').all()
    
    return render_template('new_thought_record.html', templates=templates)

@app.route('/thought_record/<int:record_id>/evidence', methods=['GET', 'POST'])
@login_required
def thought_record_evidence(record_id):
    """Add evidence analysis to thought record"""
    thought_record = ThoughtRecord.query.get_or_404(record_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if thought_record.patient_id != patient.id:
        flash('Access denied.', 'error')
        return redirect(url_for('thought_record_dashboard'))
    
    if request.method == 'POST':
        # Get evidence data
        supporting_evidence = request.form.getlist('supporting_evidence[]')
        contradicting_evidence = request.form.getlist('contradicting_evidence[]')
        
        # Update thought record
        thought_record.supporting_evidence = json.dumps(supporting_evidence)
        thought_record.contradicting_evidence = json.dumps(contradicting_evidence)
        
        db.session.commit()
        
        return redirect(url_for('thought_record_balanced', record_id=record_id))
    
    return render_template('thought_record_evidence.html', record=thought_record)

@app.route('/thought_record/<int:record_id>/balanced', methods=['GET', 'POST'])
@login_required
def thought_record_balanced(record_id):
    """Create balanced thought"""
    thought_record = ThoughtRecord.query.get_or_404(record_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if thought_record.patient_id != patient.id:
        flash('Access denied.', 'error')
        return redirect(url_for('thought_record_dashboard'))
    
    if request.method == 'POST':
        # Get balanced thought data
        balanced_thought = request.form.get('balanced_thought')
        balanced_confidence = int(request.form.get('balanced_confidence', 5))
        outcome_rating = int(request.form.get('outcome_rating', 5))
        mood_improvement = int(request.form.get('mood_improvement', 5))
        
        # Update thought record
        thought_record.balanced_thought = balanced_thought
        thought_record.balanced_confidence = balanced_confidence
        thought_record.outcome_rating = outcome_rating
        thought_record.mood_improvement = mood_improvement
        
        # Update progress
        progress = ThoughtRecordProgress.query.filter_by(patient_id=patient.id).first()
        if progress:
            progress.total_records_completed += 1
            progress.current_streak += 1
            if progress.current_streak > progress.longest_streak:
                progress.longest_streak = progress.current_streak
            progress.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        flash('Thought record completed successfully!', 'success')
        return redirect(url_for('thought_record_dashboard'))
    
    return render_template('thought_record_balanced.html', record=thought_record)

@app.route('/api/cognitive_distortions', methods=['POST'])
@login_required
def analyze_cognitive_distortions():
    """Analyze thought for cognitive distortions using AI"""
    data = request.get_json()
    thought_text = data.get('thought')
    
    if not claude_client:
        return jsonify({'error': 'AI analysis not available'}), 503
    
    try:
        # Analyze thought for cognitive distortions
        prompt = f"""
        Analyze the following thought for cognitive distortions. Identify any of these common distortions:
        - All-or-nothing thinking
        - Catastrophizing
        - Overgeneralization
        - Mental filter
        - Disqualifying the positive
        - Jumping to conclusions (mind reading, fortune telling)
        - Emotional reasoning
        - Should statements
        - Labeling
        - Personalization
        
        Thought: "{thought_text}"
        
        Return a JSON response with:
        {{
            "distortions": [
                {{
                    "type": "distortion_name",
                    "confidence": 1-10,
                    "explanation": "brief explanation"
                }}
            ]
        }}
        """
        
        response = claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        analysis = json.loads(response.content[0].text)
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing cognitive distortions: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/api/suggest_balanced_thought', methods=['POST'])
@login_required
def suggest_balanced_thought():
    """Suggest balanced alternative thoughts using AI"""
    data = request.get_json()
    initial_thought = data.get('initial_thought')
    supporting_evidence = data.get('supporting_evidence', [])
    contradicting_evidence = data.get('contradicting_evidence', [])
    
    if not claude_client:
        return jsonify({'error': 'AI suggestions not available'}), 503
    
    try:
        # Generate balanced thought suggestions
        prompt = f"""
        Based on the initial thought and evidence analysis, suggest 3 balanced alternative thoughts.
        
        Initial thought: "{initial_thought}"
        Supporting evidence: {supporting_evidence}
        Contradicting evidence: {contradicting_evidence}
        
        Return a JSON response with:
        {{
            "suggestions": [
                {{
                    "thought": "balanced thought text",
                    "reasoning": "brief explanation of why this is balanced"
                }}
            ]
        }}
        """
        
        response = claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        suggestions = json.loads(response.content[0].text)
        return jsonify(suggestions)
        
    except Exception as e:
        logger.error(f"Error suggesting balanced thoughts: {e}")
        return jsonify({'error': 'Suggestion failed'}), 500

# Behavioral Activation Routes
@app.route('/behavioral_activation')
@login_required
def behavioral_activation_dashboard():
    """Main behavioral activation dashboard"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Get or create progress tracking
    progress = BehavioralActivationProgress.query.filter_by(patient_id=patient.id).first()
    if not progress:
        progress = BehavioralActivationProgress(patient_id=patient.id)
        db.session.add(progress)
        db.session.commit()
    
    # Get current week's plan
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    current_plan = ActivityPlan.query.filter_by(
        patient_id=patient.id,
        week_start_date=week_start,
        plan_status='active'
    ).first()
    
    # Get recent activities
    recent_activities = ScheduledActivity.query.join(ActivityPlan).filter(
        ActivityPlan.patient_id == patient.id
    ).order_by(ScheduledActivity.scheduled_date.desc()).limit(10).all()
    
    # Get activity categories
    categories = ActivityCategory.query.filter_by(is_active=True).all()
    
    # Get achievements
    earned_achievements = UserAchievement.query.filter_by(patient_id=patient.id).all()
    
    dashboard_data = {
        'progress': progress,
        'current_plan': current_plan,
        'recent_activities': recent_activities,
        'categories': categories,
        'earned_achievements': earned_achievements,
        'week_start': week_start,
        'week_end': week_end
    }
    
    return render_template('behavioral_activation.html', data=dashboard_data, timedelta=timedelta)

@app.route('/behavioral_activation/plan', methods=['GET', 'POST'])
@login_required
def activity_planning():
    """Weekly activity planning interface"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('patient_dashboard'))
    
    if request.method == 'POST':
        try:
            print("POST request received for activity planning")
            print("Form data:", request.form)
            
            # Handle plan creation/update
            week_start = datetime.strptime(request.form.get('week_start'), '%Y-%m-%d').date()
            week_end = datetime.strptime(request.form.get('week_end'), '%Y-%m-%d').date()
            
            print(f"Week start: {week_start}, Week end: {week_end}")
            
            # Create or update plan
            plan = ActivityPlan.query.filter_by(
                patient_id=patient.id,
                week_start_date=week_start
            ).first()
            
            if not plan:
                plan = ActivityPlan(
                    plan_id=f"plan_{patient.id}_{week_start.strftime('%Y%m%d')}",
                    patient_id=patient.id,
                    week_start_date=week_start,
                    week_end_date=week_end,
                    plan_status='draft'
                )
                db.session.add(plan)
                print(f"Created new plan: {plan.plan_id}")
            else:
                print(f"Found existing plan: {plan.plan_id}")
            
            # Process scheduled activities
            activities_data = request.form.getlist('activities[]')
            print(f"Received {len(activities_data)} activities")
            
            for i, activity_data in enumerate(activities_data):
                if activity_data:
                    try:
                        activity_info = json.loads(activity_data)
                        print(f"Activity {i+1}: {activity_info}")
                        
                        scheduled_activity = ScheduledActivity(
                            plan_id=plan.id,
                            activity_id=activity_info['activity_id'],
                            scheduled_date=datetime.strptime(activity_info['date'], '%Y-%m-%d').date(),
                            scheduled_time=datetime.strptime(activity_info['time'], '%H:%M').time() if activity_info.get('time') else None,
                            duration_planned=activity_info['duration'],
                            predicted_enjoyment=activity_info.get('predicted_enjoyment'),
                            predicted_energy_cost=activity_info.get('predicted_energy_cost'),
                            predicted_mood_boost=activity_info.get('predicted_mood_boost'),
                            ai_recommended=activity_info.get('ai_recommended', False),
                            user_customized=activity_info.get('user_customized', False)
                        )
                        db.session.add(scheduled_activity)
                        print(f"Added scheduled activity: {activity_info.get('activity_id')}")
                    except Exception as e:
                        print(f"Error processing activity {i+1}: {e}")
                        continue
            
            plan.plan_status = 'active'
            db.session.commit()
            print("Plan saved successfully")
            flash('Activity plan saved successfully!', 'success')
            return redirect(url_for('behavioral_activation_dashboard'))
            
        except Exception as e:
            print(f"Error saving plan: {e}")
            db.session.rollback()
            flash(f'Error saving plan: {str(e)}', 'error')
            return redirect(url_for('activity_planning'))
    
    # GET request - show planning interface
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get available activities
    activities = Activity.query.filter_by(is_active=True).all()
    
    # Get existing plan
    existing_plan = ActivityPlan.query.filter_by(
        patient_id=patient.id,
        week_start_date=week_start
    ).first()
    
    planning_data = {
        'week_start': week_start,
        'week_end': week_end,
        'activities': activities,
        'existing_plan': existing_plan
    }
    
    return render_template('activity_planning.html', data=planning_data, timedelta=timedelta)

@app.route('/behavioral_activation/activities')
@login_required
def activity_library():
    """Activity library and recommendations"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Get all activities grouped by category
    categories = ActivityCategory.query.filter_by(is_active=True).all()
    activities_by_category = {}
    all_activities = []
    
    for category in categories:
        activities = Activity.query.filter_by(
            category_id=category.id,
            is_active=True
        ).all()
        activities_by_category[category] = activities
        all_activities.extend(activities)
    
    # Get user's mood correlations
    correlations = ActivityMoodCorrelation.query.filter_by(patient_id=patient.id).all()
    
    library_data = {
        'categories': categories,
        'activities_by_category': activities_by_category,
        'activities': all_activities,
        'correlations': correlations
    }
    
    return render_template('activity_library.html', data=library_data)

@app.route('/behavioral_activation/track/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def track_activity(activity_id):
    """Track activity completion and mood impact"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('behavioral_activation_dashboard'))
    
    scheduled_activity = ScheduledActivity.query.filter_by(id=activity_id).first()
    if not scheduled_activity:
        flash('Activity not found.', 'error')
        return redirect(url_for('behavioral_activation_dashboard'))
    
    if request.method == 'POST':
        # Handle activity completion tracking
        actual_enjoyment = int(request.form.get('actual_enjoyment'))
        actual_energy_cost = int(request.form.get('actual_energy_cost'))
        actual_mood_boost = int(request.form.get('actual_mood_boost'))
        actual_energy_after = int(request.form.get('actual_energy_after'))
        
        # Update scheduled activity
        scheduled_activity.completion_status = 'completed'
        scheduled_activity.actual_start_time = datetime.now()
        scheduled_activity.actual_end_time = datetime.now()
        scheduled_activity.actual_enjoyment = actual_enjoyment
        scheduled_activity.actual_energy_cost = actual_energy_cost
        scheduled_activity.actual_mood_boost = actual_mood_boost
        scheduled_activity.actual_energy_after = actual_energy_after
        
        # Update activity statistics
        activity = scheduled_activity.activity
        activity.times_completed += 1
        activity.average_enjoyment_rating = (
            (activity.average_enjoyment_rating * (activity.times_completed - 1) + actual_enjoyment) / 
            activity.times_completed
        )
        
        # Update progress
        progress = BehavioralActivationProgress.query.filter_by(patient_id=patient.id).first()
        if progress:
            progress.total_activities_completed += 1
            progress.current_streak += 1
            if progress.current_streak > progress.longest_streak:
                progress.longest_streak = progress.current_streak
        
        db.session.commit()
        flash('Activity completed and tracked successfully!', 'success')
        return redirect(url_for('behavioral_activation_dashboard'))
    
    # GET request - show tracking form
    return render_template('activity_tracking.html', activity=scheduled_activity)

@app.route('/api/behavioral_activation/recommendations', methods=['POST'])
@login_required
def get_activity_recommendations():
    """Get AI-powered activity recommendations"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    try:
        data = request.get_json()
        current_mood = data.get('current_mood', 5)
        current_energy = data.get('current_energy', 5)
        weather = data.get('weather', 'unknown')
        time_of_day = data.get('time_of_day', 'any')
        social_preference = data.get('social_preference', 0.5)
        
        # Get user's mood correlations
        correlations = ActivityMoodCorrelation.query.filter_by(patient_id=patient.id).all()
        
        # Get suitable activities
        activities = Activity.query.filter_by(is_active=True).all()
        
        # Score activities based on user preferences and correlations
        scored_activities = []
        for activity in activities:
            score = 0
            
            # Base score from typical enjoyment
            score += activity.typical_enjoyment * 2
            
            # Mood boost potential
            if current_mood < 5:
                score += activity.mood_boost_potential * 3
            
            # Energy matching
            energy_diff = abs(activity.energy_cost - current_energy)
            score += (10 - energy_diff) * 2
            
            # Social preference matching
            social_diff = abs(activity.social_level - social_preference)
            score += (1 - social_diff) * 2
            
            # Weather consideration
            if activity.weather_dependent and weather != 'unknown':
                if (weather in ['sunny', 'clear'] and activity.indoor_outdoor in ['outdoor', 'both']) or \
                   (weather in ['rainy', 'stormy'] and activity.indoor_outdoor in ['indoor', 'both']):
                    score += 3
            
            # Time of day consideration
            if activity.time_of_day_preference and time_of_day != 'any':
                if activity.time_of_day_preference == time_of_day:
                    score += 2
            
            # User correlation bonus
            correlation = next((c for c in correlations if c.activity_id == activity.id), None)
            if correlation and correlation.correlation_strength > 0.3:
                score += correlation.correlation_strength * 5
            
            scored_activities.append({
                'activity': activity,
                'score': score,
                'correlation': correlation
            })
        
        # Sort by score and return top recommendations
        scored_activities.sort(key=lambda x: x['score'], reverse=True)
        recommendations = scored_activities[:10]
        
        return jsonify({
            'recommendations': [
                {
                    'id': rec['activity'].id,
                    'name': rec['activity'].name,
                    'description': rec['activity'].description,
                    'category': rec['activity'].category.name,
                    'duration': rec['activity'].estimated_duration,
                    'energy_cost': rec['activity'].energy_cost,
                    'typical_enjoyment': rec['activity'].typical_enjoyment,
                    'score': rec['score'],
                    'correlation_strength': rec['correlation'].correlation_strength if rec['correlation'] else None
                }
                for rec in recommendations
            ]
        })
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return jsonify({'error': 'Failed to generate recommendations'}), 500

@app.route('/test_drag_drop')
def test_drag_drop():
    """Test page for drag and drop functionality"""
    return render_template('test_drag_drop.html')

@app.route('/api/behavioral_activation/insights', methods=['GET'])
@login_required
def get_behavioral_insights():
    """Get behavioral activation insights for providers"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get all patients' behavioral data
        patients = Patient.query.all()
        insights = []
        
        for patient in patients:
            progress = BehavioralActivationProgress.query.filter_by(patient_id=patient.id).first()
            if not progress:
                continue
            
            # Get recent activities
            recent_activities = ScheduledActivity.query.join(ActivityPlan).filter(
                ActivityPlan.patient_id == patient.id,
                ScheduledActivity.completion_status == 'completed'
            ).order_by(ScheduledActivity.actual_end_time.desc()).limit(20).all()
            
            # Calculate insights
            completion_rate = progress.weekly_completion_rate
            mood_improvement = progress.weekly_mood_improvement
            avoidance_count = progress.avoidance_patterns_identified
            
            # Determine risk level
            risk_level = 'low'
            if completion_rate < 50 or mood_improvement < 0 or avoidance_count > 3:
                risk_level = 'high'
            elif completion_rate < 70 or mood_improvement < 1:
                risk_level = 'medium'
            
            insights.append({
                'patient_id': patient.id,
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'completion_rate': completion_rate,
                'mood_improvement': mood_improvement,
                'avoidance_patterns': avoidance_count,
                'risk_level': risk_level,
                'total_activities': progress.total_activities_completed,
                'current_streak': progress.current_streak
            })
        
        return jsonify({'insights': insights})
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return jsonify({'error': 'Failed to generate insights'}), 500

# Mood analytics route is now handled by the mood_analytics blueprint
# @app.route('/mood-analytics')
# @login_required
# def mood_analytics_dashboard():
#     """Mood analytics dashboard"""
#     return redirect(url_for('mood_analytics.mood_analytics_dashboard'))

# Create database tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created")
    
    # Import and register blueprints after models are created
    try:
        # Import the modules
        import mood_tracking_interface
        import mood_analytics_dashboard
        import mindfulness_interface
        
        # Set up the imports in the modules
        mood_tracking_interface.db = db
        mood_tracking_interface.Patient = Patient
        mood_tracking_interface.MoodEntry = MoodEntry
        mood_tracking_interface.ExerciseStreak = ExerciseStreak
        mood_tracking_interface.AchievementUnlocked = AchievementUnlocked
        
        mood_analytics_dashboard.db = db
        mood_analytics_dashboard.Patient = Patient
        mood_analytics_dashboard.MoodEntry = MoodEntry
        mood_analytics_dashboard.ExerciseStreak = ExerciseStreak
        mood_analytics_dashboard.AchievementUnlocked = AchievementUnlocked
        
        mindfulness_interface.db = db
        mindfulness_interface.Patient = Patient
        mindfulness_interface.MindfulnessSession = MindfulnessSession
        mindfulness_interface.ExerciseStreak = ExerciseStreak
        mindfulness_interface.AchievementUnlocked = AchievementUnlocked
        
        # Register the blueprints
        app.register_blueprint(mood_tracking_interface.mood_tracking)
        app.register_blueprint(mood_analytics_dashboard.mood_analytics)
        app.register_blueprint(mindfulness_interface.mindfulness_exercises)
        
        # Register smart micro-assessment blueprint
        try:
            import smart_micro_assessment
            # Set up the models
            smart_micro_assessment.db = db
            smart_micro_assessment.Patient = Patient
            smart_micro_assessment.CrisisAlert = CrisisAlert
            smart_micro_assessment.MicroAssessment = MicroAssessment
            smart_micro_assessment.ContextData = ContextData
            smart_micro_assessment.NotificationSettings = NotificationSettings
            smart_micro_assessment.PatternAnalysis = PatternAnalysis
            smart_micro_assessment.EngagementMetrics = EngagementMetrics
            app.register_blueprint(smart_micro_assessment.smart_assessment)
            print("✅ Smart micro-assessment blueprint registered")
        except ImportError as e:
            print(f"⚠️ Could not import smart micro-assessment: {e}")
        
        print("✅ All blueprints registered")
    except ImportError as e:
        print(f"⚠️ Could not import blueprints: {e}")
        print("📝 Some features will be disabled...")
    
    # Create default users if they don't exist
    if not User.query.filter_by(username='patient1').first():
        patient1 = User(
            username='patient1',
            email='patient1@example.com',
            password_hash=generate_password_hash('password123'),
            role='patient'
        )
        db.session.add(patient1)
    
    if not User.query.filter_by(username='provider1').first():
        provider1 = User(
            username='provider1',
            email='provider1@example.com',
            password_hash=generate_password_hash('password123'),
            role='provider'
        )
        db.session.add(provider1)
    
    db.session.commit()
    print("✅ Found", User.query.count(), "existing users")

# PHQ-9 Exercise Integration Routes
@app.route('/api/phq9_exercise_integration')
@login_required
def phq9_exercise_integration_api():
    """Get PHQ-9 exercise integration data for current patient"""
    if current_user.role != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get latest PHQ-9 assessment
        latest_assessment = PHQ9Assessment.query.filter_by(
            patient_id=patient.id
        ).order_by(desc(PHQ9Assessment.assessment_date)).first()
        
        if not latest_assessment:
            return jsonify({
                'success': True,
                'data': {
                    'show_integration': False,
                    'message': 'No PHQ-9 assessment found. Please complete an assessment first.'
                }
            })
        
        # Generate exercise recommendations
        from phq9_exercise_integration import phq9_exercise_integration
        recommendations = phq9_exercise_integration.generate_phq9_based_recommendations(
            patient.id, latest_assessment.id
        )
        
        if 'error' in recommendations:
            return jsonify({'error': recommendations['error']}), 500
        
        # Prepare response data
        response_data = {
            'show_integration': True,
            'severity_level': latest_assessment.severity_level,
            'last_assessment': latest_assessment.assessment_date.strftime('%Y-%m-%d'),
            'skill_level': recommendations['patient_profile']['skill_level'],
            'show_crisis_alert': latest_assessment.q9_risk_flag or latest_assessment.crisis_alert_triggered,
            'recommendations': [],
            'recommended_exercises': []
        }
        
        # Process recommendations
        exercise_recs = recommendations['exercise_recommendations']
        if 'primary_exercises' in exercise_recs:
            response_data['recommended_exercises'] = [
                {
                    'type': 'box-breathing',
                    'name': 'Box Breathing',
                    'description': 'Structured breathing for stress relief',
                    'icon': '📦',
                    'difficulty': 'beginner'
                },
                {
                    'type': 'mindful-breathing',
                    'name': 'Mindful Breathing',
                    'description': 'Natural breathing with awareness',
                    'icon': '🌸',
                    'difficulty': 'beginner'
                }
            ]
        
        # Add crisis exercises if needed
        if response_data['show_crisis_alert']:
            response_data['recommended_exercises'].extend([
                {
                    'type': 'crisis-breathing',
                    'name': 'Crisis Breathing',
                    'description': 'Emergency breathing technique',
                    'icon': '🆘',
                    'difficulty': 'crisis'
                },
                {
                    'type': 'grounding-54321',
                    'name': 'Grounding 5-4-3-2-1',
                    'description': 'Grounding using your five senses',
                    'icon': '🌍',
                    'difficulty': 'crisis'
                }
            ])
        
        # Add recommendations
        if 'anxiety_management' in exercise_recs:
            response_data['recommendations'].append({
                'title': 'Anxiety Management',
                'description': 'Breathing exercises recommended for anxiety symptoms'
            })
        
        if 'crisis_interventions' in exercise_recs:
            response_data['recommendations'].append({
                'title': 'Crisis Support',
                'description': 'Crisis intervention exercises available for immediate support'
            })
        
        return jsonify({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        logger.error(f"Error in PHQ-9 exercise integration API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/mindfulness_progress')
@login_required
def mindfulness_progress_api():
    """Get mindfulness progress data for current patient"""
    if current_user.role != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get mindfulness sessions
        mindfulness_sessions = MindfulnessSession.query.filter_by(
            patient_id=patient.id
        ).all()
        
        # Calculate progress metrics
        total_sessions = len(mindfulness_sessions)
        completed_sessions = sum(1 for session in mindfulness_sessions if session.completion_time)
        
        # Calculate current streak
        current_streak = 0
        if mindfulness_sessions:
            # Sort by date and calculate streak
            sorted_sessions = sorted(mindfulness_sessions, key=lambda x: x.start_time, reverse=True)
            current_date = datetime.now().date()
            
            for session in sorted_sessions:
                session_date = session.start_time.date()
                if session_date == current_date or session_date == current_date - timedelta(days=1):
                    current_streak += 1
                    current_date = session_date
                else:
                    break
        
        # Calculate average effectiveness
        effectiveness_ratings = [session.effectiveness_rating for session in mindfulness_sessions if session.effectiveness_rating]
        avg_effectiveness = sum(effectiveness_ratings) / len(effectiveness_ratings) if effectiveness_ratings else 0
        
        # Calculate weekly progress (simplified)
        week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        weekly_sessions = [s for s in mindfulness_sessions if s.start_time.date() >= week_start]
        weekly_progress = min(100, (len(weekly_sessions) / 7) * 100)  # Assuming 7 sessions per week goal
        
        return jsonify({
            'success': True,
            'data': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'current_streak': current_streak,
                'avg_effectiveness': round(avg_effectiveness, 1),
                'weekly_progress': round(weekly_progress, 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in mindfulness progress API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/save_mindfulness_session', methods=['POST'])
@login_required
def save_mindfulness_session_api():
    """Save mindfulness session data"""
    if current_user.role != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Create mindfulness session
        session = MindfulnessSession(
            patient_id=patient.id,
            technique_type=data.get('exercise_type', 'mindful-breathing'),
            session_duration=data.get('duration', 0),
            engagement_level=8,  # Default engagement level
            effectiveness_rating=data.get('effectiveness_rating', 7),
            completion_time=datetime.utcnow() if data.get('completion_status') == 'completed' else None
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session saved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error saving mindfulness session: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/exercise_feedback_loop')
@login_required
def exercise_feedback_loop_api():
    """Get exercise feedback loop data"""
    if current_user.role != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        from phq9_exercise_integration import phq9_exercise_integration
        
        # Get feedback loops
        feedback_loops = phq9_exercise_integration.create_feedback_loops(patient.id)
        
        return jsonify({
            'success': True,
            'data': feedback_loops
        })
        
    except Exception as e:
        logger.error(f"Error in exercise feedback loop API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/patient_profile_comprehensive')
@login_required
def patient_profile_comprehensive_api():
    """Get comprehensive patient profile combining PHQ-9 and exercise data"""
    if current_user.role != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        from phq9_exercise_integration import phq9_exercise_integration
        
        # Get comprehensive profile
        profile = phq9_exercise_integration.build_comprehensive_patient_profile(patient.id)
        
        return jsonify({
            'success': True,
            'data': profile
        })
        
    except Exception as e:
        logger.error(f"Error in comprehensive patient profile API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/provider_workflow_integration')
@login_required
def provider_workflow_integration_api():
    """Get provider workflow integration data"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        patient_id = request.args.get('patient_id', type=int)
        if not patient_id:
            return jsonify({'error': 'Patient ID required'}), 400
        
        from phq9_exercise_integration import phq9_exercise_integration
        
        # Get workflow integration
        workflow = phq9_exercise_integration.generate_provider_workflow_integration(patient_id)
        
        return jsonify({
            'success': True,
            'data': workflow
        })
        
    except Exception as e:
        logger.error(f"Error in provider workflow integration API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/holistic_progress_measurement')
@login_required
def holistic_progress_measurement_api():
    """Get holistic progress measurement data"""
    if current_user.role != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        from phq9_exercise_integration import phq9_exercise_integration
        
        # Get holistic metrics
        metrics = phq9_exercise_integration.create_holistic_progress_measurement(patient.id)
        
        return jsonify({
            'success': True,
            'data': metrics
        })
        
    except Exception as e:
        logger.error(f"Error in holistic progress measurement API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Register dashboard blueprints
app.register_blueprint(comprehensive_dashboard_blueprint, url_prefix='/provider')

# Add AI Briefing Test route directly to main app for testing
@app.route('/ai_briefing_test')
@login_required
def ai_briefing_test_direct():
    """AI Briefing Test Page - Direct route for testing"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied. Provider role required.'}), 403
    
    return render_template('ai_briefing_test.html')

# Import and register AI briefing system
from ai_briefing_routes import ai_briefing
app.register_blueprint(ai_briefing, url_prefix='/provider')

# Provider feedback API endpoints (defined here to avoid SQLAlchemy context issues)
@app.route('/provider/api/patients')
@login_required
def provider_api_patients():
    """API endpoint to get all patients for provider feedback"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get real patients from database
        patients = Patient.query.all()
        
        patient_data = []
        for patient in patients:
            try:
                # Get latest PHQ-9 assessment
                latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient.id)\
                    .order_by(PHQ9Assessment.assessment_date.desc()).first()
                
                patient_data.append({
                    'id': patient.id,
                    'first_name': patient.first_name,
                    'last_name': patient.last_name,
                    'age': patient.age,
                    'gender': patient.gender,
                    'current_phq9_severity': latest_assessment.severity_level if latest_assessment else 'unknown',
                    'last_assessment_date': latest_assessment.assessment_date.isoformat() if latest_assessment else None
                })
            except Exception as e:
                logger.error(f"Error processing patient {patient.id}: {e}")
                # Add patient with minimal data
                patient_data.append({
                    'id': patient.id,
                    'first_name': 'Patient',
                    'last_name': f'#{patient.id}',
                    'age': patient.age or 0,
                    'gender': patient.gender or 'Unknown',
                    'current_phq9_severity': 'unknown',
                    'last_assessment_date': None
                })
        
        return jsonify({'patients': patient_data})
    except Exception as e:
        logger.error(f"Error getting patients: {str(e)}")
        return jsonify({'error': 'Failed to get patients'}), 500

@app.route('/provider/api/provider_exercise_dashboard')
@login_required  
def provider_api_dashboard():
    """API endpoint for provider dashboard data"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get real data from database
        patients = Patient.query.all()
        
        # Get recent feedback from this provider
        recent_feedback = ProviderExerciseFeedback.query.filter_by(provider_id=current_user.id)\
            .order_by(ProviderExerciseFeedback.submitted_at.desc()).limit(5).all()
        
        # Get feedback analytics
        all_feedback = ProviderExerciseFeedback.query.filter_by(provider_id=current_user.id).all()
        
        # Calculate feedback analytics
        action_dist = {}
        category_dist = {}
        for feedback in all_feedback:
            action_dist[feedback.action] = action_dist.get(feedback.action, 0) + 1
            if feedback.feedback_category:
                category_dist[feedback.feedback_category] = category_dist.get(feedback.feedback_category, 0) + 1
        
        # Get patient summaries with latest PHQ-9 scores
        patient_summaries = []
        for patient in patients:
            latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient.id)\
                .order_by(PHQ9Assessment.assessment_date.desc()).first()
            
            last_feedback = ProviderExerciseFeedback.query.filter_by(
                patient_id=patient.id, provider_id=current_user.id
            ).order_by(ProviderExerciseFeedback.submitted_at.desc()).first()
            
            patient_summaries.append({
                'id': patient.id,
                'name': f"{patient.first_name} {patient.last_name}",
                'phq9_score': latest_assessment.total_score if latest_assessment else 0,
                'severity': latest_assessment.severity_level if latest_assessment else 'unknown',
                'last_feedback': last_feedback.action if last_feedback else 'none',
                'last_feedback_date': last_feedback.submitted_at.isoformat() if last_feedback else None
            })
        
        dashboard_data = {
            'provider_id': current_user.id,
            'total_patients': len(patients),
            'pending_reviews': len(patients),
            'recent_feedback': [],
            'patient_summaries': patient_summaries,
            'feedback_analytics': {
                'total_feedback': len(all_feedback),
                'action_distribution': action_dist,
                'category_distribution': category_dist
            },
            'rl_progress': {
                'training_samples': len(all_feedback),
                'model_accuracy': 0.75,
                'daily_feedback_rate': 5,
                'data_quality': 0.85
            }
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        logger.error(f"Error getting provider dashboard: {str(e)}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500

@app.route('/provider/api/patient_exercise_recommendations/<int:patient_id>')
@login_required
def provider_api_patient_recommendations(patient_id):
    """API endpoint to get patient exercise recommendations"""
    print(f"🔍 API called for patient {patient_id}")
    print(f"🔍 Current user: {current_user}")
    print(f"🔍 User role: {current_user.role if current_user else 'None'}")
    
    if current_user.role != 'provider':
        print(f"❌ Access denied - user role: {current_user.role}")
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        print(f"✅ Authentication passed for patient {patient_id}")
        from phq9_exercise_integration import PHQ9ExerciseIntegration
        
        # Get patient data
        print(f"🔍 Getting patient data for {patient_id}")
        patient = Patient.query.get_or_404(patient_id)
        print(f"✅ Found patient: {patient.first_name} {patient.last_name}")
        
        # Get latest PHQ-9 assessment
        print(f"🔍 Getting PHQ-9 assessment for {patient_id}")
        latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(PHQ9Assessment.assessment_date.desc()).first()
        
        if not latest_assessment:
            print(f"❌ No PHQ-9 assessment found for patient {patient_id}")
            return jsonify({'error': 'No PHQ-9 assessment found for this patient'}), 404
        
        print(f"✅ Found PHQ-9 assessment: Score {latest_assessment.total_score}, Severity {latest_assessment.severity_level}")
        
        # Generate exercise recommendations
        print(f"🔍 Generating recommendations for patient {patient_id}")
        integration = PHQ9ExerciseIntegration()
        recommendations = integration.generate_adaptive_recommendations(
            patient_id=patient_id,
            assessment_id=latest_assessment.id
        )
        print(f"✅ Generated recommendations: {type(recommendations)}")
        
        # Get exercise history
        exercise_sessions = db.session.query(ExerciseSession, Exercise)\
            .join(Exercise, ExerciseSession.exercise_id == Exercise.exercise_id)\
            .filter(ExerciseSession.patient_id == patient_id)\
            .order_by(ExerciseSession.session_date.desc()).limit(10).all()
        
        exercise_history = []
        for session, exercise in exercise_sessions:
            exercise_history.append({
                'exercise_name': exercise.name,
                'exercise_type': exercise.type,
                'session_date': session.session_date.isoformat(),
                'completion_status': session.completion_status,
                'duration_minutes': session.duration_minutes,
                'mood_before': session.mood_before,
                'mood_after': session.mood_after
            })
        
        # Get previous provider feedback
        previous_feedback = ProviderExerciseFeedback.query.filter_by(patient_id=patient_id)\
            .order_by(ProviderExerciseFeedback.submitted_at.desc()).limit(5).all()
        
        feedback_history = []
        for feedback in previous_feedback:
            feedback_history.append({
                'exercise_type': feedback.exercise_type,
                'action': feedback.action,
                'feedback_category': feedback.feedback_category,
                'feedback_text': feedback.feedback_text,
                'submitted_at': feedback.submitted_at.isoformat()
            })
        
        # Format recommendations for display
        print(f"🔍 Formatting recommendations for patient {patient_id}")
        formatted_recommendations = []
        if 'exercise_recommendations' in recommendations:
            exercise_recs = recommendations['exercise_recommendations']
            
            # Process daily exercises
            if 'daily' in exercise_recs:
                for i, exercise_name in enumerate(exercise_recs['daily']):
                    formatted_recommendations.append({
                        'exercise_id': f'daily_{i}',
                        'exercise_name': exercise_name.replace('_', ' ').title(),
                        'exercise_type': 'daily',
                        'difficulty_level': 'easy',
                        'estimated_duration': 5,
                        'clinical_focus': ['mood_tracking', 'awareness'],
                        'rationale': 'Daily maintenance exercise for minimal depression',
                        'priority': 'high',
                        'engagement_mechanics': ['quick_check', 'self_reflection']
                    })
            
            # Process weekly exercises
            if 'weekly' in exercise_recs:
                for i, exercise_name in enumerate(exercise_recs['weekly']):
                    formatted_recommendations.append({
                        'exercise_id': f'weekly_{i}',
                        'exercise_name': exercise_name.replace('_', ' ').title(),
                        'exercise_type': 'weekly',
                        'difficulty_level': 'medium',
                        'estimated_duration': 15,
                        'clinical_focus': ['wellness', 'gratitude'],
                        'rationale': 'Weekly wellness exercise for minimal depression',
                        'priority': 'medium',
                        'engagement_mechanics': ['reflection', 'tracking']
                    })
        
        print(f"🔍 Building response data for patient {patient_id}")
        response_data = {
            'patient_info': {
                'id': patient.id,
                'name': f"{patient.first_name} {patient.last_name}",
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'age': patient.age,
                'gender': patient.gender,
                'total_score': latest_assessment.total_score,
                'current_phq9_score': latest_assessment.total_score,
                'current_severity': latest_assessment.severity_level,
                'current_phq9_severity': latest_assessment.severity_level,
                'last_assessment': latest_assessment.assessment_date.isoformat(),
                'assessment_date': latest_assessment.assessment_date.isoformat(),
                'q9_risk': latest_assessment.q9_risk_flag,
                'risk_flag': latest_assessment.q9_risk_flag
            },
            'recommendations': {
                'severity_based_recommendations': {
                    'daily': formatted_recommendations[:3],  # First 3 as daily
                    'weekly': formatted_recommendations[3:]  # Rest as weekly
                },
                'raw_recommendations': formatted_recommendations
            },
            'exercise_history': exercise_history,
            'feedback_history': feedback_history,
            'previous_feedback': feedback_history
        }
        
        print(f"✅ Response data built successfully for patient {patient_id}")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error getting patient recommendations: {str(e)}")
        return jsonify({'error': 'Failed to get patient recommendations'}), 500

# Simple exercise feedback page
@app.route('/provider/simple_exercise_feedback')
@login_required
def simple_exercise_feedback():
    """Simple exercise feedback page"""
    if current_user.role != 'provider':
        return redirect(url_for('login'))
    return render_template('simple_exercise_feedback.html')

# Provider feedback system integrated directly into main app

@app.route('/provider/api/submit_feedback', methods=['POST'])
@login_required
def submit_provider_feedback():
    """API endpoint to submit provider feedback on exercise recommendations"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['patient_id', 'exercise_name', 'action', 'exercise_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create feedback record
        feedback = ProviderExerciseFeedback(
            patient_id=data['patient_id'],
            provider_id=current_user.id,
            recommendation_id=f"simple_{data['exercise_name'].replace(' ', '_').lower()}",
            exercise_type=data['exercise_type'],
            action=data['action'],
            feedback_category='exercise_recommendation',
            feedback_text=data.get('feedback_text', ''),
            clinical_rationale=data.get('clinical_rationale', ''),
            submitted_at=datetime.utcnow()
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        print(f"✅ Feedback saved: {data['action']} for {data['exercise_name']} by provider {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': f'Feedback recorded: {data["action"]} for {data["exercise_name"]}',
            'feedback_id': feedback.id
        })
        
    except Exception as e:
        print(f"❌ Error saving feedback: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to save feedback'}), 500

@app.route('/provider/api/feedback_history/<int:patient_id>')
@login_required
def get_feedback_history(patient_id):
    """API endpoint to get feedback history for a patient"""
    try:
        feedback_records = ProviderExerciseFeedback.query.filter_by(patient_id=patient_id)\
            .order_by(ProviderExerciseFeedback.submitted_at.desc()).limit(10).all()
        
        feedback_data = []
        for feedback in feedback_records:
            feedback_data.append({
                'id': feedback.id,
                'exercise_name': feedback.recommendation_id.replace('simple_', '').replace('_', ' ').title(),
                'action': feedback.action,
                'feedback_text': feedback.feedback_text,
                'submitted_at': feedback.submitted_at.isoformat()
            })
        
        return jsonify({'feedback_history': feedback_data})
        
    except Exception as e:
        print(f"❌ Error getting feedback history: {str(e)}")
        return jsonify({'error': 'Failed to get feedback history'}), 500

@app.route('/provider/api/session_briefing/<int:patient_id>')
@login_required
def get_session_briefing(patient_id):
    """API endpoint to generate AI-powered pre-session intelligence briefing"""
    try:
        if not claude_client:
            # Provide a mock briefing when Claude API is not available
            return generate_mock_briefing(patient_id)
        
        # Get patient data
        patient = Patient.query.get_or_404(patient_id)
        
        # Get latest PHQ-9 assessment
        latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(PHQ9Assessment.assessment_date.desc()).first()
        
        if not latest_assessment:
            return jsonify({'error': 'No PHQ-9 assessment found for this patient'}), 404
        
        # Get recent exercise sessions (last 14 days)
        from datetime import datetime, timedelta
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        
        exercise_sessions = db.session.query(ExerciseSession, Exercise)\
            .join(Exercise, ExerciseSession.exercise_id == Exercise.exercise_id)\
            .filter(ExerciseSession.patient_id == patient_id)\
            .filter(ExerciseSession.start_time >= two_weeks_ago)\
            .order_by(ExerciseSession.start_time.desc()).all()
        
        # Get recent mood entries (last 14 days)
        mood_entries = MoodEntry.query.filter_by(patient_id=patient_id)\
            .filter(MoodEntry.timestamp >= two_weeks_ago)\
            .order_by(MoodEntry.timestamp.desc()).all()
        
        # Get recent provider feedback
        recent_feedback = ProviderExerciseFeedback.query.filter_by(patient_id=patient_id)\
            .order_by(ProviderExerciseFeedback.submitted_at.desc()).limit(5).all()
        
        # Prepare data for AI analysis
        exercise_summary = []
        for session, exercise in exercise_sessions:
            # Calculate duration if both start and completion times exist
            duration_minutes = None
            if session.completion_time and session.start_time:
                duration = session.completion_time - session.start_time
                duration_minutes = int(duration.total_seconds() / 60)
            
            exercise_summary.append({
                'exercise_name': exercise.name,
                'exercise_type': exercise.type,
                'session_date': session.start_time.isoformat(),
                'completion_status': session.completion_status,
                'duration_minutes': duration_minutes,
                'engagement_score': session.engagement_score,
                'effectiveness_rating': session.effectiveness_rating,
                'collected_data': session.collected_data
            })
        
        mood_summary = []
        for mood in mood_entries:
            mood_summary.append({
                'timestamp': mood.timestamp.isoformat(),
                'intensity_level': mood.intensity_level,
                'energy_level': mood.energy_level,
                'sleep_quality': mood.sleep_quality
            })
        
        feedback_summary = []
        for feedback in recent_feedback:
            feedback_summary.append({
                'exercise_name': feedback.recommendation_id.replace('simple_', '').replace('_', ' ').title(),
                'action': feedback.action,
                'feedback_text': feedback.feedback_text,
                'submitted_at': feedback.submitted_at.isoformat()
            })
        
        # Create AI prompt
        prompt = f"""
You are a clinical AI assistant providing pre-session intelligence briefings for mental health providers. 

PATIENT PROFILE:
- Name: {patient.first_name} {patient.last_name}
- Age: {patient.age}
- Gender: {patient.gender}
- Current PHQ-9 Score: {latest_assessment.total_score}/27
- Current Severity: {latest_assessment.severity_level}
- Last Assessment: {latest_assessment.assessment_date.strftime('%Y-%m-%d')}

RECENT EXERCISE ACTIVITY (Last 14 days):
{exercise_summary}

RECENT MOOD TRACKING (Last 14 days):
{mood_summary}

RECENT PROVIDER FEEDBACK:
{feedback_summary}

Please provide a comprehensive pre-session briefing that includes:

1. **EXERCISE ENGAGEMENT ANALYSIS**: Patterns in exercise completion, engagement scores, and effectiveness ratings
2. **MOOD TRAJECTORY INSIGHTS**: Trends in mood intensity, energy levels, and sleep quality
3. **CLINICAL OBSERVATIONS**: Key patterns that may indicate progress or concerns
4. **SESSION FOCUS AREAS**: Specific topics to address based on recent activity
5. **EXERCISE RECOMMENDATIONS**: Suggested modifications or new exercises based on feedback
6. **RISK ASSESSMENT**: Any concerning patterns that need immediate attention
7. **PROGRESS INDICATORS**: Positive changes and areas of improvement

Format the response as a professional clinical briefing with clear sections and actionable insights.
"""

        # Generate AI briefing
        try:
            response = claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            briefing_text = response.content[0].text
            
            # Parse the briefing into sections for better display
            sections = parse_briefing_sections(briefing_text)
            
            return jsonify({
                'success': True,
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'briefing_text': briefing_text,
                'sections': sections,
                'data_summary': {
                    'exercise_sessions_count': len(exercise_summary),
                    'mood_entries_count': len(mood_summary),
                    'feedback_count': len(feedback_summary),
                    'phq9_score': latest_assessment.total_score,
                    'severity': latest_assessment.severity_level
                }
            })
        except Exception as claude_error:
            print(f"❌ Claude API error: {str(claude_error)}")
            # Fallback to mock briefing if Claude API fails
            return generate_mock_briefing(patient_id, exercise_summary, mood_summary, feedback_summary, latest_assessment)
        
    except Exception as e:
        print(f"❌ Error generating session briefing: {str(e)}")
        return jsonify({'error': 'Failed to generate session briefing'}), 500

# ============================================================================
# CRISIS DETECTION API ROUTES
# ============================================================================

@app.route('/api/crisis_detection/assess_risk', methods=['POST'])
@login_required
def assess_crisis_risk():
    """Assess crisis risk for a patient using XGBoost model"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({'error': 'Patient ID is required'}), 400
        
        # Get patient data
        patient = Patient.query.get_or_404(patient_id)
        
        # Get latest PHQ-9 assessment
        latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(PHQ9Assessment.assessment_date.desc()).first()
        
        if not latest_assessment:
            return jsonify({'error': 'No PHQ-9 assessment found for this patient'}), 404
        
        # Prepare patient data for crisis detection
        patient_data = prepare_patient_data_for_crisis_detection(patient, latest_assessment)
        
        # Get crisis risk assessment
        risk_assessment = crisis_detector.predict_crisis_risk(patient_data)
        
        # Create crisis alert if risk is high
        if risk_assessment['risk_level'] in ['CRITICAL', 'HIGH']:
            crisis_alert = CrisisAlert(
                patient_id=patient_id,
                assessment_id=latest_assessment.id,
                alert_type='ml_crisis_detection',
                alert_message=f"ML Crisis Detection Alert: {risk_assessment['risk_level']} risk detected (probability: {risk_assessment['crisis_risk']:.3f})",
                severity_level='critical' if risk_assessment['risk_level'] == 'CRITICAL' else 'urgent'
            )
            db.session.add(crisis_alert)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'risk_assessment': risk_assessment,
            'patient_id': patient_id,
            'assessment_id': latest_assessment.id
        })
        
    except Exception as e:
        print(f"❌ Error assessing crisis risk: {str(e)}")
        return jsonify({'error': 'Failed to assess crisis risk'}), 500

@app.route('/api/crisis_detection/batch_assess', methods=['POST'])
@login_required
def batch_assess_crisis_risk():
    """Batch assess crisis risk for multiple patients"""
    try:
        if current_user.role != 'provider':
            return jsonify({'error': 'Provider access required'}), 403
        
        data = request.get_json()
        patient_ids = data.get('patient_ids', [])
        
        if not patient_ids:
            # Get all patients if no specific IDs provided
            patients = Patient.query.all()
            patient_ids = [p.id for p in patients]
        
        results = []
        alerts_created = 0
        
        for patient_id in patient_ids:
            try:
                patient = Patient.query.get(patient_id)
                if not patient:
                    continue
                
                # Get latest PHQ-9 assessment
                latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                    .order_by(PHQ9Assessment.assessment_date.desc()).first()
                
                if not latest_assessment:
                    continue
                
                # Prepare patient data
                patient_data = prepare_patient_data_for_crisis_detection(patient, latest_assessment)
                
                # Get risk assessment
                risk_assessment = crisis_detector.predict_crisis_risk(patient_data)
                
                # Create crisis alert if high risk
                if risk_assessment['risk_level'] in ['CRITICAL', 'HIGH']:
                    crisis_alert = CrisisAlert(
                        patient_id=patient_id,
                        assessment_id=latest_assessment.id,
                        alert_type='ml_crisis_detection_batch',
                        alert_message=f"Batch ML Crisis Detection: {risk_assessment['risk_level']} risk (probability: {risk_assessment['crisis_risk']:.3f})",
                        severity_level='critical' if risk_assessment['risk_level'] == 'CRITICAL' else 'urgent'
                    )
                    db.session.add(crisis_alert)
                    alerts_created += 1
                
                results.append({
                    'patient_id': patient_id,
                    'patient_name': f"{patient.first_name} {patient.last_name}",
                    'risk_assessment': risk_assessment
                })
                
            except Exception as e:
                print(f"❌ Error processing patient {patient_id}: {str(e)}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'results': results,
            'alerts_created': alerts_created,
            'total_patients': len(results)
        })
        
    except Exception as e:
        print(f"❌ Error in batch crisis assessment: {str(e)}")
        return jsonify({'error': 'Failed to perform batch crisis assessment'}), 500

@app.route('/api/crisis_detection/train_model', methods=['POST'])
@login_required
def train_crisis_detection_model():
    """Train the crisis detection model with current data"""
    try:
        if current_user.role != 'provider':
            return jsonify({'error': 'Provider access required'}), 403
        
        # Get training data from database
        training_data, labels = prepare_training_data_for_crisis_detection()
        
        if len(training_data) < 10:
            return jsonify({'error': 'Insufficient training data. Need at least 10 samples.'}), 400
        
        # Train the model
        accuracy = crisis_detector.train(training_data, labels)
        
        return jsonify({
            'success': True,
            'accuracy': accuracy,
            'training_samples': len(training_data),
            'message': 'Crisis detection model trained successfully'
        })
        
    except Exception as e:
        print(f"❌ Error training crisis detection model: {str(e)}")
        return jsonify({'error': 'Failed to train crisis detection model'}), 500

@app.route('/api/crisis_detection/model_status')
@login_required
def get_crisis_detection_model_status():
    """Get crisis detection model status and information"""
    try:
        status = {
            'is_trained': crisis_detector.is_trained,
            'model_path': crisis_detector.model_path,
            'feature_count': len(crisis_detector.feature_names) if crisis_detector.feature_names else 0
        }
        
        if crisis_detector.is_trained and crisis_detector.feature_names:
            # Get feature importance
            feature_importance = dict(zip(crisis_detector.feature_names, crisis_detector.model.feature_importances_))
            status['top_features'] = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return jsonify({
            'success': True,
            'model_status': status
        })
        
    except Exception as e:
        print(f"❌ Error getting model status: {str(e)}")
        return jsonify({'error': 'Failed to get model status'}), 500

@app.route('/provider/crisis_detection')
@login_required
def crisis_detection_management():
    """Crisis detection management page for providers"""
    if current_user.role != 'provider':
        flash('Access denied. Provider role required.', 'error')
        return redirect(url_for('index'))
    
    # Get all ML crisis alerts
    ml_alerts = CrisisAlert.query.filter(
        CrisisAlert.alert_type.like('%ml_crisis_detection%')
    ).order_by(CrisisAlert.created_at.desc()).limit(20).all()
    
    # Get model status
    model_status = {
        'is_trained': crisis_detector.is_trained,
        'feature_count': len(crisis_detector.feature_names) if crisis_detector.feature_names else 0,
        'model_path': crisis_detector.model_path
    }
    
    # Get recent assessments with ML risk data
    recent_assessments = PHQ9Assessment.query\
        .order_by(PHQ9Assessment.assessment_date.desc()).limit(10).all()
    
    return render_template('crisis_detection_management.html',
                         ml_alerts=ml_alerts,
                         model_status=model_status,
                         recent_assessments=recent_assessments)

@app.route('/provider/crisis_detection/batch_assess_all', methods=['POST'])
@login_required
def batch_assess_all_patients():
    """Batch assess all patients for crisis risk"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Provider access required'}), 403
    
    try:
        # Get all patients
        patients = Patient.query.all()
        patient_ids = [p.id for p in patients]
        
        # Perform batch assessment
        results = []
        alerts_created = 0
        
        for patient_id in patient_ids:
            try:
                patient = Patient.query.get(patient_id)
                if not patient:
                    continue
                
                # Get latest PHQ-9 assessment
                latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                    .order_by(PHQ9Assessment.assessment_date.desc()).first()
                
                if not latest_assessment:
                    continue
                
                # Prepare patient data
                patient_data = prepare_patient_data_for_crisis_detection(patient, latest_assessment)
                
                # Get risk assessment
                risk_assessment = crisis_detector.predict_crisis_risk(patient_data)
                
                # Create crisis alert if high risk
                if risk_assessment['risk_level'] in ['CRITICAL', 'HIGH']:
                    crisis_alert = CrisisAlert(
                        patient_id=patient_id,
                        assessment_id=latest_assessment.id,
                        alert_type='ml_crisis_detection_batch',
                        alert_message=f"Batch ML Crisis Detection: {risk_assessment['risk_level']} risk (probability: {risk_assessment['crisis_risk']:.3f})",
                        severity_level='critical' if risk_assessment['risk_level'] == 'CRITICAL' else 'urgent'
                    )
                    db.session.add(crisis_alert)
                    alerts_created += 1
                
                results.append({
                    'patient_id': patient_id,
                    'patient_name': f"{patient.first_name} {patient.last_name}",
                    'risk_assessment': risk_assessment
                })
                
            except Exception as e:
                print(f"❌ Error processing patient {patient_id}: {str(e)}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'results': results,
            'alerts_created': alerts_created,
            'total_patients': len(results)
        })
        
    except Exception as e:
        print(f"❌ Error in batch crisis assessment: {str(e)}")
        return jsonify({'error': 'Failed to perform batch crisis assessment'}), 500

# ============================================================================
# PREDICTION HELPER FUNCTIONS
# ============================================================================

def get_rule_based_prediction(patient):
    """Get rule-based prediction based on PHQ-9 severity level"""
    severity = patient.current_phq9_severity
    
    if severity in ['moderately_severe', 'severe']:
        return {
            'risk_level': 'HIGH',
            'risk_score': 0.8,
            'description': 'High Risk - Severe depression symptoms'
        }
    elif severity == 'moderate':
        return {
            'risk_level': 'MEDIUM',
            'risk_score': 0.5,
            'description': 'Medium Risk - Moderate depression symptoms'
        }
    elif severity == 'mild':
        return {
            'risk_level': 'LOW',
            'risk_score': 0.3,
            'description': 'Low Risk - Mild depression symptoms'
        }
    else:  # minimal
        return {
            'risk_level': 'MINIMAL',
            'risk_score': 0.1,
            'description': 'Minimal Risk - No significant depression symptoms'
        }

def calculate_combined_prediction(rule_based_prediction, ml_risk_assessment):
    """Calculate combined prediction with 70% ML weight and 30% rule-based weight"""
    try:
        # Convert rule-based risk level to numeric score
        rule_score = rule_based_prediction['risk_score']
        
        # Get ML risk probability
        ml_score = ml_risk_assessment['crisis_risk']
        
        # Calculate weighted average (70% ML, 30% rule-based)
        combined_score = (0.7 * ml_score) + (0.3 * rule_score)
        
        # Determine combined risk level
        if combined_score >= 0.8:
            risk_level = 'CRITICAL'
        elif combined_score >= 0.6:
            risk_level = 'HIGH'
        elif combined_score >= 0.4:
            risk_level = 'MEDIUM'
        elif combined_score >= 0.2:
            risk_level = 'LOW'
        else:
            risk_level = 'MINIMAL'
        
        # Determine confidence based on agreement between models
        score_difference = abs(ml_score - rule_score)
        if score_difference <= 0.1:
            confidence = 'HIGH'
        elif score_difference <= 0.3:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return {
            'risk_level': risk_level,
            'risk_score': combined_score,
            'confidence': confidence,
            'ml_weight': 0.7,
            'rule_weight': 0.3,
            'description': f'Combined Prediction: {risk_level} risk ({combined_score:.1%})'
        }
        
    except Exception as e:
        print(f"❌ Error calculating combined prediction: {str(e)}")
        return {
            'risk_level': 'ERROR',
            'risk_score': 0.0,
            'confidence': 'LOW',
            'description': f'Error calculating combined prediction: {str(e)}'
        }

# ============================================================================
# CRISIS DETECTION HELPER FUNCTIONS
# ============================================================================

def prepare_patient_data_for_crisis_detection(patient, assessment):
    """Prepare patient data for crisis detection model"""
    try:
        # Get additional patient data
        from datetime import datetime, timedelta
        
        # Calculate days since last session
        days_since_last_session = 0
        if assessment.assessment_date:
            days_since_last_session = (datetime.utcnow() - assessment.assessment_date).days
        
        # Get exercise completion rate (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        exercise_sessions = ExerciseSession.query.filter(
            ExerciseSession.patient_id == patient.id,
            ExerciseSession.start_time >= thirty_days_ago
        ).all()
        
        exercise_completion_rate = 1.0
        if exercise_sessions:
            completed_sessions = sum(1 for session in exercise_sessions if session.completion_time)
            exercise_completion_rate = completed_sessions / len(exercise_sessions)
        
        # Get mood data
        mood_entries = MoodEntry.query.filter(
            MoodEntry.patient_id == patient.id,
            MoodEntry.timestamp >= thirty_days_ago
        ).order_by(MoodEntry.timestamp.desc()).all()
        
        mood_intensity = 5  # Default neutral
        mood_trend = 0
        if mood_entries:
            recent_moods = [entry.intensity_level for entry in mood_entries[:5]]
            mood_intensity = sum(recent_moods) / len(recent_moods)
            if len(mood_entries) >= 2:
                mood_trend = mood_entries[0].intensity_level - mood_entries[-1].intensity_level
        
        # Get crisis history
        previous_crisis_count = CrisisAlert.query.filter(
            CrisisAlert.patient_id == patient.id,
            CrisisAlert.created_at >= thirty_days_ago
        ).count()
        
        # Calculate PHQ-9 trend (if multiple assessments exist)
        phq9_trend = 0
        previous_assessments = PHQ9Assessment.query.filter(
            PHQ9Assessment.patient_id == patient.id,
            PHQ9Assessment.assessment_date < assessment.assessment_date
        ).order_by(PHQ9Assessment.assessment_date.desc()).limit(1).all()
        
        if previous_assessments:
            phq9_trend = assessment.total_score - previous_assessments[0].total_score
        
        # Count crisis keywords in recent journal entries (if available)
        crisis_keywords = ['suicide', 'kill', 'end', 'hopeless', 'worthless', 'die', 'death']
        crisis_keyword_count = 0
        # This would need to be implemented if journal entries are stored
        
        # Prepare data in the format expected by the crisis detector
        patient_data = {
            'phq9_total_score': assessment.total_score,
            'q9_score': assessment.q9_score,
            'phq9_severity_level': assessment.severity_level,
            'phq9_trend': phq9_trend,
            'mood_intensity': mood_intensity,
            'mood_trend': mood_trend,
            'exercise_completion_rate': exercise_completion_rate,
            'days_since_last_session': days_since_last_session,
            'crisis_keyword_count': crisis_keyword_count,
            'previous_crisis_count': previous_crisis_count,
            'assessment_frequency': 7,  # Default weekly
            'treatment_duration': (datetime.utcnow() - patient.created_at).days,
            'age': patient.age or 30,
            'isolation_level': 0,  # Default
            'social_support': 1,  # Default
            'medication_adherence': 1.0,  # Default
            'therapy_attendance': 1.0,  # Default
            'provider_concern': 0,  # Default
            'clinical_observations': 0  # Default
        }
        
        return patient_data
        
    except Exception as e:
        print(f"❌ Error preparing patient data for crisis detection: {str(e)}")
        # Return minimal data if error occurs
        return {
            'phq9_total_score': assessment.total_score,
            'q9_score': assessment.q9_score,
            'phq9_severity_level': assessment.severity_level,
            'phq9_trend': 0,
            'mood_intensity': 5,
            'mood_trend': 0,
            'exercise_completion_rate': 1.0,
            'days_since_last_session': 0,
            'crisis_keyword_count': 0,
            'previous_crisis_count': 0,
            'assessment_frequency': 7,
            'treatment_duration': 0,
            'age': patient.age or 30,
            'isolation_level': 0,
            'social_support': 1,
            'medication_adherence': 1.0,
            'therapy_attendance': 1.0,
            'provider_concern': 0,
            'clinical_observations': 0
        }

def prepare_training_data_for_crisis_detection():
    """Prepare training data for crisis detection model from database"""
    try:
        training_data = []
        labels = []
        
        # Get all patients with assessments
        patients = Patient.query.all()
        
        for patient in patients:
            # Get all assessments for this patient
            assessments = PHQ9Assessment.query.filter_by(patient_id=patient.id)\
                .order_by(PHQ9Assessment.assessment_date.desc()).all()
            
            for assessment in assessments:
                # Prepare patient data for this assessment
                patient_data = prepare_patient_data_for_crisis_detection(patient, assessment)
                training_data.append(patient_data)
                
                # Create label based on Q9 score and total score
                # High risk: Q9 >= 2 or total score >= 20
                is_crisis = 1 if (assessment.q9_score >= 2 or assessment.total_score >= 20) else 0
                labels.append(is_crisis)
        
        return training_data, labels
        
    except Exception as e:
        print(f"❌ Error preparing training data: {str(e)}")
        return [], []

def generate_mock_briefing(patient_id, exercise_summary=None, mood_summary=None, feedback_summary=None, latest_assessment=None):
    """Generate a mock briefing when Claude API is not available"""
    try:
        # Get patient data
        patient = Patient.query.get_or_404(patient_id)
        
        if not latest_assessment:
            latest_assessment = PHQ9Assessment.query.filter_by(patient_id=patient_id)\
                .order_by(PHQ9Assessment.assessment_date.desc()).first()
        
        if not latest_assessment:
            return jsonify({'error': 'No PHQ-9 assessment found for this patient'}), 404
        
        # Generate mock briefing based on available data
        briefing_text = f"""
**PATIENT OVERVIEW**
Patient: {patient.first_name} {patient.last_name}
Age: {patient.age}
Current PHQ-9 Score: {latest_assessment.total_score}/27
Severity Level: {latest_assessment.severity_level.replace('_', ' ').title()}

**EXERCISE ENGAGEMENT ANALYSIS**
Based on recent activity data:
- Total exercise sessions: {len(exercise_summary) if exercise_summary else 0}
- Completion rate: {calculate_completion_rate(exercise_summary) if exercise_summary else 'N/A'}
- Average engagement score: {calculate_avg_engagement(exercise_summary) if exercise_summary else 'N/A'}

**MOOD TRAJECTORY INSIGHTS**
Recent mood tracking data:
- Mood entries recorded: {len(mood_summary) if mood_summary else 0}
- Average mood intensity: {calculate_avg_mood_intensity(mood_summary) if mood_summary else 'N/A'}
- Sleep quality trends: {analyze_sleep_quality(mood_summary) if mood_summary else 'N/A'}

**CLINICAL OBSERVATIONS**
- Patient shows {latest_assessment.severity_level.replace('_', ' ')} depression symptoms
- Recent exercise engagement appears {'positive' if len(exercise_summary) > 0 else 'limited'}
- {'Good' if latest_assessment.total_score < 10 else 'Moderate' if latest_assessment.total_score < 15 else 'High'} risk level based on PHQ-9 score

**SESSION FOCUS AREAS**
1. Review exercise completion and effectiveness
2. Discuss mood patterns and triggers
3. Address any barriers to exercise engagement
4. Plan next steps based on current progress

**EXERCISE RECOMMENDATIONS**
- Continue current exercise routine if engagement is positive
- Consider adjusting difficulty or type if engagement is low
- Focus on exercises that align with patient's preferences

**RISK ASSESSMENT**
- {'Low' if latest_assessment.total_score < 10 else 'Moderate' if latest_assessment.total_score < 15 else 'High'} risk based on PHQ-9 score
- {'No' if not latest_assessment.q9_risk_flag else 'Yes'} suicidal ideation risk detected

**PROGRESS INDICATORS**
- PHQ-9 score indicates {latest_assessment.severity_level.replace('_', ' ')} depression
- Exercise engagement: {'Active' if len(exercise_summary) > 0 else 'Limited'}
- Overall progress: {'Positive' if latest_assessment.total_score < 15 else 'Needs attention'}

**NOTE**: This is a mock briefing generated without AI analysis. For full AI-powered insights, please configure the Claude API key.
"""
        
        sections = parse_briefing_sections(briefing_text)
        
        return jsonify({
            'success': True,
            'patient_name': f"{patient.first_name} {patient.last_name}",
            'briefing_text': briefing_text,
            'sections': sections,
            'data_summary': {
                'exercise_sessions_count': len(exercise_summary) if exercise_summary else 0,
                'mood_entries_count': len(mood_summary) if mood_summary else 0,
                'feedback_count': len(feedback_summary) if feedback_summary else 0,
                'phq9_score': latest_assessment.total_score,
                'severity': latest_assessment.severity_level
            },
            'is_mock': True
        })
        
    except Exception as e:
        print(f"❌ Error generating mock briefing: {str(e)}")
        return jsonify({'error': 'Failed to generate briefing'}), 500

def calculate_completion_rate(exercise_summary):
    """Calculate completion rate from exercise summary"""
    if not exercise_summary:
        return "N/A"
    completed = sum(1 for session in exercise_summary if session.get('completion_status') == 'completed')
    return f"{(completed / len(exercise_summary) * 100):.1f}%" if exercise_summary else "N/A"

def calculate_avg_engagement(exercise_summary):
    """Calculate average engagement score"""
    if not exercise_summary:
        return "N/A"
    scores = [session.get('engagement_score') for session in exercise_summary if session.get('engagement_score')]
    return f"{sum(scores) / len(scores):.1f}" if scores else "N/A"

def calculate_avg_mood_intensity(mood_summary):
    """Calculate average mood intensity"""
    if not mood_summary:
        return "N/A"
    intensities = [mood.get('intensity_level') for mood in mood_summary if mood.get('intensity_level')]
    return f"{sum(intensities) / len(intensities):.1f}" if intensities else "N/A"

def analyze_sleep_quality(mood_summary):
    """Analyze sleep quality trends"""
    if not mood_summary:
        return "N/A"
    sleep_scores = [mood.get('sleep_quality') for mood in mood_summary if mood.get('sleep_quality')]
    if not sleep_scores:
        return "N/A"
    avg_sleep = sum(sleep_scores) / len(sleep_scores)
    if avg_sleep >= 7:
        return "Good"
    elif avg_sleep >= 5:
        return "Fair"
    else:
        return "Poor"

def parse_briefing_sections(briefing_text):
    """Parse AI briefing into structured sections"""
    sections = {}
    current_section = None
    current_content = []
    
    lines = briefing_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header (starts with ** or is all caps)
        if (line.startswith('**') and line.endswith('**')) or (line.isupper() and len(line) > 3):
            # Save previous section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            current_section = line.replace('**', '').strip()
            current_content = []
        else:
            if current_section:
                current_content.append(line)
            else:
                # Content before any section header
                if 'general' not in sections:
                    sections['general'] = []
                sections['general'].append(line)
    
    # Save last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

if __name__ == '__main__':
    print("🚀 Starting MindSpace PHQ-9 Analysis App...")
    print("📊 PHQ-9 focused assessment system with structured data")
    print("🔗 Access the app at: http://127.0.0.1:5000")
    print("👤 Login: patient1 / password123")
    print("👨‍⚕️ Provider: provider1 / password123")
    print("📋 Features: PHQ-9 assessments, crisis alerts, AI recommendations")
    app.run(debug=True, host='0.0.0.0') 