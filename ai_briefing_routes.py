#!/usr/bin/env python3
"""
AI Briefing Routes for Comprehensive Provider Dashboard
Provides API endpoints for AI-powered session briefings
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging

# Create the blueprint
ai_briefing = Blueprint('ai_briefing', __name__)

@ai_briefing.route('/api/session_briefing/<int:patient_id>')
@login_required
def get_session_briefing(patient_id):
    """Get AI-powered session briefing for a patient"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied. Provider role required.'}), 403
    
    try:
        # Import AI briefing system locally to avoid circular imports
        from ai_session_briefing_system import AISessionBriefingSystem
        
        # Initialize AI briefing system
        ai_system = AISessionBriefingSystem()
        
        # Generate briefing
        briefing = ai_system.generate_session_briefing(patient_id)
        
        if briefing.get('error'):
            return jsonify({
                'success': False,
                'error': briefing['error']
            }), 400
        
        return jsonify(briefing)
        
    except Exception as e:
        logging.error(f"Error generating session briefing: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate briefing: {str(e)}'
        }), 500

@ai_briefing.route('/api/session_briefing/<int:patient_id>/regenerate')
@login_required
def regenerate_session_briefing(patient_id):
    """Regenerate AI-powered session briefing for a patient"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied. Provider role required.'}), 403
    
    try:
        # Import AI briefing system locally to avoid circular imports
        from ai_session_briefing_system import AISessionBriefingSystem
        
        # Initialize AI briefing system
        ai_system = AISessionBriefingSystem()
        
        # Generate new briefing
        briefing = ai_system.generate_session_briefing(patient_id)
        
        if briefing.get('error'):
            return jsonify({
                'success': False,
                'error': briefing['error']
            }), 400
        
        return jsonify(briefing)
        
    except Exception as e:
        logging.error(f"Error regenerating session briefing: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to regenerate briefing: {str(e)}'
        }), 500

@ai_briefing.route('/api/session_briefing/<int:patient_id>/sections')
@login_required
def get_briefing_sections(patient_id):
    """Get specific sections of AI briefing"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied. Provider role required.'}), 403
    
    try:
        # Import AI briefing system locally to avoid circular imports
        from ai_session_briefing_system import AISessionBriefingSystem
        
        # Initialize AI briefing system
        ai_system = AISessionBriefingSystem()
        
        # Generate briefing
        briefing = ai_system.generate_session_briefing(patient_id)
        
        if briefing.get('error'):
            return jsonify({
                'success': False,
                'error': briefing['error']
            }), 400
        
        # Return only sections
        return jsonify({
            'success': True,
            'sections': briefing.get('sections', {}),
            'key_insights': briefing.get('key_insights', []),
            'recommendations': briefing.get('recommendations', [])
        })
        
    except Exception as e:
        logging.error(f"Error getting briefing sections: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get briefing sections: {str(e)}'
        }), 500

@ai_briefing.route('/api/session_briefing/<int:patient_id>/summary')
@login_required
def get_briefing_summary(patient_id):
    """Get executive summary of AI briefing"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied. Provider role required.'}), 403
    
    try:
        # Import AI briefing system locally to avoid circular imports
        from ai_session_briefing_system import AISessionBriefingSystem
        
        # Initialize AI briefing system
        ai_system = AISessionBriefingSystem()
        
        # Generate briefing
        briefing = ai_system.generate_session_briefing(patient_id)
        
        if briefing.get('error'):
            return jsonify({
                'success': False,
                'error': briefing['error']
            }), 400
        
        # Return only executive summary
        sections = briefing.get('sections', {})
        summary = sections.get('Executive Summary', 'No summary available')
        
        return jsonify({
            'success': True,
            'summary': summary,
            'patient_name': briefing.get('patient_name', 'Unknown'),
            'data_summary': briefing.get('data_summary', {}),
            'generated_at': briefing.get('generated_at')
        })
        
    except Exception as e:
        logging.error(f"Error getting briefing summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get briefing summary: {str(e)}'
        }), 500