#!/usr/bin/env python3
"""
Comprehensive Analytics Dashboard
Unified interface for PHQ-9 exercise analytics, outcome measurement, and provider decision support
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
from flask import Flask, render_template, jsonify, request
from flask_login import login_required, current_user

from phq9_exercise_analytics import PHQ9ExerciseAnalytics
from outcome_measurement import OutcomeMeasurement
from provider_decision_support import ProviderDecisionSupport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    """Comprehensive analytics dashboard for PHQ-9 exercise integration"""
    
    def __init__(self):
        self.analytics = PHQ9ExerciseAnalytics()
        self.outcome_measurement = OutcomeMeasurement()
        self.decision_support = ProviderDecisionSupport()
        
    def generate_comprehensive_dashboard(self, patient_id: int, time_period_days: int = 90) -> Dict:
        """Generate comprehensive dashboard with all analytics"""
        try:
            # Get comprehensive analytics
            analytics_data = self.analytics.generate_comprehensive_analytics(patient_id, time_period_days)
            
            # Get outcome measurements
            outcome_data = self._get_outcome_measurements(patient_id, analytics_data)
            
            # Get decision support
            decision_data = self._get_decision_support(patient_id, analytics_data)
            
            # Generate dashboard summary
            dashboard_summary = self._generate_dashboard_summary(analytics_data, outcome_data, decision_data)
            
            return {
                'dashboard_summary': dashboard_summary,
                'correlation_analysis': analytics_data.get('correlation_analysis', {}),
                'outcome_measurement': outcome_data,
                'decision_support': decision_data,
                'patient_id': patient_id,
                'analysis_period': analytics_data.get('analysis_period', {}),
                'summary_insights': analytics_data.get('summary_insights', {}),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive dashboard: {str(e)}")
            return {'error': f'Dashboard generation failed: {str(e)}'}

    def generate_provider_report(self, patient_id: int, report_type: str = 'comprehensive') -> Dict:
        """Generate provider-specific reports"""
        try:
            if report_type == 'comprehensive':
                return self.generate_comprehensive_dashboard(patient_id)
            elif report_type == 'correlation':
                return self._generate_correlation_report(patient_id)
            elif report_type == 'outcomes':
                return self._generate_outcomes_report(patient_id)
            elif report_type == 'decisions':
                return self._generate_decisions_report(patient_id)
            else:
                return {'error': f'Unknown report type: {report_type}'}
                
        except Exception as e:
            logger.error(f"Error generating provider report: {str(e)}")
            return {'error': f'Provider report generation failed: {str(e)}'}

    def generate_population_analytics(self, filters: Dict = None) -> Dict:
        """Generate population-level analytics"""
        try:
            # Get all patients
            from app_ml_complete import Patient, PHQ9Assessment, ExerciseSession
            
            patients = Patient.query.all()
            
            population_metrics = {
                'total_patients': len(patients),
                'active_patients': 0,
                'average_effectiveness': 0,
                'success_rate': 0,
                'improvement_distribution': {},
                'exercise_effectiveness_by_type': {},
                'crisis_intervention_success': {}
            }
            
            effectiveness_scores = []
            improvement_scores = []
            
            for patient in patients:
                # Get patient data
                patient_phq9 = PHQ9Assessment.query.filter_by(patient_id=patient.id).order_by(PHQ9Assessment.assessment_date).all()
                patient_exercises = ExerciseSession.query.filter_by(patient_id=patient.id).all()
                
                if patient_phq9 and patient_exercises:
                    population_metrics['active_patients'] += 1
                    
                    # Calculate patient metrics
                    patient_effectiveness = self.outcome_measurement._calculate_patient_effectiveness(patient_exercises)
                    effectiveness_scores.append(patient_effectiveness)
                    
                    if len(patient_phq9) >= 2:
                        improvement = patient_phq9[0].total_score - patient_phq9[-1].total_score
                        improvement_scores.append(improvement)
            
            # Calculate population statistics
            if effectiveness_scores:
                population_metrics['average_effectiveness'] = round(np.mean(effectiveness_scores), 2)
                population_metrics['effectiveness_std'] = round(np.std(effectiveness_scores), 2)
            
            if improvement_scores:
                population_metrics['average_improvement'] = round(np.mean(improvement_scores), 2)
                population_metrics['success_rate'] = round(sum(1 for imp in improvement_scores if imp > 0) / len(improvement_scores) * 100, 1)
                
                # Improvement distribution
                population_metrics['improvement_distribution'] = {
                    'significant_improvement': sum(1 for imp in improvement_scores if imp >= 5),
                    'moderate_improvement': sum(1 for imp in improvement_scores if 2 <= imp < 5),
                    'minimal_improvement': sum(1 for imp in improvement_scores if 0 <= imp < 2),
                    'no_improvement': sum(1 for imp in improvement_scores if imp < 0)
                }
            
            return {
                'population_metrics': population_metrics,
                'patient_rankings': self._generate_patient_rankings(patients),
                'trend_analysis': self._analyze_population_trends(patients),
                'recommendations': self._generate_population_recommendations(population_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error generating population analytics: {str(e)}")
            return {'error': f'Population analytics generation failed: {str(e)}'}

    def generate_crisis_analytics(self, patient_id: int = None) -> Dict:
        """Generate crisis intervention analytics"""
        try:
            from app_ml_complete import CrisisAlert, Patient
            
            if patient_id:
                # Patient-specific crisis analytics
                crisis_data = self.outcome_measurement.track_crisis_intervention_success(patient_id)
                return {
                    'patient_crisis_analytics': crisis_data,
                    'patient_id': patient_id
                }
            else:
                # Population crisis analytics
                all_crises = CrisisAlert.query.all()
                
                crisis_analytics = {
                    'total_crises': len(all_crises),
                    'resolved_crises': sum(1 for crisis in all_crises if crisis.acknowledged),
                    'crisis_types': {},
                    'resolution_times': [],
                    'escalation_patterns': {}
                }
                
                for crisis in all_crises:
                    # Track crisis types
                    crisis_type = crisis.alert_type
                    if crisis_type not in crisis_analytics['crisis_types']:
                        crisis_analytics['crisis_types'][crisis_type] = 0
                    crisis_analytics['crisis_types'][crisis_type] += 1
                    
                    # Calculate resolution times
                    if crisis.acknowledged and crisis.acknowledged_at:
                        resolution_time = (crisis.acknowledged_at - crisis.created_at).total_seconds() / 3600
                        crisis_analytics['resolution_times'].append(resolution_time)
                
                if crisis_analytics['resolution_times']:
                    crisis_analytics['average_resolution_time'] = round(np.mean(crisis_analytics['resolution_times']), 2)
                
                crisis_analytics['resolution_rate'] = crisis_analytics['resolved_crises'] / crisis_analytics['total_crises'] if crisis_analytics['total_crises'] > 0 else 0
                
                return {
                    'population_crisis_analytics': crisis_analytics,
                    'recommendations': self._generate_crisis_recommendations(crisis_analytics)
                }
                
        except Exception as e:
            logger.error(f"Error generating crisis analytics: {str(e)}")
            return {'error': f'Crisis analytics generation failed: {str(e)}'}

    def generate_exercise_effectiveness_report(self, exercise_type: str = None, patient_id: int = None) -> Dict:
        """Generate exercise effectiveness report"""
        try:
            from app_ml_complete import ExerciseSession, Exercise
            
            if patient_id:
                # Patient-specific exercise effectiveness
                patient_exercises = ExerciseSession.query.filter_by(patient_id=patient_id).join(Exercise).all()
                
                exercise_data = [{
                    'date': session.start_time,
                    'exercise_type': session.exercise.type,
                    'completion_status': session.completion_status,
                    'engagement_score': session.engagement_score,
                    'effectiveness_rating': session.effectiveness_rating
                } for session in patient_exercises]
                
                effectiveness_score = self.outcome_measurement.calculate_exercise_effectiveness_score(patient_id, exercise_data)
                
                return {
                    'patient_exercise_effectiveness': effectiveness_score,
                    'exercise_breakdown': self._analyze_exercise_breakdown(exercise_data),
                    'patient_id': patient_id
                }
            else:
                # Population exercise effectiveness
                all_sessions = ExerciseSession.query.join(Exercise).all()
                
                exercise_effectiveness = {}
                
                for exercise_type in set(session.exercise.type for session in all_sessions):
                    type_sessions = [s for s in all_sessions if s.exercise.type == exercise_type]
                    
                    completion_rate = sum(1 for s in type_sessions if s.completion_status == 'completed') / len(type_sessions)
                    avg_engagement = np.mean([s.engagement_score for s in type_sessions if s.engagement_score])
                    avg_effectiveness = np.mean([s.effectiveness_rating for s in type_sessions if s.effectiveness_rating])
                    
                    exercise_effectiveness[exercise_type] = {
                        'total_sessions': len(type_sessions),
                        'completion_rate': round(completion_rate, 3),
                        'average_engagement': round(avg_engagement, 2),
                        'average_effectiveness': round(avg_effectiveness, 2),
                        'effectiveness_score': round((completion_rate * 0.4 + avg_engagement * 0.3 + avg_effectiveness * 0.3) * 10, 2)
                    }
                
                return {
                    'population_exercise_effectiveness': exercise_effectiveness,
                    'top_performing_exercises': sorted(exercise_effectiveness.items(), key=lambda x: x[1]['effectiveness_score'], reverse=True)[:5],
                    'recommendations': self._generate_exercise_recommendations(exercise_effectiveness)
                }
                
        except Exception as e:
            logger.error(f"Error generating exercise effectiveness report: {str(e)}")
            return {'error': f'Exercise effectiveness report generation failed: {str(e)}'}

    # Helper methods
    def _get_outcome_measurements(self, patient_id: int, analytics_data: Dict) -> Dict:
        """Get outcome measurements for patient"""
        try:
            # Extract data from analytics
            phq9_data = analytics_data.get('correlation_analysis', {}).get('phq9_data', [])
            exercise_data = analytics_data.get('correlation_analysis', {}).get('exercise_data', [])
            
            # Calculate outcome measurements
            effectiveness_score = self.outcome_measurement.calculate_exercise_effectiveness_score(patient_id, exercise_data)
            skill_acquisition = self.outcome_measurement.measure_skill_acquisition_rates(patient_id, exercise_data)
            crisis_success = self.outcome_measurement.track_crisis_intervention_success(patient_id)
            population_effectiveness = self.outcome_measurement.generate_population_effectiveness_report(patient_id, phq9_data, exercise_data)
            
            return {
                'effectiveness_score': effectiveness_score,
                'skill_acquisition': skill_acquisition,
                'crisis_intervention_success': crisis_success,
                'population_effectiveness': population_effectiveness
            }
            
        except Exception as e:
            logger.error(f"Error getting outcome measurements: {str(e)}")
            return {'error': f'Outcome measurements failed: {str(e)}'}

    def _get_decision_support(self, patient_id: int, analytics_data: Dict) -> Dict:
        """Get decision support for patient"""
        try:
            # Extract data from analytics
            phq9_data = analytics_data.get('correlation_analysis', {}).get('phq9_data', [])
            exercise_data = analytics_data.get('correlation_analysis', {}).get('exercise_data', [])
            mood_data = analytics_data.get('correlation_analysis', {}).get('mood_data', [])
            
            # Get decision support
            reassessment_timing = self.decision_support.recommend_phq9_reassessment_timing(patient_id, phq9_data, exercise_data)
            intensification_recommendations = self.decision_support.suggest_treatment_intensification(patient_id, phq9_data, exercise_data, mood_data)
            medication_alerts = self.decision_support.alert_medication_evaluation(patient_id, phq9_data, exercise_data)
            outcome_evidence = self.decision_support.generate_outcome_evidence(patient_id, phq9_data, exercise_data)
            
            return {
                'reassessment_timing': reassessment_timing,
                'intensification_recommendations': intensification_recommendations,
                'medication_alerts': medication_alerts,
                'outcome_evidence': outcome_evidence
            }
            
        except Exception as e:
            logger.error(f"Error getting decision support: {str(e)}")
            return {'error': f'Decision support failed: {str(e)}'}

    def _generate_dashboard_summary(self, analytics_data: Dict, outcome_data: Dict, decision_data: Dict) -> Dict:
        """Generate dashboard summary"""
        try:
            summary = {
                'key_metrics': {},
                'alerts': [],
                'recommendations': [],
                'trends': {}
            }
            
            # Extract key metrics
            if 'effectiveness_score' in outcome_data:
                summary['key_metrics']['effectiveness_score'] = outcome_data['effectiveness_score'].get('score', 0)
            
            if 'reassessment_timing' in decision_data:
                summary['key_metrics']['next_reassessment'] = decision_data['reassessment_timing'].get('recommended_timing', '2 weeks')
            
            # Extract alerts
            if 'medication_alerts' in decision_data:
                alerts = decision_data['medication_alerts'].get('alerts', [])
                summary['alerts'] = [alert['description'] for alert in alerts if alert.get('severity') == 'high']
            
            # Extract recommendations
            if 'intensification_recommendations' in decision_data:
                recommendations = decision_data['intensification_recommendations'].get('recommendations', [])
                summary['recommendations'] = [rec['specific_action'] for rec in recommendations]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {str(e)}")
            return {'error': f'Dashboard summary generation failed: {str(e)}'}

    def _generate_correlation_report(self, patient_id: int) -> Dict:
        """Generate correlation analysis report"""
        try:
            analytics_data = self.analytics.generate_comprehensive_analytics(patient_id)
            return {
                'correlation_analysis': analytics_data.get('correlation_analysis', {}),
                'patient_id': patient_id,
                'report_type': 'correlation'
            }
            
        except Exception as e:
            logger.error(f"Error generating correlation report: {str(e)}")
            return {'error': f'Correlation report generation failed: {str(e)}'}

    def _generate_outcomes_report(self, patient_id: int) -> Dict:
        """Generate outcomes report"""
        try:
            analytics_data = self.analytics.generate_comprehensive_analytics(patient_id)
            outcome_data = self._get_outcome_measurements(patient_id, analytics_data)
            
            return {
                'outcome_measurement': outcome_data,
                'patient_id': patient_id,
                'report_type': 'outcomes'
            }
            
        except Exception as e:
            logger.error(f"Error generating outcomes report: {str(e)}")
            return {'error': f'Outcomes report generation failed: {str(e)}'}

    def _generate_decisions_report(self, patient_id: int) -> Dict:
        """Generate decisions report"""
        try:
            analytics_data = self.analytics.generate_comprehensive_analytics(patient_id)
            decision_data = self._get_decision_support(patient_id, analytics_data)
            
            return {
                'decision_support': decision_data,
                'patient_id': patient_id,
                'report_type': 'decisions'
            }
            
        except Exception as e:
            logger.error(f"Error generating decisions report: {str(e)}")
            return {'error': f'Decisions report generation failed: {str(e)}'}

    def _analyze_exercise_breakdown(self, exercise_data: List[Dict]) -> Dict:
        """Analyze exercise breakdown by type"""
        try:
            if not exercise_data:
                return {}
            
            df = pd.DataFrame(exercise_data)
            breakdown = {}
            
            for exercise_type in df['exercise_type'].unique():
                type_data = df[df['exercise_type'] == exercise_type]
                
                breakdown[exercise_type] = {
                    'total_sessions': len(type_data),
                    'completion_rate': (type_data['completion_status'] == 'completed').mean(),
                    'average_engagement': type_data['engagement_score'].mean(),
                    'average_effectiveness': type_data['effectiveness_rating'].mean()
                }
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error analyzing exercise breakdown: {str(e)}")
            return {}

    def _generate_exercise_recommendations(self, exercise_effectiveness: Dict) -> List[str]:
        """Generate exercise recommendations based on effectiveness data"""
        try:
            recommendations = []
            
            # Find low-performing exercises
            low_performing = [ex_type for ex_type, data in exercise_effectiveness.items() 
                            if data['effectiveness_score'] < 60]
            
            if low_performing:
                recommendations.append(f"Review and improve effectiveness of: {', '.join(low_performing)}")
            
            # Find high-performing exercises
            high_performing = [ex_type for ex_type, data in exercise_effectiveness.items() 
                             if data['effectiveness_score'] >= 80]
            
            if high_performing:
                recommendations.append(f"Consider expanding use of effective exercises: {', '.join(high_performing)}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating exercise recommendations: {str(e)}")
            return []

    def _generate_crisis_recommendations(self, crisis_analytics: Dict) -> List[str]:
        """Generate crisis intervention recommendations"""
        try:
            recommendations = []
            
            resolution_rate = crisis_analytics.get('resolution_rate', 0)
            if resolution_rate < 0.7:
                recommendations.append("Improve crisis response protocols and provider notification systems")
            
            avg_resolution_time = crisis_analytics.get('average_resolution_time', 0)
            if avg_resolution_time > 8:
                recommendations.append("Optimize crisis response time through automated alerts and escalation procedures")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating crisis recommendations: {str(e)}")
            return []

# Initialize the analytics dashboard
analytics_dashboard = AnalyticsDashboard()

# Flask routes for the dashboard
def create_dashboard_routes(app):
    """Create Flask routes for the analytics dashboard"""
    
    @app.route('/analytics/dashboard/<int:patient_id>')
    @login_required
    def patient_analytics_dashboard(patient_id):
        """Patient analytics dashboard"""
        try:
            time_period = request.args.get('period', 90, type=int)
            dashboard_data = analytics_dashboard.generate_comprehensive_dashboard(patient_id, time_period)
            
            if 'error' in dashboard_data:
                return jsonify({'error': dashboard_data['error']}), 400
            
            return jsonify(dashboard_data)
            
        except Exception as e:
            logger.error(f"Error in patient analytics dashboard: {str(e)}")
            return jsonify({'error': 'Dashboard generation failed'}), 500

    @app.route('/analytics/provider-report/<int:patient_id>')
    @login_required
    def provider_report(patient_id):
        """Provider-specific report"""
        try:
            report_type = request.args.get('type', 'comprehensive')
            report_data = analytics_dashboard.generate_provider_report(patient_id, report_type)
            
            if 'error' in report_data:
                return jsonify({'error': report_data['error']}), 400
            
            return jsonify(report_data)
            
        except Exception as e:
            logger.error(f"Error in provider report: {str(e)}")
            return jsonify({'error': 'Report generation failed'}), 500

    @app.route('/analytics/population')
    @login_required
    def population_analytics():
        """Population-level analytics"""
        try:
            filters = request.args.to_dict()
            population_data = analytics_dashboard.generate_population_analytics(filters)
            
            if 'error' in population_data:
                return jsonify({'error': population_data['error']}), 400
            
            return jsonify(population_data)
            
        except Exception as e:
            logger.error(f"Error in population analytics: {str(e)}")
            return jsonify({'error': 'Population analytics generation failed'}), 500

    @app.route('/analytics/crisis/<int:patient_id>')
    @login_required
    def crisis_analytics(patient_id):
        """Crisis intervention analytics"""
        try:
            crisis_data = analytics_dashboard.generate_crisis_analytics(patient_id)
            
            if 'error' in crisis_data:
                return jsonify({'error': crisis_data['error']}), 400
            
            return jsonify(crisis_data)
            
        except Exception as e:
            logger.error(f"Error in crisis analytics: {str(e)}")
            return jsonify({'error': 'Crisis analytics generation failed'}), 500

    @app.route('/analytics/exercise-effectiveness')
    @login_required
    def exercise_effectiveness():
        """Exercise effectiveness report"""
        try:
            patient_id = request.args.get('patient_id', type=int)
            exercise_type = request.args.get('exercise_type')
            
            effectiveness_data = analytics_dashboard.generate_exercise_effectiveness_report(exercise_type, patient_id)
            
            if 'error' in effectiveness_data:
                return jsonify({'error': effectiveness_data['error']}), 400
            
            return jsonify(effectiveness_data)
            
        except Exception as e:
            logger.error(f"Error in exercise effectiveness: {str(e)}")
            return jsonify({'error': 'Exercise effectiveness report generation failed'}), 500

    return app
