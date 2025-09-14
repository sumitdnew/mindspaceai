#!/usr/bin/env python3
"""
Smart Micro-Assessment System for Real-Time Mood and Context Tracking
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import numpy as np
import json
import logging
from sqlalchemy import func, and_, or_, desc
# These will be imported from app_ml_complete
db = None
Patient = None
CrisisAlert = None
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# These will be set by app_ml_complete.py
db = None
Patient = None
CrisisAlert = None
MicroAssessment = None
ContextData = None
NotificationSettings = None
PatternAnalysis = None
EngagementMetrics = None

# Create Blueprint
smart_assessment = Blueprint('smart_assessment', __name__)

class SmartNotificationEngine:
    """Intelligent notification timing and context awareness"""
    
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.settings = self._get_notification_settings()
        self.patterns = self._get_pattern_analysis()
    
    def _get_notification_settings(self):
        """Get patient's notification settings"""
        return NotificationSettings.query.filter_by(patient_id=self.patient_id).first()
    
    def _get_pattern_analysis(self):
        """Get recent pattern analysis"""
        return PatternAnalysis.query.filter_by(patient_id=self.patient_id).order_by(desc(PatternAnalysis.analysis_date)).first()
    
    def should_send_notification(self, current_time=None):
        """Determine if notification should be sent based on smart timing"""
        if current_time is None:
            current_time = datetime.now()
        
        # Check if patient has settings
        if not self.settings:
            return self._default_notification_logic(current_time)
        
        # Check minimum interval
        last_assessment = self._get_last_assessment()
        if last_assessment:
            time_since_last = current_time - last_assessment.timestamp
            if time_since_last.total_seconds() < self.settings.min_interval_hours * 3600:
                return False
        
        # Check preferred times
        if self.settings.preferred_times:
            current_hour = current_time.hour
            if current_hour not in self.settings.preferred_times:
                return False
        
        # Check avoid times
        if self.settings.avoid_times:
            current_hour = current_time.hour
            if current_hour in self.settings.avoid_times:
                return False
        
        return True
    
    def _default_notification_logic(self, current_time):
        """Default notification logic when no settings exist"""
        # Avoid late night/early morning
        if 22 <= current_time.hour or current_time.hour <= 7:
            return False
        
        # Check last assessment
        last_assessment = self._get_last_assessment()
        if last_assessment:
            time_since_last = current_time - last_assessment.timestamp
            if time_since_last.total_seconds() < 3600:  # 1 hour minimum
                return False
        
        return True
    
    def _get_last_assessment(self):
        """Get the most recent micro-assessment"""
        return MicroAssessment.query.filter_by(patient_id=self.patient_id).order_by(desc(MicroAssessment.timestamp)).first()
    
    def _is_high_risk_patient(self):
        """Check if patient is currently high risk"""
        # Check recent crisis alerts
        recent_crisis = CrisisAlert.query.filter_by(
            patient_id=self.patient_id,
            acknowledged=False
        ).filter(
            CrisisAlert.created_at >= datetime.now() - timedelta(days=7)
        ).first()
        
        return recent_crisis is not None

# Routes
@smart_assessment.route('/micro-assessment')
@login_required
def micro_assessment_dashboard():
    """Main micro-assessment dashboard"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found', 'error')
        return redirect(url_for('index'))
    
    # Get recent assessments
    recent_assessments = MicroAssessment.query.filter_by(
        patient_id=patient.id
    ).order_by(desc(MicroAssessment.timestamp)).limit(10).all()
    
    # Get engagement metrics
    engagement = EngagementMetrics.query.filter_by(patient_id=patient.id).first()
    
    return render_template('micro_assessment_dashboard.html',
                         patient=patient,
                         recent_assessments=recent_assessments,
                         engagement=engagement)

@smart_assessment.route('/micro-assessment/check-in', methods=['GET', 'POST'])
@login_required
def micro_assessment_checkin():
    """Quick micro-assessment check-in"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Process assessment submission
        start_time = session.get('assessment_start_time')
        response_time = None
        if start_time:
            response_time = int((datetime.now() - datetime.fromisoformat(start_time)).total_seconds())
        
        # Create context data
        context_data = ContextData(
            context_id=f"context_{patient.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            location_type=request.form.get('location_type'),
            activity_type=request.form.get('activity_type'),
            social_situation=request.form.get('social_situation'),
            environment_type=request.form.get('environment_type'),
            noise_level=request.form.get('noise_level'),
            physical_state=request.form.get('physical_state'),
            time_of_day=request.form.get('time_of_day'),
            day_of_week=datetime.now().strftime('%A').lower(),
            is_weekend=datetime.now().weekday() >= 5
        )
        
        db.session.add(context_data)
        db.session.flush()  # Get the ID
        
        # Create micro-assessment
        assessment = MicroAssessment(
            assessment_id=f"micro_{patient.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            patient_id=patient.id,
            mood_rating=int(request.form.get('mood_rating')),
            mood_emoji=request.form.get('mood_emoji'),
            energy_level=int(request.form.get('energy_level')),
            stress_level=int(request.form.get('stress_level')),
            context_data_id=context_data.id,
            coping_skill_used=request.form.get('coping_skill_used'),
            coping_effectiveness=int(request.form.get('coping_effectiveness')) if request.form.get('coping_effectiveness') else None,
            crisis_risk_level=request.form.get('crisis_risk_level', 'low'),
            needs_immediate_support=request.form.get('needs_immediate_support') == 'true',
            response_time_seconds=response_time,
            timestamp=datetime.now()
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        flash('Assessment completed successfully!', 'success')
        return redirect(url_for('smart_assessment.micro_assessment_dashboard'))
    
    # Clear any existing start time
    session.pop('assessment_start_time', None)
    session['assessment_start_time'] = datetime.now().isoformat()
    
    return render_template('micro_assessment_checkin.html',
                         patient=patient)

@smart_assessment.route('/micro-assessment/analytics')
@login_required
def micro_assessment_analytics():
    """Analytics and insights dashboard"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found', 'error')
        return redirect(url_for('index'))
    
    # Get pattern analysis
    patterns = PatternAnalysis.query.filter_by(
        patient_id=patient.id
    ).order_by(desc(PatternAnalysis.analysis_date)).limit(5).all()
    
    # Get recent assessments for trend analysis
    recent_assessments = MicroAssessment.query.filter_by(
        patient_id=patient.id
    ).order_by(MicroAssessment.timestamp).limit(50).all()
    
    # Prepare trend data
    trend_data = []
    for assessment in recent_assessments:
        trend_data.append({
            'timestamp': assessment.timestamp.isoformat(),
            'mood': assessment.mood_rating,
            'energy': assessment.energy_level,
            'stress': assessment.stress_level
        })
    
    return render_template('micro_assessment_analytics.html',
                         patient=patient,
                         patterns=patterns,
                         trend_data=json.dumps(trend_data))

@smart_assessment.route('/micro-assessment/patterns/analyze', methods=['POST'])
@login_required
def analyze_patterns():
    """Trigger pattern analysis"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    try:
        # Simple pattern analysis for now
        recent_assessments = MicroAssessment.query.filter_by(
            patient_id=patient.id
        ).order_by(desc(MicroAssessment.timestamp)).limit(20).all()
        
        if len(recent_assessments) >= 5:
            # Create basic pattern analysis
            pattern_analysis = PatternAnalysis(
                analysis_id=f"pattern_{patient.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                patient_id=patient.id,
                pattern_type='mood_fluctuation',
                pattern_description="Basic mood pattern analysis completed",
                confidence_level=0.6,
                data_points_analyzed=len(recent_assessments),
                time_period_days=7,
                analysis_date=datetime.now()
            )
            
            db.session.add(pattern_analysis)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Pattern analysis completed',
                'analysis_id': pattern_analysis.analysis_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Insufficient data for pattern analysis'
            })
    
    except Exception as e:
        logger.error(f"Pattern analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@smart_assessment.route('/micro-assessment/notification/check')
@login_required
def check_notification():
    """Check if notification should be sent"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    notification_engine = SmartNotificationEngine(patient.id)
    should_send = notification_engine.should_send_notification()
    
    if should_send:
        return jsonify({
            'should_send': True,
            'prompt': "How are you feeling right now?"
        })
    else:
        return jsonify({
            'should_send': False
        })

@smart_assessment.route('/micro-assessment/settings', methods=['GET', 'POST'])
@login_required
def notification_settings():
    """Manage notification settings"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found', 'error')
        return redirect(url_for('index'))
    
    settings = NotificationSettings.query.filter_by(patient_id=patient.id).first()
    
    if request.method == 'POST':
        if not settings:
            settings = NotificationSettings(patient_id=patient.id)
            db.session.add(settings)
        
        # Update settings
        settings.frequency_type = request.form.get('frequency_type', 'adaptive')
        settings.min_interval_hours = int(request.form.get('min_interval_hours', 1))
        settings.max_interval_hours = int(request.form.get('max_interval_hours', 8))
        settings.avoid_meetings = request.form.get('avoid_meetings') == 'true'
        settings.avoid_sleep_hours = request.form.get('avoid_sleep_hours') == 'true'
        settings.show_coping_suggestions = request.form.get('show_coping_suggestions') == 'true'
        settings.emergency_contact_visible = request.form.get('emergency_contact_visible') == 'true'
        
        # Parse preferred times
        preferred_times = request.form.get('preferred_times', '')
        if preferred_times:
            settings.preferred_times = [int(t) for t in preferred_times.split(',') if t.strip()]
        
        db.session.commit()
        flash('Notification settings updated successfully!', 'success')
        return redirect(url_for('smart_assessment.notification_settings'))
    
    return render_template('micro_assessment_settings.html',
                         patient=patient,
                         settings=settings)
