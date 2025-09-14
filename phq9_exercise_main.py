#!/usr/bin/env python3
"""
PHQ-9 Exercise Integration Main System
Demonstrates the complete integration of PHQ-9 analysis with adaptive exercise recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import logging

# Import all the integration components
from phq9_exercise_integration import phq9_exercise_integration
from exercise_execution_engine import exercise_execution_engine
from provider_dashboard import provider_dashboard
from patient_motivation_system import patient_motivation_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PHQ9ExerciseMainSystem:
    """Main system that orchestrates all PHQ-9 exercise integration components"""
    
    def __init__(self):
        self.integration = phq9_exercise_integration
        self.execution_engine = exercise_execution_engine
        self.dashboard = provider_dashboard
        self.motivation_system = patient_motivation_system

    def process_phq9_assessment(self, patient_id: int, assessment_id: int) -> Dict:
        """Complete workflow for processing a PHQ-9 assessment and generating exercise recommendations"""
        try:
            logger.info(f"Processing PHQ-9 assessment {assessment_id} for patient {patient_id}")
            
            # Step 1: Generate adaptive recommendations based on PHQ-9
            recommendations = self.integration.generate_adaptive_recommendations(patient_id, assessment_id)
            
            if 'error' in recommendations:
                return {'error': f'Failed to generate recommendations: {recommendations["error"]}'}
            
            # Step 2: Create provider dashboard update
            dashboard_update = self.dashboard.get_daily_dashboard()
            
            # Step 3: Generate patient motivation elements
            motivation_data = self.motivation_system.create_progress_visualization(patient_id)
            
            # Step 4: Create comprehensive response
            response = {
                'timestamp': datetime.now().isoformat(),
                'patient_id': patient_id,
                'assessment_id': assessment_id,
                'recommendations': recommendations,
                'dashboard_update': dashboard_update,
                'motivation_data': motivation_data,
                'next_actions': self._generate_next_actions(patient_id, recommendations)
            }
            
            logger.info(f"Successfully processed PHQ-9 assessment for patient {patient_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing PHQ-9 assessment: {str(e)}")
            return {'error': f'Processing failed: {str(e)}'}

    def execute_exercise_session(self, patient_id: int, exercise_type: str, context: Dict = None) -> Dict:
        """Execute an exercise session with real-time adaptation"""
        try:
            logger.info(f"Executing exercise {exercise_type} for patient {patient_id}")
            
            # Execute the exercise
            execution_result = self.execution_engine.execute_exercise(patient_id, exercise_type, context)
            
            if 'error' in execution_result:
                return {'error': f'Exercise execution failed: {execution_result["error"]}'}
            
            # Generate motivation notification
            notification = self.motivation_system.generate_smart_notification(patient_id, 'motivational')
            
            # Update provider dashboard
            dashboard_update = self.dashboard.get_patient_detailed_view(patient_id)
            
            # Create comprehensive response
            response = {
                'timestamp': datetime.now().isoformat(),
                'patient_id': patient_id,
                'exercise_type': exercise_type,
                'execution_result': execution_result,
                'motivation_notification': notification,
                'dashboard_update': dashboard_update,
                'next_recommendations': execution_result.get('next_recommendations', [])
            }
            
            logger.info(f"Successfully executed exercise for patient {patient_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error executing exercise session: {str(e)}")
            return {'error': f'Exercise execution failed: {str(e)}'}

    def get_provider_insights(self, provider_id: int = None) -> Dict:
        """Get comprehensive provider insights and dashboard"""
        try:
            logger.info("Generating provider insights")
            
            # Get daily dashboard
            daily_dashboard = self.dashboard.get_daily_dashboard(provider_id)
            
            # Get crisis escalation report
            crisis_report = self.dashboard.get_crisis_escalation_report()
            
            # Get weekly report
            weekly_report = self.dashboard.get_weekly_report()
            
            # Create comprehensive insights
            insights = {
                'timestamp': datetime.now().isoformat(),
                'daily_dashboard': daily_dashboard,
                'crisis_report': crisis_report,
                'weekly_report': weekly_report,
                'priority_actions': self._identify_priority_actions(daily_dashboard, crisis_report),
                'system_health': self._assess_system_health()
            }
            
            logger.info("Successfully generated provider insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating provider insights: {str(e)}")
            return {'error': f'Insights generation failed: {str(e)}'}

    def generate_patient_report(self, patient_id: int) -> Dict:
        """Generate comprehensive patient report"""
        try:
            logger.info(f"Generating comprehensive report for patient {patient_id}")
            
            # Get detailed patient view
            patient_view = self.dashboard.get_patient_detailed_view(patient_id)
            
            # Get progress visualization
            progress_viz = self.motivation_system.create_progress_visualization(patient_id)
            
            # Get weekly report
            weekly_report = self.dashboard.get_weekly_report(patient_id)
            
            # Create comprehensive report
            report = {
                'timestamp': datetime.now().isoformat(),
                'patient_id': patient_id,
                'patient_view': patient_view,
                'progress_visualization': progress_viz,
                'weekly_report': weekly_report,
                'recommendations': self._generate_patient_recommendations(patient_id),
                'engagement_analysis': self._analyze_patient_engagement(patient_id)
            }
            
            logger.info(f"Successfully generated report for patient {patient_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating patient report: {str(e)}")
            return {'error': f'Report generation failed: {str(e)}'}

    def handle_crisis_situation(self, patient_id: int, crisis_data: Dict) -> Dict:
        """Handle crisis situation with immediate intervention"""
        try:
            logger.info(f"Handling crisis situation for patient {patient_id}")
            
            # Execute crisis exercise
            crisis_result = self.execution_engine.execute_exercise(
                patient_id, 'breathing_grounding', 
                context={'crisis_indicators': crisis_data.get('indicators', [])}
            )
            
            # Generate urgent notification
            urgent_notification = self.motivation_system.generate_smart_notification(
                patient_id, 'reminder'
            )
            
            # Update provider dashboard with crisis alert
            dashboard_update = self.dashboard.get_crisis_escalation_report()
            
            # Create crisis response
            response = {
                'timestamp': datetime.now().isoformat(),
                'patient_id': patient_id,
                'crisis_handled': True,
                'crisis_result': crisis_result,
                'urgent_notification': urgent_notification,
                'dashboard_update': dashboard_update,
                'provider_alert': True,
                'next_actions': ['immediate_provider_contact', 'crisis_monitoring', 'safety_planning']
            }
            
            logger.info(f"Successfully handled crisis for patient {patient_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error handling crisis situation: {str(e)}")
            return {'error': f'Crisis handling failed: {str(e)}'}

    def _generate_next_actions(self, patient_id: int, recommendations: Dict) -> List[Dict]:
        """Generate next actions based on recommendations"""
        try:
            actions = []
            
            # Add exercise execution actions
            exercise_recs = recommendations.get('exercise_recommendations', {})
            if 'daily' in exercise_recs:
                for exercise in exercise_recs['daily']:
                    actions.append({
                        'type': 'execute_exercise',
                        'exercise': exercise,
                        'priority': 'high',
                        'timing': 'today'
                    })
            
            # Add monitoring actions
            monitoring_plan = recommendations.get('monitoring_plan', {})
            if monitoring_plan.get('weekly_analysis'):
                actions.append({
                    'type': 'weekly_analysis',
                    'priority': 'medium',
                    'timing': 'weekly'
                })
            
            # Add motivation actions
            actions.append({
                'type': 'send_motivation',
                'priority': 'medium',
                'timing': 'daily'
            })
            
            return actions
            
        except Exception as e:
            logger.error(f"Error generating next actions: {str(e)}")
            return []

    def _identify_priority_actions(self, daily_dashboard: Dict, crisis_report: Dict) -> List[Dict]:
        """Identify priority actions for providers"""
        try:
            priority_actions = []
            
            # Check for crisis alerts
            if crisis_report.get('crisis_alerts_24h', 0) > 0:
                priority_actions.append({
                    'type': 'crisis_intervention',
                    'priority': 'critical',
                    'description': f"{crisis_report['crisis_alerts_24h']} crisis alerts in last 24 hours",
                    'action': 'immediate_review'
                })
            
            # Check for severe patients
            if crisis_report.get('severe_patients', 0) > 0:
                priority_actions.append({
                    'type': 'severe_patient_monitoring',
                    'priority': 'high',
                    'description': f"{crisis_report['severe_patients']} patients with severe depression",
                    'action': 'review_care_plans'
                })
            
            # Check for declining engagement
            if crisis_report.get('declining_engagement', 0) > 0:
                priority_actions.append({
                    'type': 'engagement_intervention',
                    'priority': 'medium',
                    'description': f"{crisis_report['declining_engagement']} patients with declining engagement",
                    'action': 'adjust_exercise_plans'
                })
            
            return priority_actions
            
        except Exception as e:
            logger.error(f"Error identifying priority actions: {str(e)}")
            return []

    def _assess_system_health(self) -> Dict:
        """Assess overall system health and performance"""
        try:
            # This would include various system health metrics
            # For now, return basic health status
            return {
                'status': 'healthy',
                'active_patients': 0,  # Would be calculated from database
                'system_performance': 'optimal',
                'last_maintenance': datetime.now().isoformat(),
                'recommendations': []
            }
            
        except Exception as e:
            logger.error(f"Error assessing system health: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def _generate_patient_recommendations(self, patient_id: int) -> List[Dict]:
        """Generate specific recommendations for patient"""
        try:
            recommendations = []
            
            # Get patient's current state
            patient_view = self.dashboard.get_patient_detailed_view(patient_id)
            
            if 'error' in patient_view:
                return recommendations
            
            # Generate recommendations based on current state
            current_status = patient_view.get('current_status', {})
            engagement = patient_view.get('exercise_engagement', {})
            
            # Low engagement recommendation
            if engagement.get('completion_rate', 1) < 0.5:
                recommendations.append({
                    'type': 'increase_support',
                    'description': 'Low exercise completion - consider simplified exercises',
                    'priority': 'high'
                })
            
            # Mood improvement recommendation
            if current_status.get('current_mood_trend') == 'declining':
                recommendations.append({
                    'type': 'mood_intervention',
                    'description': 'Declining mood trend - consider crisis monitoring',
                    'priority': 'high'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating patient recommendations: {str(e)}")
            return []

    def _analyze_patient_engagement(self, patient_id: int) -> Dict:
        """Analyze patient engagement patterns"""
        try:
            # Get patient's exercise history
            patient_view = self.dashboard.get_patient_detailed_view(patient_id)
            
            if 'error' in patient_view:
                return {'engagement_level': 'unknown', 'trend': 'unknown'}
            
            engagement_data = patient_view.get('exercise_engagement', {})
            
            return {
                'engagement_level': engagement_data.get('engagement_level', 'unknown'),
                'completion_rate': engagement_data.get('completion_rate', 0),
                'trend': engagement_data.get('trend', 'unknown'),
                'recommendations': self._generate_engagement_recommendations(engagement_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patient engagement: {str(e)}")
            return {'engagement_level': 'error', 'trend': 'error'}

    def _generate_engagement_recommendations(self, engagement_data: Dict) -> List[str]:
        """Generate engagement improvement recommendations"""
        try:
            recommendations = []
            
            completion_rate = engagement_data.get('completion_rate', 0)
            
            if completion_rate < 0.3:
                recommendations.append("Consider crisis intervention and immediate provider contact")
            elif completion_rate < 0.5:
                recommendations.append("Simplify exercise plan and increase support")
            elif completion_rate < 0.7:
                recommendations.append("Add motivational elements and check-in reminders")
            elif completion_rate < 0.9:
                recommendations.append("Maintain current plan and celebrate progress")
            else:
                recommendations.append("Consider advancing to more challenging exercises")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating engagement recommendations: {str(e)}")
            return []

# Initialize the main system
phq9_exercise_main = PHQ9ExerciseMainSystem()

def demonstrate_system_workflow():
    """Demonstrate the complete system workflow"""
    try:
        logger.info("Starting PHQ-9 Exercise Integration System demonstration")
        
        # Example patient and assessment IDs (would come from actual database)
        example_patient_id = 1
        example_assessment_id = 1
        
        # Step 1: Process PHQ-9 assessment
        logger.info("Step 1: Processing PHQ-9 assessment")
        assessment_result = phq9_exercise_main.process_phq9_assessment(
            example_patient_id, example_assessment_id
        )
        
        if 'error' not in assessment_result:
            logger.info("✓ PHQ-9 assessment processed successfully")
            print("Assessment Result:", json.dumps(assessment_result, indent=2))
        else:
            logger.error(f"✗ Assessment processing failed: {assessment_result['error']}")
        
        # Step 2: Execute exercise session
        logger.info("Step 2: Executing exercise session")
        exercise_result = phq9_exercise_main.execute_exercise_session(
            example_patient_id, 'mood_check_in'
        )
        
        if 'error' not in exercise_result:
            logger.info("✓ Exercise session executed successfully")
            print("Exercise Result:", json.dumps(exercise_result, indent=2))
        else:
            logger.error(f"✗ Exercise execution failed: {exercise_result['error']}")
        
        # Step 3: Generate provider insights
        logger.info("Step 3: Generating provider insights")
        insights = phq9_exercise_main.get_provider_insights()
        
        if 'error' not in insights:
            logger.info("✓ Provider insights generated successfully")
            print("Provider Insights:", json.dumps(insights, indent=2))
        else:
            logger.error(f"✗ Insights generation failed: {insights['error']}")
        
        # Step 4: Generate patient report
        logger.info("Step 4: Generating patient report")
        patient_report = phq9_exercise_main.generate_patient_report(example_patient_id)
        
        if 'error' not in patient_report:
            logger.info("✓ Patient report generated successfully")
            print("Patient Report:", json.dumps(patient_report, indent=2))
        else:
            logger.error(f"✗ Report generation failed: {patient_report['error']}")
        
        logger.info("PHQ-9 Exercise Integration System demonstration completed")
        
    except Exception as e:
        logger.error(f"Demonstration failed: {str(e)}")

if __name__ == "__main__":
    # Run the demonstration
    demonstrate_system_workflow()
