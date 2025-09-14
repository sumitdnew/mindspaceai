#!/usr/bin/env python3
"""
PHQ-9 Exercise Analytics System
Comprehensive analytics connecting PHQ-9 trends with exercise engagement
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
from sqlalchemy import and_, func, desc, extract
from sqlalchemy.orm import joinedload
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from app_ml_complete import (
    db, Patient, PHQ9Assessment, Exercise, ExerciseSession, 
    Activity, ActivityCategory, BehavioralActivationProgress,
    CrisisAlert, RecommendationResult, MoodEntry, MindfulnessSession,
    MicroAssessment, ExerciseStreak
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PHQ9ExerciseAnalytics:
    """Comprehensive analytics system connecting PHQ-9 trends with exercise engagement"""
    
    def __init__(self):
        self.correlation_threshold = 0.3
        self.improvement_threshold = 0.5
        self.engagement_threshold = 0.7
        
    def generate_comprehensive_analytics(self, patient_id: int, time_period_days: int = 90) -> Dict:
        """Generate comprehensive analytics for a patient"""
        try:
            # Get data for analysis period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_period_days)
            
            # Collect all relevant data
            phq9_data = self._get_phq9_data(patient_id, start_date, end_date)
            exercise_data = self._get_exercise_data(patient_id, start_date, end_date)
            mood_data = self._get_mood_data(patient_id, start_date, end_date)
            
            # Generate analytics
            correlation_analysis = self._correlation_analysis_engine(phq9_data, exercise_data, mood_data)
            outcome_measurement = self._outcome_measurement_system(patient_id, phq9_data, exercise_data)
            decision_support = self._provider_decision_support(patient_id, phq9_data, exercise_data, mood_data)
            
            return {
                'patient_id': patient_id,
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days_analyzed': time_period_days
                },
                'correlation_analysis': correlation_analysis,
                'outcome_measurement': outcome_measurement,
                'decision_support': decision_support,
                'summary_insights': self._generate_summary_insights(correlation_analysis, outcome_measurement, decision_support)
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analytics: {str(e)}")
            return {'error': f'Failed to generate analytics: {str(e)}'}

    def _correlation_analysis_engine(self, phq9_data: List[Dict], exercise_data: List[Dict], mood_data: List[Dict]) -> Dict:
        """Track PHQ-9 score changes vs exercise completion rates and identify effective exercises"""
        try:
            # Create time-series dataframes
            phq9_df = pd.DataFrame(phq9_data)
            exercise_df = pd.DataFrame(exercise_data)
            mood_df = pd.DataFrame(mood_data)
            
            if phq9_df.empty or exercise_df.empty:
                return {'error': 'Insufficient data for correlation analysis'}
            
            # 1. PHQ-9 vs Exercise Completion Rate Correlation
            completion_correlation = self._analyze_completion_correlation(phq9_df, exercise_df)
            
            # 2. Exercise Effectiveness Analysis
            exercise_effectiveness = self._identify_effective_exercises(phq9_df, exercise_df)
            
            # 3. Time-to-Improvement Analysis
            time_to_improvement = self._measure_time_to_improvement(phq9_df, exercise_df)
            
            # 4. Predictive Models
            predictive_models = self._generate_predictive_models(phq9_df, exercise_df, mood_df)
            
            return {
                'completion_correlation': completion_correlation,
                'exercise_effectiveness': exercise_effectiveness,
                'time_to_improvement': time_to_improvement,
                'predictive_models': predictive_models
            }
            
        except Exception as e:
            logger.error(f"Error in correlation analysis: {str(e)}")
            return {'error': f'Correlation analysis failed: {str(e)}'}

    def _analyze_completion_correlation(self, phq9_df: pd.DataFrame, exercise_df: pd.DataFrame) -> Dict:
        """Analyze correlation between PHQ-9 scores and exercise completion rates"""
        try:
            # Calculate weekly completion rates
            exercise_df['week'] = pd.to_datetime(exercise_df['date']).dt.isocalendar().week
            weekly_completion = exercise_df.groupby('week').agg({
                'completion_status': lambda x: (x == 'completed').mean(),
                'engagement_score': 'mean',
                'effectiveness_rating': 'mean'
            }).reset_index()
            
            # Calculate weekly PHQ-9 averages
            phq9_df['week'] = pd.to_datetime(phq9_df['assessment_date']).dt.isocalendar().week
            weekly_phq9 = phq9_df.groupby('week')['total_score'].mean().reset_index()
            
            # Merge data
            correlation_data = pd.merge(weekly_completion, weekly_phq9, on='week', how='inner')
            
            if len(correlation_data) < 2:
                return {'error': 'Insufficient data for correlation analysis'}
            
            # Calculate correlations
            correlations = {
                'completion_rate_vs_phq9': np.corrcoef(correlation_data['completion_status'], correlation_data['total_score'])[0,1],
                'engagement_vs_phq9': np.corrcoef(correlation_data['engagement_score'], correlation_data['total_score'])[0,1],
                'effectiveness_vs_phq9': np.corrcoef(correlation_data['effectiveness_rating'], correlation_data['total_score'])[0,1]
            }
            
            # Determine correlation strength
            correlation_insights = {}
            for key, value in correlations.items():
                if abs(value) > 0.7:
                    strength = 'strong'
                elif abs(value) > 0.3:
                    strength = 'moderate'
                else:
                    strength = 'weak'
                
                correlation_insights[key] = {
                    'correlation_coefficient': round(value, 3),
                    'strength': strength,
                    'interpretation': self._interpret_correlation(key, value)
                }
            
            return {
                'correlations': correlation_insights,
                'data_points': len(correlation_data),
                'trend_analysis': self._analyze_trends(correlation_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing completion correlation: {str(e)}")
            return {'error': f'Completion correlation analysis failed: {str(e)}'}

    def _identify_effective_exercises(self, phq9_df: pd.DataFrame, exercise_df: pd.DataFrame) -> Dict:
        """Identify which exercises are most effective for PHQ-9 score improvement"""
        try:
            # Group exercises by type and calculate effectiveness
            exercise_effectiveness = {}
            
            for exercise_type in exercise_df['exercise_type'].unique():
                type_data = exercise_df[exercise_df['exercise_type'] == exercise_type]
                
                if len(type_data) < 3:  # Need minimum data points
                    continue
                
                # Calculate effectiveness metrics
                completion_rate = (type_data['completion_status'] == 'completed').mean()
                avg_engagement = type_data['engagement_score'].mean()
                avg_effectiveness = type_data['effectiveness_rating'].mean()
                
                # Calculate PHQ-9 improvement correlation
                phq9_improvement = self._calculate_phq9_improvement_correlation(phq9_df, type_data)
                
                exercise_effectiveness[exercise_type] = {
                    'completion_rate': round(completion_rate, 3),
                    'avg_engagement': round(avg_engagement, 2),
                    'avg_effectiveness': round(avg_effectiveness, 2),
                    'phq9_improvement_correlation': phq9_improvement,
                    'total_sessions': len(type_data),
                    'effectiveness_score': self._calculate_effectiveness_score(
                        completion_rate, avg_engagement, avg_effectiveness, phq9_improvement
                    )
                }
            
            # Sort by effectiveness score
            sorted_exercises = sorted(
                exercise_effectiveness.items(), 
                key=lambda x: x[1]['effectiveness_score'], 
                reverse=True
            )
            
            return {
                'exercise_rankings': dict(sorted_exercises),
                'top_performing_exercises': sorted_exercises[:3],
                'recommendations': self._generate_exercise_recommendations(sorted_exercises)
            }
            
        except Exception as e:
            logger.error(f"Error identifying effective exercises: {str(e)}")
            return {'error': f'Exercise effectiveness analysis failed: {str(e)}'}

    def _measure_time_to_improvement(self, phq9_df: pd.DataFrame, exercise_df: pd.DataFrame) -> Dict:
        """Measure time-to-improvement based on exercise adherence"""
        try:
            # Find periods of consistent exercise adherence
            exercise_df['date'] = pd.to_datetime(exercise_df['date'])
            exercise_df = exercise_df.sort_values('date')
            
            # Calculate rolling completion rates
            exercise_df['rolling_completion'] = exercise_df['completion_status'].rolling(
                window=7, min_periods=1
            ).apply(lambda x: (x == 'completed').mean())
            
            # Identify high adherence periods (>70% completion for 7+ days)
            high_adherence_periods = exercise_df[exercise_df['rolling_completion'] >= 0.7]
            
            if len(high_adherence_periods) == 0:
                return {'error': 'No high adherence periods found'}
            
            # Calculate PHQ-9 improvements during these periods
            improvements = []
            for _, period in high_adherence_periods.groupby(high_adherence_periods.index // 7):
                if len(period) >= 7:  # At least 7 days of high adherence
                    period_start = period['date'].min()
                    period_end = period['date'].max()
                    
                    # Get PHQ-9 scores before and after the period
                    before_scores = phq9_df[phq9_df['assessment_date'] < period_start]['total_score'].tail(2)
                    after_scores = phq9_df[phq9_df['assessment_date'] > period_end]['total_score'].head(2)
                    
                    if len(before_scores) > 0 and len(after_scores) > 0:
                        before_avg = before_scores.mean()
                        after_avg = after_scores.mean()
                        improvement = before_avg - after_avg
                        
                        if improvement > 0:  # Lower score is better
                            improvements.append({
                                'period_start': period_start.isoformat(),
                                'period_end': period_end.isoformat(),
                                'days_of_adherence': len(period),
                                'improvement': round(improvement, 2),
                                'before_score': round(before_avg, 2),
                                'after_score': round(after_avg, 2)
                            })
            
            if not improvements:
                return {'message': 'No significant improvements detected during high adherence periods'}
            
            # Calculate average time to improvement
            avg_days_to_improvement = np.mean([imp['days_of_adherence'] for imp in improvements])
            avg_improvement = np.mean([imp['improvement'] for imp in improvements])
            
            return {
                'improvement_periods': improvements,
                'average_days_to_improvement': round(avg_days_to_improvement, 1),
                'average_improvement': round(avg_improvement, 2),
                'total_improvement_periods': len(improvements),
                'recommendations': self._generate_improvement_recommendations(improvements)
            }
            
        except Exception as e:
            logger.error(f"Error measuring time to improvement: {str(e)}")
            return {'error': f'Time to improvement analysis failed: {str(e)}'}

    def _generate_predictive_models(self, phq9_df: pd.DataFrame, exercise_df: pd.DataFrame, mood_df: pd.DataFrame) -> Dict:
        """Generate predictive models for treatment response"""
        try:
            # Prepare features for prediction
            features = self._prepare_prediction_features(phq9_df, exercise_df, mood_df)
            
            if len(features) < 10:  # Need sufficient data
                return {'error': 'Insufficient data for predictive modeling'}
            
            # Split features and target
            X = features.drop(['next_phq9_score', 'improvement'], axis=1, errors='ignore')
            y_phq9 = features['next_phq9_score']
            y_improvement = features['improvement']
            
            # Train models
            phq9_model = self._train_phq9_prediction_model(X, y_phq9)
            improvement_model = self._train_improvement_prediction_model(X, y_improvement)
            
            # Feature importance analysis
            feature_importance = self._analyze_feature_importance(improvement_model, X.columns)
            
            return {
                'phq9_prediction_model': phq9_model,
                'improvement_prediction_model': improvement_model,
                'feature_importance': feature_importance,
                'model_performance': self._evaluate_model_performance(phq9_model, improvement_model, X, y_phq9, y_improvement)
            }
            
        except Exception as e:
            logger.error(f"Error generating predictive models: {str(e)}")
            return {'error': f'Predictive modeling failed: {str(e)}'}

    def _outcome_measurement_system(self, patient_id: int, phq9_data: List[Dict], exercise_data: List[Dict]) -> Dict:
        """Calculate comprehensive outcome measurements"""
        try:
            # 1. Exercise Effectiveness Score
            effectiveness_score = self._calculate_exercise_effectiveness_score(patient_id, exercise_data)
            
            # 2. Skill Acquisition Rates
            skill_acquisition = self._measure_skill_acquisition_rates(patient_id, exercise_data)
            
            # 3. Crisis Intervention Success Rates
            crisis_success = self._track_crisis_intervention_success(patient_id)
            
            # 4. Population-level Effectiveness Reports
            population_effectiveness = self._generate_population_effectiveness_report(patient_id, phq9_data, exercise_data)
            
            return {
                'effectiveness_score': effectiveness_score,
                'skill_acquisition': skill_acquisition,
                'crisis_intervention_success': crisis_success,
                'population_effectiveness': population_effectiveness
            }
            
        except Exception as e:
            logger.error(f"Error in outcome measurement: {str(e)}")
            return {'error': f'Outcome measurement failed: {str(e)}'}

    def _provider_decision_support(self, patient_id: int, phq9_data: List[Dict], exercise_data: List[Dict], mood_data: List[Dict]) -> Dict:
        """Provide comprehensive decision support for providers"""
        try:
            # 1. PHQ-9 Reassessment Timing
            reassessment_timing = self._recommend_phq9_reassessment_timing(patient_id, phq9_data, exercise_data)
            
            # 2. Treatment Intensification Recommendations
            intensification_recommendations = self._suggest_treatment_intensification(patient_id, phq9_data, exercise_data, mood_data)
            
            # 3. Medication Evaluation Alerts
            medication_alerts = self._alert_medication_evaluation(patient_id, phq9_data, exercise_data)
            
            # 4. Insurance/Outcome Reporting Evidence
            outcome_evidence = self._generate_outcome_evidence(patient_id, phq9_data, exercise_data)
            
            return {
                'reassessment_timing': reassessment_timing,
                'intensification_recommendations': intensification_recommendations,
                'medication_alerts': medication_alerts,
                'outcome_evidence': outcome_evidence
            }
            
        except Exception as e:
            logger.error(f"Error in provider decision support: {str(e)}")
            return {'error': f'Decision support generation failed: {str(e)}'}

    # Helper methods for data collection
    def _get_phq9_data(self, patient_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get PHQ-9 assessment data for analysis period"""
        try:
            assessments = PHQ9Assessment.query.filter(
                and_(
                    PHQ9Assessment.patient_id == patient_id,
                    PHQ9Assessment.assessment_date >= start_date,
                    PHQ9Assessment.assessment_date <= end_date
                )
            ).order_by(PHQ9Assessment.assessment_date).all()
            
            return [{
                'assessment_date': assessment.assessment_date,
                'total_score': assessment.total_score,
                'severity_level': assessment.severity_level,
                'q9_risk_flag': assessment.q9_risk_flag,
                'q1_score': assessment.q1_score,
                'q2_score': assessment.q2_score,
                'q3_score': assessment.q3_score,
                'q4_score': assessment.q4_score,
                'q5_score': assessment.q5_score,
                'q6_score': assessment.q6_score,
                'q7_score': assessment.q7_score,
                'q8_score': assessment.q8_score,
                'q9_score': assessment.q9_score
            } for assessment in assessments]
            
        except Exception as e:
            logger.error(f"Error getting PHQ-9 data: {str(e)}")
            return []

    def _get_exercise_data(self, patient_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get exercise session data for analysis period"""
        try:
            sessions = ExerciseSession.query.filter(
                and_(
                    ExerciseSession.patient_id == patient_id,
                    ExerciseSession.start_time >= start_date,
                    ExerciseSession.start_time <= end_date
                )
            ).join(Exercise).order_by(ExerciseSession.start_time).all()
            
            return [{
                'date': session.start_time,
                'exercise_type': session.exercise.type,
                'exercise_name': session.exercise.name,
                'completion_status': session.completion_status,
                'engagement_score': session.engagement_score,
                'effectiveness_rating': session.effectiveness_rating,
                'duration': (session.completion_time - session.start_time).total_seconds() / 60 if session.completion_time else None,
                'collected_data': session.collected_data
            } for session in sessions]
            
        except Exception as e:
            logger.error(f"Error getting exercise data: {str(e)}")
            return []

    def _get_mood_data(self, patient_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get mood entry data for analysis period"""
        try:
            mood_entries = MoodEntry.query.filter(
                and_(
                    MoodEntry.patient_id == patient_id,
                    MoodEntry.timestamp >= start_date,
                    MoodEntry.timestamp <= end_date
                )
            ).order_by(MoodEntry.timestamp).all()
            
            return [{
                'timestamp': entry.timestamp,
                'mood_score': entry.intensity_level,
                'energy_level': entry.energy_level,
                'sleep_quality': entry.sleep_quality,
                'social_context': entry.social_context,
                'notes': entry.notes_brief
            } for entry in mood_entries]
            
        except Exception as e:
            logger.error(f"Error getting mood data: {str(e)}")
            return []

    def _interpret_correlation(self, key: str, value: float) -> str:
        """Interpret correlation coefficient"""
        if 'completion_rate' in key:
            if value < -0.3:
                return "Higher exercise completion associated with lower PHQ-9 scores (better outcomes)"
            elif value > 0.3:
                return "Higher exercise completion associated with higher PHQ-9 scores (concerning)"
            else:
                return "No clear relationship between exercise completion and PHQ-9 scores"
        else:
            return f"Correlation coefficient: {value:.3f}"

    def _calculate_effectiveness_score(self, completion_rate: float, engagement: float, effectiveness: float, phq9_correlation: float) -> float:
        """Calculate overall effectiveness score"""
        # Normalize all components to 0-100 scale
        completion_norm = completion_rate * 100
        engagement_norm = engagement * 10
        effectiveness_norm = effectiveness * 10
        correlation_norm = max(0, 100 - abs(phq9_correlation) * 100)  # Lower correlation is better
        
        # Weighted average
        return (completion_norm * 0.3 + engagement_norm * 0.3 + effectiveness_norm * 0.3 + correlation_norm * 0.1)

    def _generate_summary_insights(self, correlation_analysis: Dict, outcome_measurement: Dict, decision_support: Dict) -> Dict:
        """Generate summary insights from all analytics"""
        try:
            insights = {
                'key_findings': [],
                'recommendations': [],
                'risk_factors': [],
                'positive_indicators': []
            }
            
            # Extract key findings from correlation analysis
            if 'correlation_analysis' in correlation_analysis and 'completion_correlation' in correlation_analysis['correlation_analysis']:
                corr_data = correlation_analysis['correlation_analysis']['completion_correlation']
                if 'correlations' in corr_data:
                    for key, value in corr_data['correlations'].items():
                        if value['strength'] in ['strong', 'moderate']:
                            insights['key_findings'].append(f"Strong correlation found: {key} ({value['correlation_coefficient']})")
            
            # Extract recommendations from decision support
            if 'decision_support' in decision_support:
                if 'reassessment_timing' in decision_support['decision_support']:
                    timing = decision_support['decision_support']['reassessment_timing']
                    if 'recommended_timing' in timing:
                        insights['recommendations'].append(f"Schedule PHQ-9 reassessment in {timing['recommended_timing']}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating summary insights: {str(e)}")
            return {'error': f'Summary insights generation failed: {str(e)}'}

# Initialize the analytics system
phq9_exercise_analytics = PHQ9ExerciseAnalytics()
