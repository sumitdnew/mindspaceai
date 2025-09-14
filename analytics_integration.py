#!/usr/bin/env python3
"""
Analytics Integration System
Unified interface for all exercise analytics components
"""

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import numpy as np

# Import analytics modules
from exercise_analytics import ExerciseAnalytics
from clinical_progress_analytics import ClinicalProgressAnalytics
from personalization_algorithms import PersonalizationEngine
from risk_detection_system import RiskDetectionSystem
from provider_analytics_dashboard import ProviderAnalyticsDashboard
from continuous_improvement_system import ContinuousImprovementSystem

analytics_integration = Blueprint('analytics_integration', __name__)

class AnalyticsIntegrationSystem:
    """Unified analytics integration system"""
    
    def __init__(self):
        self.analysis_period = 30  # days
    
    def get_comprehensive_analytics(self, patient_id=None):
        """Get comprehensive analytics for all systems"""
        if patient_id:
            return self._get_patient_analytics(patient_id)
        else:
            return self._get_system_analytics()
    
    def _get_patient_analytics(self, patient_id):
        """Get comprehensive analytics for a specific patient"""
        analytics = {
            'engagement_analytics': self._get_engagement_analytics(patient_id),
            'clinical_progress': self._get_clinical_progress(patient_id),
            'personalization': self._get_personalization(patient_id),
            'risk_analysis': self._get_risk_analysis(patient_id),
            'recommendations': self._get_patient_recommendations(patient_id)
        }
        
        return analytics
    
    def _get_system_analytics(self):
        """Get system-wide analytics for providers"""
        analytics = {
            'provider_dashboard': self._get_provider_dashboard(),
            'continuous_improvement': self._get_continuous_improvement(),
            'system_insights': self._get_system_insights()
        }
        
        return analytics
    
    def _get_engagement_analytics(self, patient_id):
        """Get engagement analytics for a patient"""
        try:
            analytics = ExerciseAnalytics(patient_id)
            return analytics.get_engagement_analytics()
        except Exception as e:
            return {'error': f'Failed to get engagement analytics: {str(e)}'}
    
    def _get_clinical_progress(self, patient_id):
        """Get clinical progress analytics for a patient"""
        try:
            analytics = ClinicalProgressAnalytics(patient_id)
            return analytics.get_clinical_progress_analytics()
        except Exception as e:
            return {'error': f'Failed to get clinical progress analytics: {str(e)}'}
    
    def _get_personalization(self, patient_id):
        """Get personalization recommendations for a patient"""
        try:
            engine = PersonalizationEngine(patient_id)
            return engine.get_personalized_recommendations()
        except Exception as e:
            return {'error': f'Failed to get personalization data: {str(e)}'}
    
    def _get_risk_analysis(self, patient_id):
        """Get risk analysis for a patient"""
        try:
            risk_system = RiskDetectionSystem(patient_id)
            return risk_system.get_risk_analysis()
        except Exception as e:
            return {'error': f'Failed to get risk analysis: {str(e)}'}
    
    def _get_patient_recommendations(self, patient_id):
        """Generate comprehensive recommendations for a patient"""
        try:
            # Get all analytics data
            engagement = self._get_engagement_analytics(patient_id)
            clinical = self._get_clinical_progress(patient_id)
            personalization = self._get_personalization(patient_id)
            risk = self._get_risk_analysis(patient_id)
            
            # Generate comprehensive recommendations
            recommendations = {
                'immediate_actions': self._generate_immediate_actions(engagement, clinical, risk),
                'long_term_strategies': self._generate_long_term_strategies(engagement, clinical, personalization),
                'risk_mitigation': self._generate_risk_mitigation(risk),
                'optimization_opportunities': self._generate_optimization_opportunities(personalization)
            }
            
            return recommendations
        except Exception as e:
            return {'error': f'Failed to generate recommendations: {str(e)}'}
    
    def _generate_immediate_actions(self, engagement, clinical, risk):
        """Generate immediate action items"""
        actions = []
        
        # Check for high-risk situations
        if risk.get('overall_risk_level') == 'critical':
            actions.append({
                'priority': 'critical',
                'action': 'Immediate clinical intervention required',
                'reason': 'Critical risk level detected',
                'urgency': 'immediate'
            })
        
        # Check for engagement drops
        engagement_drops = engagement.get('drop_off_analysis', {})
        if engagement_drops.get('drop_off_rate', 0) > 0.5:
            actions.append({
                'priority': 'high',
                'action': 'Address engagement barriers',
                'reason': f"High drop-off rate: {engagement_drops.get('drop_off_rate', 0):.1%}",
                'urgency': 'within_24_hours'
            })
        
        # Check for mood instability
        mood_stability = clinical.get('mood_stability', {})
        if mood_stability.get('mood_variability', 0) > 3:
            actions.append({
                'priority': 'high',
                'action': 'Stabilize mood patterns',
                'reason': f"High mood variability: {mood_stability.get('mood_variability', 0):.1f}",
                'urgency': 'within_24_hours'
            })
        
        return actions
    
    def _generate_long_term_strategies(self, engagement, clinical, personalization):
        """Generate long-term strategies"""
        strategies = []
        
        # Skill development strategy
        skill_acquisition = clinical.get('skill_acquisition', {})
        if skill_acquisition.get('skill_progression') == 'beginner':
            strategies.append({
                'focus_area': 'skill_development',
                'strategy': 'Progressive skill building program',
                'timeline': '3-6 months',
                'expected_outcome': 'Intermediate skill level'
            })
        
        # Engagement optimization
        timing_patterns = engagement.get('timing_patterns', {})
        if timing_patterns.get('optimal_times'):
            strategies.append({
                'focus_area': 'timing_optimization',
                'strategy': f"Schedule sessions during optimal times: {', '.join(map(str, timing_patterns.get('optimal_times', [])))}",
                'timeline': 'ongoing',
                'expected_outcome': 'Improved session effectiveness'
            })
        
        # Personalization strategy
        exercise_recommendations = personalization.get('exercise_type_recommendations', {})
        if exercise_recommendations.get('top_recommendation'):
            strategies.append({
                'focus_area': 'exercise_selection',
                'strategy': f"Focus on {exercise_recommendations.get('top_recommendation')} exercises",
                'timeline': 'ongoing',
                'expected_outcome': 'Higher effectiveness and engagement'
            })
        
        return strategies
    
    def _generate_risk_mitigation(self, risk):
        """Generate risk mitigation strategies"""
        mitigation = []
        
        risk_alerts = risk.get('risk_alerts', [])
        for alert in risk_alerts:
            if alert.get('type') == 'engagement_drop':
                mitigation.append({
                    'risk_type': 'engagement_drop',
                    'strategy': 'Implement engagement boosters',
                    'actions': [
                        'Send motivational messages',
                        'Reduce session difficulty temporarily',
                        'Provide additional support resources'
                    ]
                })
            elif alert.get('type') == 'negative_ratings':
                mitigation.append({
                    'risk_type': 'negative_ratings',
                    'strategy': 'Improve exercise effectiveness',
                    'actions': [
                        'Review exercise instructions',
                        'Provide additional guidance',
                        'Consider alternative exercises'
                    ]
                })
        
        return mitigation
    
    def _generate_optimization_opportunities(self, personalization):
        """Generate optimization opportunities"""
        opportunities = []
        
        # Timing optimization
        optimal_timing = personalization.get('optimal_timing', {})
        if optimal_timing.get('optimal_hours'):
            opportunities.append({
                'type': 'timing_optimization',
                'description': f"Schedule sessions during hours: {', '.join(map(str, optimal_timing.get('optimal_hours', [])))}",
                'potential_improvement': '20-30% effectiveness increase'
            })
        
        # Difficulty adaptation
        difficulty_adaptation = personalization.get('difficulty_adaptation', {})
        if difficulty_adaptation.get('recommended_difficulty') != difficulty_adaptation.get('current_difficulty_level'):
            opportunities.append({
                'type': 'difficulty_optimization',
                'description': f"Adjust difficulty from {difficulty_adaptation.get('current_difficulty_level')} to {difficulty_adaptation.get('recommended_difficulty')}",
                'potential_improvement': '15-25% engagement increase'
            })
        
        return opportunities
    
    def _get_provider_dashboard(self):
        """Get provider dashboard data"""
        try:
            dashboard = ProviderAnalyticsDashboard()
            return dashboard.get_provider_dashboard_data()
        except Exception as e:
            return {'error': f'Failed to get provider dashboard: {str(e)}'}
    
    def _get_continuous_improvement(self):
        """Get continuous improvement data"""
        try:
            improvement = ContinuousImprovementSystem()
            return improvement.get_continuous_improvement_data()
        except Exception as e:
            return {'error': f'Failed to get continuous improvement data: {str(e)}'}
    
    def _get_system_insights(self):
        """Generate system-wide insights"""
        insights = {
            'system_health': self._assess_system_health(),
            'trends': self._identify_system_trends(),
            'optimization_opportunities': self._identify_optimization_opportunities()
        }
        
        return insights
    
    def _assess_system_health(self):
        """Assess overall system health"""
        # This would analyze system-wide metrics
        health_metrics = {
            'overall_engagement': 0.75,  # Would be calculated from actual data
            'average_effectiveness': 7.2,  # Would be calculated from actual data
            'risk_level': 'low',  # Would be calculated from actual data
            'system_stability': 'excellent'
        }
        
        return health_metrics
    
    def _identify_system_trends(self):
        """Identify system-wide trends"""
        trends = [
            'Increasing adoption of mindfulness exercises',
            'Improving session completion rates',
            'Growing preference for guided meditation',
            'Positive correlation between timing and effectiveness'
        ]
        
        return trends
    
    def _identify_optimization_opportunities(self):
        """Identify system-wide optimization opportunities"""
        opportunities = [
            'Implement A/B testing for exercise variations',
            'Develop personalized timing recommendations',
            'Enhance risk detection algorithms',
            'Improve provider dashboard analytics'
        ]
        
        return opportunities

# API Routes for Analytics Integration
@analytics_integration.route('/api/analytics/comprehensive/<int:patient_id>')
@login_required
def get_comprehensive_patient_analytics(patient_id):
    """Get comprehensive analytics for a specific patient"""
    # Verify user has access to this patient
    from app_ml_complete import Patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id and current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    integration = AnalyticsIntegrationSystem()
    return jsonify(integration.get_comprehensive_analytics(patient_id))

@analytics_integration.route('/api/analytics/system')
@login_required
def get_system_analytics():
    """Get system-wide analytics (provider only)"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    integration = AnalyticsIntegrationSystem()
    return jsonify(integration.get_comprehensive_analytics())

@analytics_integration.route('/analytics/dashboard')
@login_required
def analytics_dashboard():
    """Main analytics dashboard page"""
    if current_user.role == 'provider':
        # Provider sees system-wide analytics
        integration = AnalyticsIntegrationSystem()
        analytics_data = integration.get_comprehensive_analytics()
        return render_template('provider_analytics_dashboard.html', data=analytics_data)
    else:
        # Patient sees their own analytics
        from app_ml_complete import Patient
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        integration = AnalyticsIntegrationSystem()
        analytics_data = integration.get_comprehensive_analytics(patient.id)
        return render_template('patient_analytics_dashboard.html', data=analytics_data)

# Individual Analytics Endpoints
@analytics_integration.route('/api/analytics/engagement/<int:patient_id>')
@login_required
def get_engagement_analytics(patient_id):
    """Get engagement analytics for a patient"""
    from app_ml_complete import Patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id and current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    analytics = ExerciseAnalytics(patient_id)
    return jsonify(analytics.get_engagement_analytics())

@analytics_integration.route('/api/analytics/clinical-progress/<int:patient_id>')
@login_required
def get_clinical_progress_analytics(patient_id):
    """Get clinical progress analytics for a patient"""
    from app_ml_complete import Patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id and current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    analytics = ClinicalProgressAnalytics(patient_id)
    return jsonify(analytics.get_clinical_progress_analytics())

@analytics_integration.route('/api/analytics/personalization/<int:patient_id>')
@login_required
def get_personalization_recommendations(patient_id):
    """Get personalization recommendations for a patient"""
    from app_ml_complete import Patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id and current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    engine = PersonalizationEngine(patient_id)
    return jsonify(engine.get_personalized_recommendations())

@analytics_integration.route('/api/analytics/risk-analysis/<int:patient_id>')
@login_required
def get_risk_analysis(patient_id):
    """Get risk analysis for a patient"""
    from app_ml_complete import Patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id and current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    risk_system = RiskDetectionSystem(patient_id)
    return jsonify(risk_system.get_risk_analysis())

@analytics_integration.route('/api/analytics/continuous-improvement')
@login_required
def get_continuous_improvement_data():
    """Get continuous improvement data (provider only)"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    improvement = ContinuousImprovementSystem()
    return jsonify(improvement.get_continuous_improvement_data())

# Analytics Summary Endpoint
@analytics_integration.route('/api/analytics/summary/<int:patient_id>')
@login_required
def get_analytics_summary(patient_id):
    """Get a summary of key analytics for a patient"""
    from app_ml_complete import Patient
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id and current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    integration = AnalyticsIntegrationSystem()
    analytics = integration.get_comprehensive_analytics(patient_id)
    
    # Create a summary
    summary = {
        'patient_name': f"{patient.first_name} {patient.last_name}",
        'engagement_score': analytics.get('engagement_analytics', {}).get('completion_rates', {}).get('overall_rate', 0),
        'risk_level': analytics.get('risk_analysis', {}).get('overall_risk_level', 'unknown'),
        'skill_level': analytics.get('clinical_progress', {}).get('skill_acquisition', {}).get('skill_progression', 'unknown'),
        'mood_stability': analytics.get('clinical_progress', {}).get('mood_stability', {}).get('mood_trend', 'unknown'),
        'top_recommendation': analytics.get('personalization', {}).get('exercise_type_recommendations', {}).get('top_recommendation', 'none'),
        'immediate_actions': len(analytics.get('recommendations', {}).get('immediate_actions', [])),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return jsonify(summary)

if __name__ == '__main__':
    print("Analytics Integration System Loaded")
