#!/usr/bin/env python3
"""
Outcome Measurement System
Comprehensive measurement of exercise effectiveness, skill acquisition, and crisis intervention success
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
import numpy as np
import pandas as pd
from sqlalchemy import and_, func, desc
from sqlalchemy.orm import joinedload

from app_ml_complete import (
    db, Patient, PHQ9Assessment, Exercise, ExerciseSession, 
    CrisisAlert, MoodEntry, MindfulnessSession, ExerciseStreak
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutcomeMeasurement:
    """Comprehensive outcome measurement system for PHQ-9 exercise integration"""
    
    def __init__(self):
        self.effectiveness_thresholds = {
            'excellent': 80,
            'good': 60,
            'fair': 40,
            'poor': 20
        }
        
    def calculate_exercise_effectiveness_score(self, patient_id: int, exercise_data: List[Dict]) -> Dict:
        """Calculate comprehensive Exercise Effectiveness Score for a patient"""
        try:
            if not exercise_data:
                return {'score': 0, 'components': {}, 'interpretation': 'No exercise data available'}
            
            df = pd.DataFrame(exercise_data)
            
            # Calculate component scores
            completion_score = (df['completion_status'] == 'completed').mean() * 100
            engagement_score = df['engagement_score'].mean() * 10  # Scale to 100
            effectiveness_score = df['effectiveness_rating'].mean() * 10  # Scale to 100
            
            # Calculate consistency score (standard deviation of engagement)
            consistency_score = max(0, 100 - (df['engagement_score'].std() * 10))
            
            # Calculate progress score (improvement over time)
            progress_score = self._calculate_progress_score(df)
            
            # Weighted composite score
            weights = {
                'completion': 0.25,
                'engagement': 0.25,
                'effectiveness': 0.20,
                'consistency': 0.15,
                'progress': 0.15
            }
            
            composite_score = (
                completion_score * weights['completion'] +
                engagement_score * weights['engagement'] +
                effectiveness_score * weights['effectiveness'] +
                consistency_score * weights['consistency'] +
                progress_score * weights['progress']
            )
            
            return {
                'score': round(composite_score, 1),
                'components': {
                    'completion_rate': round(completion_score, 1),
                    'engagement_level': round(engagement_score, 1),
                    'effectiveness_rating': round(effectiveness_score, 1),
                    'consistency': round(consistency_score, 1),
                    'progress': round(progress_score, 1)
                },
                'interpretation': self._interpret_effectiveness_score(composite_score),
                'recommendations': self._generate_effectiveness_recommendations(composite_score, {
                    'completion': completion_score,
                    'engagement': engagement_score,
                    'effectiveness': effectiveness_score,
                    'consistency': consistency_score,
                    'progress': progress_score
                })
            }
            
        except Exception as e:
            logger.error(f"Error calculating effectiveness score: {str(e)}")
            return {'error': f'Effectiveness score calculation failed: {str(e)}'}

    def measure_skill_acquisition_rates(self, patient_id: int, exercise_data: List[Dict]) -> Dict:
        """Measure skill acquisition rates for CBT techniques and mindfulness"""
        try:
            df = pd.DataFrame(exercise_data)
            
            # Group by exercise type and analyze skill development
            skill_development = {}
            
            for exercise_type in df['exercise_type'].unique():
                type_data = df[df['exercise_type'] == exercise_type]
                
                if len(type_data) < 3:
                    continue
                
                # Calculate skill development metrics
                skill_development[exercise_type] = {
                    'total_sessions': len(type_data),
                    'completion_rate': (type_data['completion_status'] == 'completed').mean(),
                    'engagement_trend': self._calculate_engagement_trend(type_data),
                    'effectiveness_trend': self._calculate_effectiveness_trend(type_data),
                    'skill_mastery_level': self._assess_skill_mastery(type_data),
                    'learning_curve': self._analyze_learning_curve(type_data)
                }
            
            # Calculate overall skill acquisition rate
            overall_acquisition = self._calculate_overall_skill_acquisition(skill_development)
            
            return {
                'skill_development_by_type': skill_development,
                'overall_acquisition_rate': overall_acquisition,
                'mastery_levels': self._summarize_mastery_levels(skill_development),
                'recommendations': self._generate_skill_development_recommendations(skill_development)
            }
            
        except Exception as e:
            logger.error(f"Error measuring skill acquisition: {str(e)}")
            return {'error': f'Skill acquisition measurement failed: {str(e)}'}

    def track_crisis_intervention_success(self, patient_id: int) -> Dict:
        """Track crisis intervention success rates"""
        try:
            # Get crisis alerts and interventions
            crisis_alerts = CrisisAlert.query.filter_by(patient_id=patient_id).all()
            
            if not crisis_alerts:
                return {'message': 'No crisis interventions recorded'}
            
            success_metrics = {
                'total_crises': len(crisis_alerts),
                'resolved_crises': 0,
                'escalation_rate': 0,
                'average_resolution_time': 0,
                'crisis_types': {}
            }
            
            resolution_times = []
            
            for alert in crisis_alerts:
                # Track crisis type
                alert_type = alert.alert_type
                if alert_type not in success_metrics['crisis_types']:
                    success_metrics['crisis_types'][alert_type] = {
                        'count': 0,
                        'resolved': 0,
                        'escalated': 0
                    }
                success_metrics['crisis_types'][alert_type]['count'] += 1
                
                # Check if crisis was resolved (acknowledged and no follow-up alerts within 24 hours)
                if alert.acknowledged:
                    success_metrics['resolved_crises'] += 1
                    success_metrics['crisis_types'][alert_type]['resolved'] += 1
                    
                    # Calculate resolution time
                    if alert.acknowledged_at:
                        resolution_time = (alert.acknowledged_at - alert.created_at).total_seconds() / 3600  # hours
                        resolution_times.append(resolution_time)
                
                # Check for escalation (multiple alerts within short time)
                follow_up_alerts = CrisisAlert.query.filter(
                    and_(
                        CrisisAlert.patient_id == patient_id,
                        CrisisAlert.created_at > alert.created_at,
                        CrisisAlert.created_at < alert.created_at + timedelta(hours=24)
                    )
                ).count()
                
                if follow_up_alerts > 0:
                    success_metrics['escalation_rate'] += 1
                    success_metrics['crisis_types'][alert_type]['escalated'] += 1
            
            # Calculate averages
            if resolution_times:
                success_metrics['average_resolution_time'] = round(np.mean(resolution_times), 2)
            
            success_metrics['escalation_rate'] = success_metrics['escalation_rate'] / len(crisis_alerts)
            success_metrics['resolution_rate'] = success_metrics['resolved_crises'] / len(crisis_alerts)
            
            return {
                'success_metrics': success_metrics,
                'crisis_effectiveness': self._assess_crisis_effectiveness(success_metrics),
                'recommendations': self._generate_crisis_recommendations(success_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error tracking crisis intervention success: {str(e)}")
            return {'error': f'Crisis intervention tracking failed: {str(e)}'}

    def generate_population_effectiveness_report(self, patient_id: int, phq9_data: List[Dict], exercise_data: List[Dict]) -> Dict:
        """Generate population-level effectiveness reports"""
        try:
            # Get population data for comparison
            all_patients = Patient.query.all()
            population_metrics = {
                'total_patients': len(all_patients),
                'active_patients': 0,
                'average_effectiveness': 0,
                'success_rate': 0,
                'improvement_distribution': {}
            }
            
            # Calculate population averages
            effectiveness_scores = []
            improvement_scores = []
            
            for patient in all_patients:
                # Get patient's exercise data
                patient_exercises = ExerciseSession.query.filter_by(patient_id=patient.id).all()
                patient_phq9 = PHQ9Assessment.query.filter_by(patient_id=patient.id).order_by(PHQ9Assessment.assessment_date).all()
                
                if patient_exercises and patient_phq9:
                    population_metrics['active_patients'] += 1
                    
                    # Calculate patient effectiveness
                    patient_effectiveness = self._calculate_patient_effectiveness(patient_exercises)
                    effectiveness_scores.append(patient_effectiveness)
                    
                    # Calculate patient improvement
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
            
            # Compare current patient to population
            current_patient_effectiveness = self._calculate_patient_effectiveness_from_data(exercise_data)
            current_patient_improvement = self._calculate_patient_improvement_from_data(phq9_data)
            
            population_comparison = {
                'effectiveness_percentile': self._calculate_percentile(current_patient_effectiveness, effectiveness_scores),
                'improvement_percentile': self._calculate_percentile(current_patient_improvement, improvement_scores),
                'relative_performance': self._assess_relative_performance(current_patient_effectiveness, current_patient_improvement, population_metrics)
            }
            
            return {
                'population_metrics': population_metrics,
                'current_patient_comparison': population_comparison,
                'benchmark_analysis': self._generate_benchmark_analysis(population_metrics, current_patient_effectiveness, current_patient_improvement)
            }
            
        except Exception as e:
            logger.error(f"Error generating population effectiveness report: {str(e)}")
            return {'error': f'Population effectiveness report generation failed: {str(e)}'}

    # Helper methods
    def _calculate_progress_score(self, df: pd.DataFrame) -> float:
        """Calculate progress score based on improvement over time"""
        try:
            if len(df) < 2:
                return 50  # Neutral score for insufficient data
            
            # Sort by date and calculate engagement trend
            df_sorted = df.sort_values('date')
            engagement_trend = np.polyfit(range(len(df_sorted)), df_sorted['engagement_score'], 1)[0]
            
            # Convert trend to progress score (0-100)
            if engagement_trend > 0:
                progress_score = min(100, 50 + (engagement_trend * 100))
            else:
                progress_score = max(0, 50 + (engagement_trend * 100))
            
            return progress_score
            
        except Exception as e:
            logger.error(f"Error calculating progress score: {str(e)}")
            return 50

    def _interpret_effectiveness_score(self, score: float) -> str:
        """Interpret effectiveness score"""
        if score >= self.effectiveness_thresholds['excellent']:
            return "Excellent - Patient is highly engaged and showing good outcomes"
        elif score >= self.effectiveness_thresholds['good']:
            return "Good - Patient is engaged with positive trends"
        elif score >= self.effectiveness_thresholds['fair']:
            return "Fair - Moderate engagement with room for improvement"
        else:
            return "Poor - Low engagement requiring intervention"

    def _generate_effectiveness_recommendations(self, score: float, components: Dict) -> List[str]:
        """Generate recommendations based on effectiveness score and components"""
        recommendations = []
        
        if score < self.effectiveness_thresholds['fair']:
            recommendations.append("Consider increasing exercise frequency and intensity")
            recommendations.append("Add motivational support and reminders")
            recommendations.append("Review exercise difficulty level")
        
        if components['completion'] < 60:
            recommendations.append("Focus on improving exercise completion rates")
            recommendations.append("Simplify exercises or reduce duration")
        
        if components['engagement'] < 60:
            recommendations.append("Enhance exercise engagement through personalization")
            recommendations.append("Add gamification elements")
        
        if components['consistency'] < 60:
            recommendations.append("Work on maintaining consistent engagement")
            recommendations.append("Establish regular exercise routines")
        
        return recommendations

    def _calculate_engagement_trend(self, type_data: pd.DataFrame) -> float:
        """Calculate engagement trend over time"""
        try:
            if len(type_data) < 2:
                return 0
            
            type_data_sorted = type_data.sort_values('date')
            engagement_trend = np.polyfit(range(len(type_data_sorted)), type_data_sorted['engagement_score'], 1)[0]
            return round(engagement_trend, 3)
            
        except Exception as e:
            logger.error(f"Error calculating engagement trend: {str(e)}")
            return 0

    def _calculate_effectiveness_trend(self, type_data: pd.DataFrame) -> float:
        """Calculate effectiveness trend over time"""
        try:
            if len(type_data) < 2:
                return 0
            
            type_data_sorted = type_data.sort_values('date')
            effectiveness_trend = np.polyfit(range(len(type_data_sorted)), type_data_sorted['effectiveness_rating'], 1)[0]
            return round(effectiveness_trend, 3)
            
        except Exception as e:
            logger.error(f"Error calculating effectiveness trend: {str(e)}")
            return 0

    def _assess_skill_mastery(self, type_data: pd.DataFrame) -> str:
        """Assess skill mastery level based on engagement and effectiveness"""
        try:
            avg_engagement = type_data['engagement_score'].mean()
            avg_effectiveness = type_data['effectiveness_rating'].mean()
            completion_rate = (type_data['completion_status'] == 'completed').mean()
            
            if avg_engagement >= 8 and avg_effectiveness >= 8 and completion_rate >= 0.8:
                return 'mastered'
            elif avg_engagement >= 6 and avg_effectiveness >= 6 and completion_rate >= 0.6:
                return 'proficient'
            elif avg_engagement >= 4 and avg_effectiveness >= 4 and completion_rate >= 0.4:
                return 'developing'
            else:
                return 'beginner'
                
        except Exception as e:
            logger.error(f"Error assessing skill mastery: {str(e)}")
            return 'unknown'

    def _analyze_learning_curve(self, type_data: pd.DataFrame) -> Dict:
        """Analyze learning curve for skill development"""
        try:
            if len(type_data) < 3:
                return {'curve_type': 'insufficient_data', 'slope': 0}
            
            type_data_sorted = type_data.sort_values('date')
            
            # Calculate learning curve slope
            x = range(len(type_data_sorted))
            y = type_data_sorted['effectiveness_rating']
            slope = np.polyfit(x, y, 1)[0]
            
            # Determine curve type
            if slope > 0.5:
                curve_type = 'rapid_improvement'
            elif slope > 0.1:
                curve_type = 'steady_improvement'
            elif slope > -0.1:
                curve_type = 'plateau'
            else:
                curve_type = 'declining'
            
            return {
                'curve_type': curve_type,
                'slope': round(slope, 3),
                'data_points': len(type_data_sorted)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning curve: {str(e)}")
            return {'curve_type': 'error', 'slope': 0}

    def _calculate_overall_skill_acquisition(self, skill_development: Dict) -> float:
        """Calculate overall skill acquisition rate"""
        try:
            if not skill_development:
                return 0
            
            total_sessions = sum(skill['total_sessions'] for skill in skill_development.values())
            weighted_completion = sum(
                skill['completion_rate'] * skill['total_sessions'] 
                for skill in skill_development.values()
            )
            
            overall_rate = weighted_completion / total_sessions if total_sessions > 0 else 0
            return round(overall_rate * 100, 1)
            
        except Exception as e:
            logger.error(f"Error calculating overall skill acquisition: {str(e)}")
            return 0

    def _summarize_mastery_levels(self, skill_development: Dict) -> Dict:
        """Summarize mastery levels across all skills"""
        try:
            mastery_counts = {'mastered': 0, 'proficient': 0, 'developing': 0, 'beginner': 0}
            
            for skill_data in skill_development.values():
                mastery_level = skill_data.get('skill_mastery_level', 'unknown')
                if mastery_level in mastery_counts:
                    mastery_counts[mastery_level] += 1
            
            return mastery_counts
            
        except Exception as e:
            logger.error(f"Error summarizing mastery levels: {str(e)}")
            return {}

    def _generate_skill_development_recommendations(self, skill_development: Dict) -> List[str]:
        """Generate recommendations for skill development"""
        recommendations = []
        
        for skill_type, skill_data in skill_development.items():
            mastery_level = skill_data.get('skill_mastery_level', 'unknown')
            
            if mastery_level == 'beginner':
                recommendations.append(f"Focus on basic {skill_type} exercises to build foundation")
            elif mastery_level == 'developing':
                recommendations.append(f"Continue practicing {skill_type} with moderate difficulty")
            elif mastery_level == 'proficient':
                recommendations.append(f"Challenge with advanced {skill_type} exercises")
            elif mastery_level == 'mastered':
                recommendations.append(f"Maintain {skill_type} mastery through regular practice")
        
        return recommendations

    def _assess_crisis_effectiveness(self, success_metrics: Dict) -> str:
        """Assess overall crisis intervention effectiveness"""
        try:
            resolution_rate = success_metrics.get('resolution_rate', 0)
            escalation_rate = success_metrics.get('escalation_rate', 0)
            avg_resolution_time = success_metrics.get('average_resolution_time', 0)
            
            if resolution_rate >= 0.8 and escalation_rate <= 0.2 and avg_resolution_time <= 4:
                return 'excellent'
            elif resolution_rate >= 0.6 and escalation_rate <= 0.4 and avg_resolution_time <= 8:
                return 'good'
            elif resolution_rate >= 0.4 and escalation_rate <= 0.6:
                return 'fair'
            else:
                return 'poor'
                
        except Exception as e:
            logger.error(f"Error assessing crisis effectiveness: {str(e)}")
            return 'unknown'

    def _generate_crisis_recommendations(self, success_metrics: Dict) -> List[str]:
        """Generate recommendations for crisis intervention improvement"""
        recommendations = []
        
        resolution_rate = success_metrics.get('resolution_rate', 0)
        escalation_rate = success_metrics.get('escalation_rate', 0)
        
        if resolution_rate < 0.6:
            recommendations.append("Improve crisis response protocols")
            recommendations.append("Enhance provider notification systems")
        
        if escalation_rate > 0.4:
            recommendations.append("Strengthen crisis prevention measures")
            recommendations.append("Implement early warning systems")
        
        return recommendations

    def _calculate_patient_effectiveness(self, patient_exercises: List) -> float:
        """Calculate effectiveness score for a patient from exercise sessions"""
        try:
            if not patient_exercises:
                return 0
            
            completion_rate = sum(1 for ex in patient_exercises if ex.completion_status == 'completed') / len(patient_exercises)
            engagement_scores = [ex.engagement_score for ex in patient_exercises if ex.engagement_score]
            effectiveness_scores = [ex.effectiveness_rating for ex in patient_exercises if ex.effectiveness_rating]
            
            avg_engagement = np.mean(engagement_scores) if engagement_scores else 5
            avg_effectiveness = np.mean(effectiveness_scores) if effectiveness_scores else 5
            
            # Calculate composite score
            effectiveness_score = (completion_rate * 0.4 + avg_engagement * 0.3 + avg_effectiveness * 0.3) * 10
            return round(effectiveness_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating patient effectiveness: {str(e)}")
            return 0

    def _calculate_patient_effectiveness_from_data(self, exercise_data: List[Dict]) -> float:
        """Calculate effectiveness score from exercise data"""
        try:
            if not exercise_data:
                return 0
            
            completion_rate = sum(1 for ex in exercise_data if ex['completion_status'] == 'completed') / len(exercise_data)
            engagement_scores = [ex['engagement_score'] for ex in exercise_data if ex['engagement_score']]
            effectiveness_scores = [ex['effectiveness_rating'] for ex in exercise_data if ex['effectiveness_rating']]
            
            avg_engagement = np.mean(engagement_scores) if engagement_scores else 5
            avg_effectiveness = np.mean(effectiveness_scores) if effectiveness_scores else 5
            
            effectiveness_score = (completion_rate * 0.4 + avg_engagement * 0.3 + avg_effectiveness * 0.3) * 10
            return round(effectiveness_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating patient effectiveness from data: {str(e)}")
            return 0

    def _calculate_patient_improvement_from_data(self, phq9_data: List[Dict]) -> float:
        """Calculate improvement score from PHQ-9 data"""
        try:
            if len(phq9_data) < 2:
                return 0
            
            initial_score = phq9_data[0]['total_score']
            final_score = phq9_data[-1]['total_score']
            improvement = initial_score - final_score  # Lower score is better
            
            return improvement
            
        except Exception as e:
            logger.error(f"Error calculating patient improvement from data: {str(e)}")
            return 0

    def _calculate_percentile(self, value: float, population_values: List[float]) -> float:
        """Calculate percentile rank of a value in a population"""
        try:
            if not population_values:
                return 50
            
            sorted_values = sorted(population_values)
            rank = sum(1 for x in sorted_values if x <= value)
            percentile = (rank / len(sorted_values)) * 100
            return round(percentile, 1)
            
        except Exception as e:
            logger.error(f"Error calculating percentile: {str(e)}")
            return 50

    def _assess_relative_performance(self, effectiveness: float, improvement: float, population_metrics: Dict) -> str:
        """Assess relative performance compared to population"""
        try:
            avg_effectiveness = population_metrics.get('average_effectiveness', 50)
            avg_improvement = population_metrics.get('average_improvement', 0)
            
            effectiveness_ratio = effectiveness / avg_effectiveness if avg_effectiveness > 0 else 1
            improvement_ratio = improvement / avg_improvement if avg_improvement > 0 else 1
            
            if effectiveness_ratio >= 1.2 and improvement_ratio >= 1.2:
                return 'excellent'
            elif effectiveness_ratio >= 1.0 and improvement_ratio >= 1.0:
                return 'above_average'
            elif effectiveness_ratio >= 0.8 and improvement_ratio >= 0.8:
                return 'average'
            else:
                return 'below_average'
                
        except Exception as e:
            logger.error(f"Error assessing relative performance: {str(e)}")
            return 'unknown'

    def _generate_benchmark_analysis(self, population_metrics: Dict, current_effectiveness: float, current_improvement: float) -> Dict:
        """Generate benchmark analysis for current patient"""
        try:
            avg_effectiveness = population_metrics.get('average_effectiveness', 50)
            avg_improvement = population_metrics.get('average_improvement', 0)
            
            effectiveness_gap = current_effectiveness - avg_effectiveness
            improvement_gap = current_improvement - avg_improvement
            
            return {
                'effectiveness_gap': round(effectiveness_gap, 2),
                'improvement_gap': round(improvement_gap, 2),
                'effectiveness_performance': 'above_average' if effectiveness_gap > 0 else 'below_average',
                'improvement_performance': 'above_average' if improvement_gap > 0 else 'below_average',
                'recommendations': self._generate_benchmark_recommendations(effectiveness_gap, improvement_gap)
            }
            
        except Exception as e:
            logger.error(f"Error generating benchmark analysis: {str(e)}")
            return {'error': f'Benchmark analysis failed: {str(e)}'}

    def _generate_benchmark_recommendations(self, effectiveness_gap: float, improvement_gap: float) -> List[str]:
        """Generate recommendations based on benchmark gaps"""
        recommendations = []
        
        if effectiveness_gap < -10:
            recommendations.append("Focus on improving exercise engagement and completion rates")
        
        if improvement_gap < -2:
            recommendations.append("Review exercise effectiveness and consider treatment adjustments")
        
        if effectiveness_gap > 10 and improvement_gap > 2:
            recommendations.append("Excellent performance - consider sharing best practices")
        
        return recommendations

# Initialize the outcome measurement system
outcome_measurement = OutcomeMeasurement()
