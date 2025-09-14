#!/usr/bin/env python3
"""
Provider Dashboard Helper Methods
Completes missing functionality for the comprehensive provider dashboard
"""

from datetime import datetime, timedelta
import numpy as np
from sqlalchemy import func, and_, desc

class ProviderDashboardHelpers:
    """Helper methods for the comprehensive provider dashboard"""
    
    @staticmethod
    def _get_recent_mood_data(patient_id, days=7):
        """Get recent mood data for patient"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= start_date
            )
        ).order_by(MoodEntry.timestamp).all()
        
        if not mood_entries:
            return {
                'current_mood_score': 5,
                'mood_trend': 'stable',
                'recent_scores': [],
                'mood_stability': 0
            }
        
        scores = [m.intensity_level for m in mood_entries]
        current_score = scores[-1] if scores else 5
        
        # Calculate mood stability (standard deviation)
        mood_stability = np.std(scores) if len(scores) > 1 else 0
        
        # Calculate trend
        if len(scores) >= 3:
            trend = np.polyfit(range(len(scores)), scores, 1)[0]
            if trend > 0.3:
                trend_direction = 'improving'
            elif trend < -0.3:
                trend_direction = 'declining'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'stable'
        
        return {
            'current_mood_score': current_score,
            'mood_trend': trend_direction,
            'recent_scores': scores,
            'mood_stability': mood_stability
        }
    
    @staticmethod
    def _get_last_activity(patient_id):
        """Get last activity timestamp for patient"""
        # Check mood entries
        last_mood = MoodEntry.query.filter_by(patient_id=patient_id)\
            .order_by(desc(MoodEntry.timestamp)).first()
        
        # Check exercise sessions
        last_exercise = ExerciseSession.query.filter_by(patient_id=patient_id)\
            .order_by(desc(ExerciseSession.start_time)).first()
        
        # Check thought records
        last_thought = ThoughtRecord.query.filter_by(patient_id=patient_id)\
            .order_by(desc(ThoughtRecord.timestamp)).first()
        
        # Find the most recent activity
        activities = []
        if last_mood:
            activities.append(('Mood Entry', last_mood.timestamp))
        if last_exercise:
            activities.append(('Exercise', last_exercise.start_time))
        if last_thought:
            activities.append(('Thought Record', last_thought.timestamp))
        
        if not activities:
            return 'No recent activity'
        
        # Get most recent
        most_recent = max(activities, key=lambda x: x[1])
        days_ago = (datetime.now() - most_recent[1]).days
        
        if days_ago == 0:
            return f"Today - {most_recent[0]}"
        elif days_ago == 1:
            return f"Yesterday - {most_recent[0]}"
        else:
            return f"{days_ago} days ago - {most_recent[0]}"
    
    @staticmethod
    def _calculate_risk_level(status, mood_trajectory, crisis_usage):
        """Calculate overall risk level for patient"""
        risk_score = 0
        
        # Status-based risk
        if status == 'red':
            risk_score += 4
        elif status == 'orange':
            risk_score += 3
        elif status == 'yellow':
            risk_score += 2
        else:
            risk_score += 1
        
        # Mood trajectory risk
        if mood_trajectory.get('trend') == 'declining':
            risk_score += 2
        elif mood_trajectory.get('trend') == 'stable':
            risk_score += 1
        
        # Crisis usage risk
        if crisis_usage.get('recent_crisis_usage', False):
            risk_score += 3
        elif crisis_usage.get('days_since_last_usage', 999) <= 14:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 6:
            return 'critical'
        elif risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _generate_status_recommendations(status, mood_trajectory, exercise_engagement, crisis_usage):
        """Generate recommendations based on patient status"""
        recommendations = []
        
        # Crisis recommendations
        if crisis_usage.get('recent_crisis_usage', False):
            recommendations.append("Immediate crisis intervention required")
            recommendations.append("Review safety planning")
        
        # Mood recommendations
        if mood_trajectory.get('trend') == 'declining':
            recommendations.append("Address declining mood patterns")
            recommendations.append("Consider medication review")
        
        # Engagement recommendations
        if exercise_engagement.get('overall_engagement', 0) < 0.5:
            recommendations.append("Low exercise engagement - consider barriers")
            recommendations.append("Simplify exercise recommendations")
        
        # Status-based recommendations
        if status == 'red':
            recommendations.append("Immediate clinical attention required")
            recommendations.append("Consider hospitalization assessment")
        elif status == 'orange':
            recommendations.append("Increase session frequency")
            recommendations.append("Review treatment plan effectiveness")
        elif status == 'yellow':
            recommendations.append("Monitor closely for deterioration")
            recommendations.append("Reinforce coping strategies")
        else:
            recommendations.append("Continue current treatment plan")
            recommendations.append("Celebrate progress and maintain gains")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    @staticmethod
    def _get_comprehensive_patient_data(patient_id):
        """Get comprehensive data for a patient"""
        return {
            'patient_id': patient_id,
            'traffic_light_status': 'green',  # Will be calculated
            'mood_trajectory': ProviderDashboardHelpers._get_recent_mood_data(patient_id),
            'engagement_percentage': 0.8,  # Will be calculated
            'adherence_score': 0.7,  # Will be calculated
            'crisis_usage': ProviderDashboardHelpers._get_crisis_usage_data(patient_id)
        }
    
    @staticmethod
    def _get_immediate_attention_reason(patient_data):
        """Get reason for immediate attention"""
        reasons = []
        
        if patient_data.get('traffic_light_status') == 'red':
            reasons.append("Critical status indicators")
        
        if patient_data.get('crisis_usage', {}).get('recent_crisis_usage', False):
            reasons.append("Recent crisis tool usage")
        
        if patient_data.get('mood_trajectory', {}).get('trend') == 'declining':
            reasons.append("Declining mood trajectory")
        
        return "; ".join(reasons) if reasons else "Multiple risk factors detected"
    
    @staticmethod
    def _get_immediate_action(patient_data):
        """Get immediate action recommendation"""
        if patient_data.get('crisis_usage', {}).get('recent_crisis_usage', False):
            return "Contact patient immediately for crisis assessment"
        elif patient_data.get('traffic_light_status') == 'red':
            return "Schedule urgent session within 24 hours"
        else:
            return "Review treatment plan and consider intervention"
    
    @staticmethod
    def _get_treatment_adjustment_reason(patient_data):
        """Get reason for treatment adjustment"""
        reasons = []
        
        if patient_data.get('engagement_percentage', 0) < 0.5:
            reasons.append("Low engagement")
        
        if patient_data.get('adherence_score', 0) < 0.6:
            reasons.append("Poor treatment adherence")
        
        if patient_data.get('traffic_light_status') == 'orange':
            reasons.append("Warning status indicators")
        
        return "; ".join(reasons) if reasons else "Treatment plan not effective"
    
    @staticmethod
    def _get_treatment_adjustment_action(patient_data):
        """Get treatment adjustment action"""
        return "Review and modify treatment plan based on engagement patterns"
    
    @staticmethod
    def _get_good_progress_reason(patient_data):
        """Get reason for good progress"""
        reasons = []
        
        if patient_data.get('traffic_light_status') == 'green':
            reasons.append("Good status indicators")
        
        if patient_data.get('mood_trajectory', {}).get('trend') == 'improving':
            reasons.append("Improving mood trajectory")
        
        if patient_data.get('engagement_percentage', 0) > 0.8:
            reasons.append("High engagement")
        
        return "; ".join(reasons) if reasons else "Positive treatment response"
    
    @staticmethod
    def _get_celebration_action(patient_data):
        """Get celebration action"""
        return "Acknowledge progress and reinforce positive changes"
    
    @staticmethod
    def _get_concerning_pattern_reason(patient_data):
        """Get reason for concerning patterns"""
        reasons = []
        
        if patient_data.get('mood_trajectory', {}).get('trend') == 'declining':
            reasons.append("Declining mood")
        
        if patient_data.get('engagement_percentage', 0) < 0.7:
            reasons.append("Decreasing engagement")
        
        if patient_data.get('traffic_light_status') == 'yellow':
            reasons.append("Caution indicators")
        
        return "; ".join(reasons) if reasons else "Emerging concerning patterns"
    
    @staticmethod
    def _get_early_intervention_action(patient_data):
        """Get early intervention action"""
        return "Implement early intervention strategies to prevent deterioration"
    
    @staticmethod
    def _get_last_phq9_assessment(patient_id):
        """Get last PHQ-9 assessment for patient"""
        return PHQ9Assessment.query.filter_by(patient_id=patient_id)\
            .order_by(desc(PHQ9Assessment.assessment_date)).first()
    
    @staticmethod
    def _get_crisis_episodes(patient_id):
        """Get crisis episodes for patient"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= start_date
            )
        ).order_by(desc(CrisisAlert.created_at)).all()
        
        episodes = []
        for alert in crisis_alerts:
            episodes.append({
                'date': alert.created_at.strftime('%Y-%m-%d'),
                'description': alert.alert_message,
                'context': f"Severity: {alert.severity_level}",
                'type': alert.alert_type
            })
        
        return episodes
    
    @staticmethod
    def _get_progress_highlights(patient_id):
        """Get progress highlights for patient"""
        highlights = []
        
        # Check for mood improvement
        mood_data = ProviderDashboardHelpers._get_recent_mood_data(patient_id, 14)
        if mood_data.get('mood_trend') == 'improving':
            highlights.append({
                'type': 'Mood Improvement',
                'description': 'Consistent mood improvement over 2 weeks',
                'impact': 'Positive treatment response'
            })
        
        # Check for exercise engagement
        engagement = ProviderDashboardHelpers._get_exercise_engagement(patient_id)
        if engagement.get('overall_engagement', 0) > 0.8:
            highlights.append({
                'type': 'High Engagement',
                'description': f"{(engagement.get('overall_engagement', 0) * 100):.1f}% exercise completion rate",
                'impact': 'Good treatment adherence'
            })
        
        # Check for crisis reduction
        crisis_data = ProviderDashboardHelpers._get_crisis_usage_data(patient_id)
        if crisis_data.get('days_since_last_usage', 0) > 14:
            highlights.append({
                'type': 'Crisis Reduction',
                'description': f"No crisis episodes for {crisis_data.get('days_since_last_usage', 0)} days",
                'impact': 'Improved crisis management'
            })
        
        return highlights
    
    @staticmethod
    def _get_concerning_patterns(patient_id):
        """Get concerning patterns for patient"""
        patterns = []
        
        # Check mood stability
        mood_data = ProviderDashboardHelpers._get_recent_mood_data(patient_id, 7)
        if mood_data.get('mood_stability', 0) > 2:
            patterns.append({
                'type': 'Mood Instability',
                'description': 'High mood variability',
                'severity': 'moderate'
            })
        
        # Check engagement drops
        engagement = ProviderDashboardHelpers._get_exercise_engagement(patient_id)
        if engagement.get('weekly_comparison', 0) < -20:
            patterns.append({
                'type': 'Engagement Drop',
                'description': f"{(abs(engagement.get('weekly_comparison', 0))):.1f}% decrease in engagement",
                'severity': 'high'
            })
        
        return patterns
    
    @staticmethod
    def _get_last_session_date(patient_id):
        """Get last session date for patient"""
        # This would typically come from a session tracking system
        # For now, return a placeholder
        return "2024-01-15"  # Placeholder
    
    @staticmethod
    def _get_session_notes(patient_id):
        """Get session notes for patient"""
        # This would typically come from a session notes system
        # For now, return placeholder
        return "Patient showed good engagement with CBT exercises. Mood slightly improved."
    
    @staticmethod
    def _calculate_goal_achievement(patient_id):
        """Calculate treatment goal achievement"""
        # This would be based on specific treatment goals
        # For now, return placeholder data
        return {
            'overall_achievement': 75,
            'mood_goals': 80,
            'engagement_goals': 70,
            'crisis_goals': 90
        }
    
    @staticmethod
    def _calculate_functional_improvement(patient_id):
        """Calculate functional improvement"""
        # This would be based on functional assessments
        # For now, return placeholder data
        return {
            'social_functioning': 70,
            'work_functioning': 65,
            'daily_activities': 80,
            'overall_functioning': 72
        }
    
    @staticmethod
    def _calculate_overall_effectiveness(improvement_rates, crisis_success, goal_achievement, functional_improvement):
        """Calculate overall treatment effectiveness score"""
        # Weighted average of different effectiveness measures
        mood_score = improvement_rates.get('mood_improvement', 0) / 100
        crisis_score = crisis_success.get('success_rate', 100) / 100
        goal_score = goal_achievement.get('overall_achievement', 0) / 100
        functional_score = functional_improvement.get('overall_functioning', 0) / 100
        
        # Weighted average
        overall_score = (
            mood_score * 0.3 +
            crisis_score * 0.25 +
            goal_score * 0.25 +
            functional_score * 0.2
        ) * 100
        
        return min(100, max(0, overall_score))
    
    @staticmethod
    def _calculate_system_effectiveness(patients):
        """Calculate system-wide effectiveness metrics"""
        total_patients = len(patients)
        if total_patients == 0:
            return {
                'average_improvement': 0,
                'crisis_resolution_rate': 0,
                'engagement_rate': 0,
                'satisfaction_score': 0
            }
        
        # Calculate averages across all patients
        total_improvement = 0
        total_crisis_resolution = 0
        total_engagement = 0
        
        for patient in patients:
            # Get patient data (simplified for this example)
            improvement = 50  # Placeholder
            crisis_resolution = 80  # Placeholder
            engagement = 70  # Placeholder
            
            total_improvement += improvement
            total_crisis_resolution += crisis_resolution
            total_engagement += engagement
        
        return {
            'average_improvement': total_improvement / total_patients,
            'crisis_resolution_rate': total_crisis_resolution / total_patients,
            'engagement_rate': total_engagement / total_patients,
            'satisfaction_score': 85  # Placeholder
        }
    
    @staticmethod
    def _calculate_quality_metrics(patients):
        """Calculate quality metrics for value-based care"""
        total_patients = len(patients)
        if total_patients == 0:
            return {
                'readmission_rate': 0,
                'treatment_completion_rate': 0,
                'patient_satisfaction': 0,
                'clinical_outcomes': 0
            }
        
        # Calculate quality metrics (simplified for this example)
        return {
            'readmission_rate': 5.2,  # Percentage
            'treatment_completion_rate': 78.5,  # Percentage
            'patient_satisfaction': 4.2,  # Out of 5
            'clinical_outcomes': 82.3  # Percentage
        }
    
    @staticmethod
    def _generate_adherence_recommendations(mood_adherence, exercise_adherence, thought_adherence):
        """Generate adherence recommendations"""
        recommendations = []
        
        if mood_adherence < 0.7:
            recommendations.append("Increase mood tracking frequency")
        
        if exercise_adherence < 0.6:
            recommendations.append("Simplify exercise recommendations")
            recommendations.append("Address exercise barriers")
        
        if thought_adherence < 0.5:
            recommendations.append("Provide more CBT guidance")
            recommendations.append("Consider group therapy options")
        
        if not recommendations:
            recommendations.append("Maintain current adherence levels")
        
        return recommendations
    
    @staticmethod
    def _generate_status_summary(patient_statuses):
        """Generate summary of patient statuses"""
        total_patients = len(patient_statuses)
        if total_patients == 0:
            return {
                'total_patients': 0,
                'status_breakdown': {},
                'average_engagement': 0,
                'crisis_patients': 0
            }
        
        # Count statuses
        status_counts = {}
        total_engagement = 0
        crisis_patients = 0
        
        for patient in patient_statuses:
            status = patient.get('traffic_light_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            total_engagement += patient.get('engagement_percentage', 0)
            
            if patient.get('days_since_crisis', 999) <= 7:
                crisis_patients += 1
        
        return {
            'total_patients': total_patients,
            'status_breakdown': status_counts,
            'average_engagement': (total_engagement / total_patients) * 100,
            'crisis_patients': crisis_patients
        }
