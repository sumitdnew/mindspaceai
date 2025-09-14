#!/usr/bin/env python3
"""
Provider Decision Support System
Comprehensive decision support for providers including reassessment timing, treatment intensification, and medication alerts
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
    CrisisAlert, MoodEntry, MindfulnessSession
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProviderDecisionSupport:
    """Comprehensive decision support system for healthcare providers"""
    
    def __init__(self):
        self.reassessment_thresholds = {
            'immediate': {'score_change': 5, 'completion_rate': 0.3},
            'urgent': {'score_change': 3, 'completion_rate': 0.5},
            'standard': {'score_change': 2, 'completion_rate': 0.7},
            'extended': {'score_change': 1, 'completion_rate': 0.8}
        }
        
    def recommend_phq9_reassessment_timing(self, patient_id: int, phq9_data: List[Dict], exercise_data: List[Dict]) -> Dict:
        """Recommend optimal PHQ-9 reassessment timing based on exercise progress"""
        try:
            if not phq9_data or not exercise_data:
                return {'recommendation': 'Schedule reassessment in 2 weeks', 'reason': 'Insufficient data for analysis'}
            
            # Analyze recent trends
            recent_phq9 = sorted(phq9_data, key=lambda x: x['assessment_date'])[-2:]
            recent_exercises = sorted(exercise_data, key=lambda x: x['date'])[-14:]  # Last 2 weeks
            
            if len(recent_phq9) < 2 or len(recent_exercises) < 7:
                return {'recommendation': 'Schedule reassessment in 2 weeks', 'reason': 'Insufficient recent data'}
            
            # Calculate exercise engagement trend
            completion_rate = sum(1 for ex in recent_exercises if ex['completion_status'] == 'completed') / len(recent_exercises)
            engagement_trend = self._calculate_engagement_trend(pd.DataFrame(recent_exercises))
            
            # Calculate PHQ-9 trend
            phq9_trend = recent_phq9[-1]['total_score'] - recent_phq9[0]['total_score']
            
            # Determine reassessment timing
            if phq9_trend < -2 and completion_rate > 0.8:  # Improving with high engagement
                timing = '1 week'
                reason = 'Significant improvement detected with high exercise engagement'
            elif phq9_trend > 2 or completion_rate < 0.3:  # Declining or low engagement
                timing = '1 week'
                reason = 'Concerning trends detected - immediate reassessment recommended'
            elif abs(phq9_trend) <= 2 and 0.3 <= completion_rate <= 0.8:  # Stable with moderate engagement
                timing = '2 weeks'
                reason = 'Stable condition with moderate engagement - standard reassessment timing'
            else:
                timing = '3 weeks'
                reason = 'Good progress with consistent engagement - extended reassessment timing'
            
            return {
                'recommended_timing': timing,
                'reasoning': reason,
                'confidence_level': self._calculate_timing_confidence(phq9_trend, completion_rate, engagement_trend),
                'supporting_data': {
                    'phq9_trend': phq9_trend,
                    'completion_rate': round(completion_rate, 3),
                    'engagement_trend': engagement_trend
                }
            }
            
        except Exception as e:
            logger.error(f"Error recommending reassessment timing: {str(e)}")
            return {'error': f'Reassessment timing recommendation failed: {str(e)}'}

    def suggest_treatment_intensification(self, patient_id: int, phq9_data: List[Dict], exercise_data: List[Dict], mood_data: List[Dict]) -> Dict:
        """Suggest treatment intensification based on engagement patterns"""
        try:
            # Analyze current engagement patterns
            engagement_analysis = self._analyze_engagement_patterns(exercise_data)
            
            # Analyze mood trends
            mood_trends = self._analyze_mood_trends_from_data(mood_data)
            
            # Analyze PHQ-9 progression
            phq9_progression = self._analyze_phq9_progression(phq9_data)
            
            recommendations = []
            urgency_level = 'low'
            
            # Check for concerning patterns
            if engagement_analysis.get('completion_rate', 0) < 0.4:
                recommendations.append({
                    'type': 'increase_exercise_frequency',
                    'urgency': 'high',
                    'reason': 'Low exercise completion rate indicates need for more intensive intervention',
                    'specific_action': 'Increase daily exercise frequency and add motivational support'
                })
                urgency_level = 'high'
            
            if mood_trends.get('trend') == 'declining':
                recommendations.append({
                    'type': 'add_crisis_monitoring',
                    'urgency': 'medium',
                    'reason': 'Declining mood trends detected',
                    'specific_action': 'Add daily mood monitoring and crisis intervention exercises'
                })
                urgency_level = max(urgency_level, 'medium')
            
            if phq9_progression.get('recent_trend', 0) > 3:
                recommendations.append({
                    'type': 'provider_consultation',
                    'urgency': 'high',
                    'reason': 'Significant PHQ-9 score increase detected',
                    'specific_action': 'Schedule immediate provider consultation for treatment adjustment'
                })
                urgency_level = 'high'
            
            # Check for positive patterns that might allow de-escalation
            if (engagement_analysis.get('completion_rate', 0) > 0.8 and 
                mood_trends.get('trend') == 'improving' and 
                phq9_progression.get('recent_trend', 0) < -2):
                recommendations.append({
                    'type': 'maintain_current_level',
                    'urgency': 'low',
                    'reason': 'Excellent progress with high engagement and improving mood',
                    'specific_action': 'Maintain current exercise regimen and monitor for continued improvement'
                })
            
            return {
                'recommendations': recommendations,
                'urgency_level': urgency_level,
                'supporting_evidence': {
                    'engagement_analysis': engagement_analysis,
                    'mood_trends': mood_trends,
                    'phq9_progression': phq9_progression
                }
            }
            
        except Exception as e:
            logger.error(f"Error suggesting treatment intensification: {str(e)}")
            return {'error': f'Treatment intensification recommendation failed: {str(e)}'}

    def alert_medication_evaluation(self, patient_id: int, phq9_data: List[Dict], exercise_data: List[Dict]) -> Dict:
        """Alert for patients likely to need medication evaluation"""
        try:
            alerts = []
            
            # Analyze recent PHQ-9 scores
            recent_phq9 = sorted(phq9_data, key=lambda x: x['assessment_date'])[-3:]
            
            if len(recent_phq9) >= 2:
                # Check for persistent high scores
                high_scores = [p for p in recent_phq9 if p['total_score'] >= 15]
                if len(high_scores) >= 2:
                    alerts.append({
                        'type': 'persistent_high_scores',
                        'severity': 'high',
                        'description': f'Patient has maintained high PHQ-9 scores ({len(high_scores)} assessments ≥15)',
                        'recommendation': 'Consider medication evaluation for persistent moderate-severe depression'
                    })
                
                # Check for worsening despite exercise engagement
                if len(recent_phq9) >= 2:
                    score_change = recent_phq9[-1]['total_score'] - recent_phq9[0]['total_score']
                    if score_change > 3:  # Worsening by 3+ points
                        recent_exercises = [ex for ex in exercise_data if ex['date'] >= recent_phq9[0]['assessment_date']]
                        completion_rate = sum(1 for ex in recent_exercises if ex['completion_status'] == 'completed') / len(recent_exercises) if recent_exercises else 0
                        
                        if completion_rate > 0.6:  # Good exercise engagement
                            alerts.append({
                                'type': 'worsening_despite_engagement',
                                'severity': 'medium',
                                'description': f'PHQ-9 score increased by {score_change} points despite {completion_rate*100:.1f}% exercise completion',
                                'recommendation': 'Consider medication evaluation as exercise therapy may be insufficient'
                            })
            
            # Check for crisis indicators
            crisis_alerts = CrisisAlert.query.filter_by(patient_id=patient_id).order_by(CrisisAlert.created_at.desc()).limit(5).all()
            recent_crises = [alert for alert in crisis_alerts if (datetime.utcnow() - alert.created_at).days <= 30]
            
            if len(recent_crises) >= 3:
                alerts.append({
                    'type': 'frequent_crises',
                    'severity': 'high',
                    'description': f'Patient has experienced {len(recent_crises)} crisis events in the past 30 days',
                    'recommendation': 'Urgent medication evaluation recommended for crisis management'
                })
            
            return {
                'alerts': alerts,
                'total_alerts': len(alerts),
                'highest_severity': max([alert['severity'] for alert in alerts], default='none'),
                'summary': self._summarize_medication_alerts(alerts)
            }
            
        except Exception as e:
            logger.error(f"Error alerting medication evaluation: {str(e)}")
            return {'error': f'Medication evaluation alerting failed: {str(e)}'}

    def generate_outcome_evidence(self, patient_id: int, phq9_data: List[Dict], exercise_data: List[Dict]) -> Dict:
        """Generate evidence for insurance/outcome reporting"""
        try:
            if not phq9_data or not exercise_data:
                return {'error': 'Insufficient data for outcome evidence generation'}
            
            # Calculate key outcome metrics
            initial_score = phq9_data[0]['total_score'] if phq9_data else None
            final_score = phq9_data[-1]['total_score'] if phq9_data else None
            total_sessions = len(exercise_data)
            completion_rate = sum(1 for ex in exercise_data if ex['completion_status'] == 'completed') / len(exercise_data)
            
            # Calculate improvement metrics
            improvement_metrics = {}
            if initial_score is not None and final_score is not None:
                score_improvement = initial_score - final_score
                percent_improvement = (score_improvement / initial_score) * 100 if initial_score > 0 else 0
                
                improvement_metrics = {
                    'absolute_improvement': score_improvement,
                    'percent_improvement': round(percent_improvement, 1),
                    'clinical_significance': self._assess_clinical_significance(score_improvement),
                    'severity_change': self._assess_severity_change(initial_score, final_score)
                }
            
            # Generate outcome report
            outcome_report = {
                'patient_identifier': patient_id,
                'treatment_period': {
                    'start_date': phq9_data[0]['assessment_date'] if phq9_data else None,
                    'end_date': phq9_data[-1]['assessment_date'] if phq9_data else None,
                    'duration_weeks': len(phq9_data) if phq9_data else 0
                },
                'intervention_summary': {
                    'total_exercise_sessions': total_sessions,
                    'completion_rate': round(completion_rate * 100, 1),
                    'average_engagement': round(np.mean([ex['engagement_score'] for ex in exercise_data if ex['engagement_score']]), 2),
                    'average_effectiveness': round(np.mean([ex['effectiveness_rating'] for ex in exercise_data if ex['effectiveness_rating']]), 2)
                },
                'outcome_metrics': improvement_metrics,
                'evidence_strength': self._assess_evidence_strength(phq9_data, exercise_data),
                'recommendations_for_continued_care': self._generate_continued_care_recommendations(improvement_metrics, completion_rate)
            }
            
            return outcome_report
            
        except Exception as e:
            logger.error(f"Error generating outcome evidence: {str(e)}")
            return {'error': f'Outcome evidence generation failed: {str(e)}'}

    # Helper methods
    def _calculate_engagement_trend(self, df: pd.DataFrame) -> float:
        """Calculate engagement trend over time"""
        try:
            if len(df) < 2:
                return 0
            
            df_sorted = df.sort_values('date')
            engagement_trend = np.polyfit(range(len(df_sorted)), df_sorted['engagement_score'], 1)[0]
            return round(engagement_trend, 3)
            
        except Exception as e:
            logger.error(f"Error calculating engagement trend: {str(e)}")
            return 0

    def _calculate_timing_confidence(self, phq9_trend: float, completion_rate: float, engagement_trend: float) -> str:
        """Calculate confidence level for timing recommendation"""
        try:
            # Factors that increase confidence
            confidence_factors = 0
            
            if abs(phq9_trend) > 3:
                confidence_factors += 1
            if completion_rate > 0.8 or completion_rate < 0.3:
                confidence_factors += 1
            if abs(engagement_trend) > 0.5:
                confidence_factors += 1
            
            if confidence_factors >= 2:
                return 'high'
            elif confidence_factors >= 1:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error calculating timing confidence: {str(e)}")
            return 'low'

    def _analyze_engagement_patterns(self, exercise_data: List[Dict]) -> Dict:
        """Analyze exercise engagement patterns"""
        try:
            if not exercise_data:
                return {'completion_rate': 0, 'engagement_level': 'none'}
            
            completed = sum(1 for ex in exercise_data if ex['completion_status'] == 'completed')
            completion_rate = completed / len(exercise_data)
            
            engagement_scores = [ex['engagement_score'] for ex in exercise_data if ex['engagement_score']]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
            
            if completion_rate > 0.8 and avg_engagement > 7:
                engagement_level = 'high'
            elif completion_rate > 0.5 and avg_engagement > 5:
                engagement_level = 'moderate'
            else:
                engagement_level = 'low'
            
            return {
                'completion_rate': completion_rate,
                'average_engagement': avg_engagement,
                'engagement_level': engagement_level,
                'total_sessions': len(exercise_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing engagement patterns: {str(e)}")
            return {'completion_rate': 0, 'engagement_level': 'error'}

    def _analyze_mood_trends_from_data(self, mood_data: List[Dict]) -> Dict:
        """Analyze mood trends from mood data"""
        try:
            if not mood_data:
                return {'trend': 'insufficient_data'}
            
            mood_scores = [entry['mood_score'] for entry in mood_data]
            
            # Calculate trend
            if len(mood_scores) >= 7:
                recent_avg = sum(mood_scores[-7:]) / 7
                previous_avg = sum(mood_scores[-14:-7]) / 7 if len(mood_scores) >= 14 else mood_scores[0]
                
                if recent_avg < previous_avg:
                    trend = 'improving'
                elif recent_avg > previous_avg:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            return {
                'trend': trend,
                'total_entries': len(mood_scores)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing mood trends: {str(e)}")
            return {'trend': 'error'}

    def _analyze_phq9_progression(self, phq9_data: List[Dict]) -> Dict:
        """Analyze PHQ-9 score progression"""
        try:
            if len(phq9_data) < 2:
                return {'recent_trend': 0, 'overall_trend': 0}
            
            # Recent trend (last 2 assessments)
            recent_trend = phq9_data[-1]['total_score'] - phq9_data[-2]['total_score']
            
            # Overall trend (first to last)
            overall_trend = phq9_data[-1]['total_score'] - phq9_data[0]['total_score']
            
            return {
                'recent_trend': recent_trend,
                'overall_trend': overall_trend,
                'total_assessments': len(phq9_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing PHQ-9 progression: {str(e)}")
            return {'recent_trend': 0, 'overall_trend': 0}

    def _summarize_medication_alerts(self, alerts: List[Dict]) -> Dict:
        """Summarize medication alerts"""
        try:
            if not alerts:
                return {'summary': 'No medication evaluation alerts'}
            
            severity_counts = {'high': 0, 'medium': 0, 'low': 0}
            type_counts = {}
            
            for alert in alerts:
                severity = alert.get('severity', 'low')
                alert_type = alert.get('type', 'unknown')
                
                severity_counts[severity] += 1
                type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
            
            return {
                'total_alerts': len(alerts),
                'severity_distribution': severity_counts,
                'type_distribution': type_counts,
                'highest_priority': 'high' if severity_counts['high'] > 0 else 'medium' if severity_counts['medium'] > 0 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error summarizing medication alerts: {str(e)}")
            return {'error': f'Alert summarization failed: {str(e)}'}

    def _assess_clinical_significance(self, score_improvement: float) -> str:
        """Assess clinical significance of PHQ-9 improvement"""
        try:
            if score_improvement >= 5:
                return 'clinically_significant'
            elif score_improvement >= 3:
                return 'moderate_improvement'
            elif score_improvement >= 1:
                return 'minimal_improvement'
            elif score_improvement >= -1:
                return 'no_change'
            else:
                return 'worsening'
                
        except Exception as e:
            logger.error(f"Error assessing clinical significance: {str(e)}")
            return 'unknown'

    def _assess_severity_change(self, initial_score: float, final_score: float) -> str:
        """Assess change in depression severity"""
        try:
            initial_severity = self._get_severity_level(initial_score)
            final_severity = self._get_severity_level(final_score)
            
            severity_levels = ['minimal', 'mild', 'moderate', 'moderately_severe', 'severe']
            
            initial_index = severity_levels.index(initial_severity)
            final_index = severity_levels.index(final_severity)
            
            change = final_index - initial_index
            
            if change < 0:
                return 'improved_severity'
            elif change > 0:
                return 'worsened_severity'
            else:
                return 'no_severity_change'
                
        except Exception as e:
            logger.error(f"Error assessing severity change: {str(e)}")
            return 'unknown'

    def _get_severity_level(self, total_score: float) -> str:
        """Determine severity level from PHQ-9 total score"""
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

    def _assess_evidence_strength(self, phq9_data: List[Dict], exercise_data: List[Dict]) -> str:
        """Assess strength of evidence for outcome reporting"""
        try:
            # Factors that increase evidence strength
            evidence_factors = 0
            
            # Multiple PHQ-9 assessments
            if len(phq9_data) >= 3:
                evidence_factors += 1
            
            # Consistent exercise engagement
            if len(exercise_data) >= 10:
                evidence_factors += 1
            
            # High completion rate
            completion_rate = sum(1 for ex in exercise_data if ex['completion_status'] == 'completed') / len(exercise_data)
            if completion_rate >= 0.7:
                evidence_factors += 1
            
            # Regular assessment intervals
            if len(phq9_data) >= 2:
                intervals = []
                for i in range(1, len(phq9_data)):
                    interval = (phq9_data[i]['assessment_date'] - phq9_data[i-1]['assessment_date']).days
                    intervals.append(interval)
                
                avg_interval = np.mean(intervals)
                if 7 <= avg_interval <= 28:  # Weekly to monthly intervals
                    evidence_factors += 1
            
            if evidence_factors >= 3:
                return 'strong'
            elif evidence_factors >= 2:
                return 'moderate'
            else:
                return 'weak'
                
        except Exception as e:
            logger.error(f"Error assessing evidence strength: {str(e)}")
            return 'unknown'

    def _generate_continued_care_recommendations(self, improvement_metrics: Dict, completion_rate: float) -> List[str]:
        """Generate recommendations for continued care"""
        try:
            recommendations = []
            
            if not improvement_metrics:
                recommendations.append("Continue current treatment plan with regular monitoring")
                return recommendations
            
            clinical_significance = improvement_metrics.get('clinical_significance', 'unknown')
            percent_improvement = improvement_metrics.get('percent_improvement', 0)
            
            if clinical_significance == 'clinically_significant':
                recommendations.append("Consider tapering exercise frequency while maintaining monitoring")
                recommendations.append("Schedule follow-up PHQ-9 assessment in 4-6 weeks")
            elif clinical_significance == 'moderate_improvement':
                recommendations.append("Continue current exercise regimen with monthly reassessment")
                recommendations.append("Consider adding complementary interventions")
            elif clinical_significance == 'minimal_improvement':
                recommendations.append("Review and potentially intensify exercise program")
                recommendations.append("Consider additional therapeutic modalities")
            else:
                recommendations.append("Re-evaluate treatment approach and consider alternatives")
                recommendations.append("Schedule provider consultation for treatment adjustment")
            
            if completion_rate < 0.6:
                recommendations.append("Focus on improving exercise adherence and engagement")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating continued care recommendations: {str(e)}")
            return ["Continue current treatment plan with regular monitoring"]

# Initialize the provider decision support system
provider_decision_support = ProviderDecisionSupport()
