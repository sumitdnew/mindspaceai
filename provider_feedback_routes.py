#!/usr/bin/env python3
"""
Provider Feedback Routes
Flask routes for provider exercise feedback system
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import logging

from provider_exercise_feedback_system import provider_exercise_feedback

# Create blueprint
provider_feedback_bp = Blueprint('provider_feedback', __name__)

logger = logging.getLogger(__name__)

def get_models():
    """Get database models (to avoid circular imports)"""
    import app_ml_complete
    return {
        'db': app_ml_complete.db,
        'Patient': app_ml_complete.Patient,
        'User': app_ml_complete.User,
        'PHQ9Assessment': app_ml_complete.PHQ9Assessment,
        'ProviderExerciseFeedback': app_ml_complete.ProviderExerciseFeedback,
        'Exercise': getattr(app_ml_complete, 'Exercise', None)
    }

@provider_feedback_bp.route('/exercise_feedback')
@login_required
def exercise_feedback_dashboard():
    """Provider exercise feedback dashboard"""
    if current_user.role != 'provider':
        flash('Access denied. Provider role required.', 'error')
        return redirect(url_for('index'))
    
    return render_template('provider_exercise_feedback.html')

@provider_feedback_bp.route('/api/provider_exercise_dashboard')
@login_required
def api_provider_dashboard():
    """API endpoint for provider dashboard data"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        dashboard_data = provider_exercise_feedback.get_provider_dashboard(current_user.id)
        return jsonify(dashboard_data)
    except Exception as e:
        logger.error(f"Error getting provider dashboard: {str(e)}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500

@provider_feedback_bp.route('/api/patients')
@login_required
def api_get_patients():
    """API endpoint to get all patients"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        models = get_models()
        Patient = models['Patient']
        PHQ9Assessment = models['PHQ9Assessment']
        
        patients = Patient.query.all()
        patient_data = []
        
        for patient in patients:
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
        
        return jsonify({'patients': patient_data})
    except Exception as e:
        logger.error(f"Error getting patients: {str(e)}")
        return jsonify({'error': 'Failed to get patients'}), 500

@provider_feedback_bp.route('/api/patient_exercise_recommendations/<int:patient_id>')
@login_required
def api_patient_recommendations(patient_id):
    """API endpoint to get patient exercise recommendations"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        recommendations = provider_exercise_feedback.get_patient_exercise_recommendations(
            patient_id, current_user.id
        )
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting patient recommendations: {str(e)}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@provider_feedback_bp.route('/api/submit_provider_feedback/<int:patient_id>', methods=['POST'])
@login_required
def api_submit_feedback(patient_id):
    """API endpoint to submit provider feedback"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        feedback_data = request.get_json()
        
        if not feedback_data:
            return jsonify({'error': 'No feedback data provided'}), 400
        
        result = provider_exercise_feedback.submit_provider_feedback(
            patient_id, current_user.id, feedback_data
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@provider_feedback_bp.route('/api/available_exercises')
@login_required
def api_available_exercises():
    """API endpoint to get available exercises"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from app_ml_complete import Exercise
        
        exercises = Exercise.query.all()
        exercise_data = []
        
        for exercise in exercises:
            exercise_data.append({
                'id': exercise.id,
                'type': exercise.type,
                'name': exercise.name,
                'difficulty_level': exercise.difficulty_level,
                'estimated_duration': exercise.estimated_duration,
                'clinical_focus_areas': exercise.clinical_focus_areas,
                'description': exercise.description
            })
        
        return jsonify({'exercises': exercise_data})
    except Exception as e:
        logger.error(f"Error getting available exercises: {str(e)}")
        return jsonify({'error': 'Failed to get exercises'}), 500

@provider_feedback_bp.route('/api/export_rl_training_data')
@login_required
def api_export_training_data():
    """API endpoint to export RL training data"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        training_data = provider_exercise_feedback.get_rl_training_data(current_user.id)
        
        # Create CSV export
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'patient_id', 'provider_id', 'timestamp', 'exercise_type', 'action',
            'feedback_category', 'clinical_rationale', 'reward_signal',
            'severity_level', 'phq9_score', 'q9_risk', 'mood_trend', 'engagement_score'
        ])
        
        # Write data
        for sample in training_data.get('training_data', []):
            patient_context = sample.get('patient_context', {})
            assessment_data = patient_context.get('assessment_data', {})
            
            writer.writerow([
                sample.get('patient_id'),
                sample.get('provider_id'),
                sample.get('timestamp'),
                sample.get('recommended_exercise'),
                sample.get('provider_action'),
                sample.get('feedback_category'),
                sample.get('clinical_rationale'),
                sample.get('reward_signal'),
                assessment_data.get('severity_level'),
                assessment_data.get('total_score'),
                assessment_data.get('q9_risk'),
                ','.join(map(str, patient_context.get('mood_trend', []))),
                ','.join(map(str, [ex.get('engagement_score', 0) for ex in patient_context.get('exercise_history', [])]))
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=rl_training_data.csv'}
        )
    except Exception as e:
        logger.error(f"Error exporting training data: {str(e)}")
        return jsonify({'error': 'Failed to export training data'}), 500

@provider_feedback_bp.route('/api/rl_training_data')
@login_required
def api_rl_training_data():
    """API endpoint to get RL training data"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        limit = request.args.get('limit', 1000, type=int)
        training_data = provider_exercise_feedback.get_rl_training_data(current_user.id, limit)
        return jsonify(training_data)
    except Exception as e:
        logger.error(f"Error getting RL training data: {str(e)}")
        return jsonify({'error': 'Failed to get training data'}), 500

@provider_feedback_bp.route('/api/feedback_analytics')
@login_required
def api_feedback_analytics():
    """API endpoint to get feedback analytics"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        dashboard_data = provider_exercise_feedback.get_provider_dashboard(current_user.id)
        return jsonify(dashboard_data.get('feedback_analytics', {}))
    except Exception as e:
        logger.error(f"Error getting feedback analytics: {str(e)}")
        return jsonify({'error': 'Failed to get analytics'}), 500

@provider_feedback_bp.route('/api/patient_feedback_history/<int:patient_id>')
@login_required
def api_patient_feedback_history(patient_id):
    """API endpoint to get patient feedback history"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from provider_exercise_feedback_system import ProviderExerciseFeedback
        
        feedback_history = ProviderExerciseFeedback.query.filter_by(
            patient_id=patient_id, provider_id=current_user.id
        ).order_by(ProviderExerciseFeedback.submitted_at.desc()).all()
        
        history_data = []
        for feedback in feedback_history:
            history_data.append({
                'id': feedback.id,
                'exercise_type': feedback.exercise_type,
                'action': feedback.action,
                'feedback_category': feedback.feedback_category,
                'clinical_rationale': feedback.clinical_rationale,
                'submitted_at': feedback.submitted_at.isoformat(),
                'modified_recommendations': json.loads(feedback.modified_recommendations) if feedback.modified_recommendations else {}
            })
        
        return jsonify({'feedback_history': history_data})
    except Exception as e:
        logger.error(f"Error getting patient feedback history: {str(e)}")
        return jsonify({'error': 'Failed to get feedback history'}), 500

@provider_feedback_bp.route('/api/bulk_feedback', methods=['POST'])
@login_required
def api_bulk_feedback():
    """API endpoint for bulk feedback operations"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        action = data.get('action')  # approve_all, reject_all, modify_all
        feedback_data = data.get('feedback_data', {})
        
        if not patient_id or not action:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Get current recommendations
        recommendations = provider_exercise_feedback.get_patient_exercise_recommendations(
            patient_id, current_user.id
        )
        
        if 'error' in recommendations:
            return jsonify({'error': recommendations['error']}), 500
        
        # Process bulk action
        results = []
        severity_recs = recommendations.get('recommendations', {}).get('severity_based_recommendations', {})
        
        # Process daily exercises
        for exercise in severity_recs.get('daily', []):
            result = provider_exercise_feedback.submit_provider_feedback(
                patient_id, current_user.id, {
                    'exercise_type': exercise,
                    'action': action,
                    'category': feedback_data.get('category', 'clinical_appropriateness'),
                    'clinical_rationale': feedback_data.get('rationale', f'Bulk {action} action'),
                    'recommendation_id': recommendations.get('recommendations', {}).get('recommendation_id')
                }
            )
            results.append(result)
        
        # Process weekly exercises
        for exercise in severity_recs.get('weekly', []):
            result = provider_exercise_feedback.submit_provider_feedback(
                patient_id, current_user.id, {
                    'exercise_type': exercise,
                    'action': action,
                    'category': feedback_data.get('category', 'clinical_appropriateness'),
                    'clinical_rationale': feedback_data.get('rationale', f'Bulk {action} action'),
                    'recommendation_id': recommendations.get('recommendations', {}).get('recommendation_id')
                }
            )
            results.append(result)
        
        return jsonify({
            'success': True,
            'processed_count': len(results),
            'results': results
        })
    except Exception as e:
        logger.error(f"Error processing bulk feedback: {str(e)}")
        return jsonify({'error': 'Failed to process bulk feedback'}), 500

@provider_feedback_bp.route('/api/rl_model_status')
@login_required
def api_rl_model_status():
    """API endpoint to get RL model training status"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # This would integrate with your RL model training system
        # For now, return mock data
        model_status = {
            'training_status': 'idle',  # idle, training, completed, error
            'last_training': None,
            'next_training': None,
            'model_accuracy': 0.0,
            'training_samples': 0,
            'validation_accuracy': 0.0,
            'training_loss': 0.0,
            'validation_loss': 0.0,
            'feature_importance': {},
            'recommendation_accuracy': 0.0
        }
        
        return jsonify(model_status)
    except Exception as e:
        logger.error(f"Error getting RL model status: {str(e)}")
        return jsonify({'error': 'Failed to get model status'}), 500

@provider_feedback_bp.route('/api/start_rl_training', methods=['POST'])
@login_required
def api_start_rl_training():
    """API endpoint to start RL model training"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # This would start the RL model training process
        # Implementation depends on your RL training system
        
        return jsonify({
            'success': True,
            'message': 'RL model training started',
            'training_id': f'training_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        })
    except Exception as e:
        logger.error(f"Error starting RL training: {str(e)}")
        return jsonify({'error': 'Failed to start training'}), 500

@provider_feedback_bp.route('/api/rl_predictions/<int:patient_id>')
@login_required
def api_rl_predictions(patient_id):
    """API endpoint to get RL model predictions for a patient"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # This would get predictions from your trained RL model
        # For now, return mock data
        predictions = {
            'patient_id': patient_id,
            'model_predictions': [],
            'confidence_scores': {},
            'recommended_exercises': [],
            'prediction_timestamp': datetime.now().isoformat(),
            'model_version': '1.0.0'
        }
        
        return jsonify(predictions)
    except Exception as e:
        logger.error(f"Error getting RL predictions: {str(e)}")
        return jsonify({'error': 'Failed to get predictions'}), 500
