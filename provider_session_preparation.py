#!/usr/bin/env python3
"""
Provider Session Preparation System
Generates pre-session intelligence briefs and session-specific talking points
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import numpy as np
from sqlalchemy import func, and_, desc, extract
from collections import defaultdict
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

# Import database models
from app_ml_complete import (
    db, Patient, PHQ9Assessment, ExerciseSession, MoodEntry, 
    CrisisAlert, MindfulnessSession, MicroAssessment, ThoughtRecord
)

session_preparation = Blueprint('session_preparation', __name__)

class ProviderSessionPreparationSystem:
    """Provider session preparation system"""
    
    def __init__(self):
        self.analysis_periods = {
            'week': 7,
            'month': 30,
            'quarter': 90
        }
    
    def generate_pre_session_brief(self, patient_id: int) -> Dict[str, Any]:
        """Generate comprehensive pre-session intelligence brief"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Get week-at-a-glance data
            week_overview = self._get_week_at_a_glance(patient_id)
            
            # Get key concerns
            key_concerns = self._identify_key_concerns(patient_id)
            
            # Get progress highlights
            progress_highlights = self._get_progress_highlights(patient_id)
            
            # Get suggested session focus
            session_focus = self._suggest_session_focus(patient_id)
            
            # Get treatment plan updates
            treatment_updates = self._get_treatment_plan_updates(patient_id)
            
            return {
                'patient_info': {
                    'id': patient.id,
                    'name': f"{patient.first_name} {patient.last_name}",
                    'current_severity': patient.current_phq9_severity,
                    'last_session': self._get_last_session_date(patient_id)
                },
                'week_at_a_glance': week_overview,
                'key_concerns': key_concerns,
                'progress_highlights': progress_highlights,
                'suggested_session_focus': session_focus,
                'treatment_plan_updates': treatment_updates,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating pre-session brief: {str(e)}")
            return {'error': f'Failed to generate pre-session brief: {str(e)}'}
    
    def generate_session_talking_points(self, patient_id: int) -> Dict[str, Any]:
        """Generate session-specific talking points"""
        try:
            # Analyze recent patterns
            mood_patterns = self._analyze_mood_patterns_for_talking_points(patient_id)
            exercise_patterns = self._analyze_exercise_patterns_for_talking_points(patient_id)
            cbt_patterns = self._analyze_cbt_patterns_for_talking_points(patient_id)
            crisis_patterns = self._analyze_crisis_patterns_for_talking_points(patient_id)
            
            # Generate talking points
            talking_points = self._generate_talking_points(
                patient_id, mood_patterns, exercise_patterns, cbt_patterns, crisis_patterns
            )
            
            return {
                'mood_focused_points': talking_points['mood'],
                'exercise_focused_points': talking_points['exercise'],
                'cbt_focused_points': talking_points['cbt'],
                'crisis_focused_points': talking_points['crisis'],
                'general_points': talking_points['general'],
                'evidence_basis': talking_points['evidence'],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating talking points: {str(e)}")
            return {'error': f'Failed to generate talking points: {str(e)}'}
    
    def generate_evidence_based_session_plan(self, patient_id: int) -> Dict[str, Any]:
        """Generate evidence-based session planning"""
        try:
            # Get correlation data
            correlations = self._get_correlation_data(patient_id)
            
            # Get pattern recognition
            patterns = self._get_pattern_recognition(patient_id)
            
            # Get skill development metrics
            skill_development = self._get_skill_development_metrics(patient_id)
            
            # Get treatment response data
            treatment_response = self._get_treatment_response_data(patient_id)
            
            return {
                'correlation_data': correlations,
                'pattern_recognition': patterns,
                'skill_development': skill_development,
                'treatment_response': treatment_response,
                'session_planning_insights': self._generate_session_planning_insights(
                    patient_id, correlations, patterns, skill_development, treatment_response
                ),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating evidence-based session plan: {str(e)}")
            return {'error': f'Failed to generate session plan: {str(e)}'}
    
    def _get_week_at_a_glance(self, patient_id: int) -> Dict[str, Any]:
        """Get week-at-a-glance summary"""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get mood trends
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        # Get exercise completion
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            )
        ).all()
        
        # Get crisis episodes
        crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= week_ago
            )
        ).all()
        
        # Calculate trends
        mood_trend = 'stable'
        if len(mood_entries) >= 3:
            recent_avg = np.mean([entry.intensity_level for entry in mood_entries[-3:]])
            earlier_avg = np.mean([entry.intensity_level for entry in mood_entries[:3]])
            if recent_avg > earlier_avg + 1:
                mood_trend = 'improving'
            elif recent_avg < earlier_avg - 1:
                mood_trend = 'declining'
        
        exercise_completion = len([s for s in exercise_sessions if s.completion_status == 'completed'])
        total_exercises = len(exercise_sessions)
        completion_rate = exercise_completion / total_exercises if total_exercises > 0 else 0
        
        return {
            'mood_trend': mood_trend,
            'mood_entries_count': len(mood_entries),
            'avg_mood_level': np.mean([entry.intensity_level for entry in mood_entries]) if mood_entries else None,
            'exercise_completion_rate': round(completion_rate, 3),
            'exercises_completed': exercise_completion,
            'total_exercises_assigned': total_exercises,
            'crisis_episodes': len(crisis_alerts),
            'engagement_level': 'high' if completion_rate >= 0.8 and len(mood_entries) >= 5 else 'low'
        }
    
    def _identify_key_concerns(self, patient_id: int) -> List[Dict[str, Any]]:
        """Identify key concerns for the session"""
        concerns = []
        week_ago = datetime.now() - timedelta(days=7)
        
        # Check for declining patterns
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        if len(mood_entries) >= 3:
            recent_avg = np.mean([entry.intensity_level for entry in mood_entries[-3:]])
            earlier_avg = np.mean([entry.intensity_level for entry in mood_entries[:3]])
            if recent_avg < earlier_avg - 2:
                concerns.append({
                    'type': 'mood_decline',
                    'severity': 'moderate',
                    'description': 'Significant mood decline over the past week',
                    'priority': 'high'
                })
        
        # Check for missed exercises
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            )
        ).all()
        
        skipped_exercises = [s for s in exercise_sessions if s.completion_status == 'abandoned']
        if len(skipped_exercises) >= 3:
            concerns.append({
                'type': 'exercise_avoidance',
                'severity': 'moderate',
                'description': f'Multiple exercises skipped ({len(skipped_exercises)} this week)',
                'priority': 'medium'
            })
        
        # Check for crisis episodes
        crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= week_ago
            )
        ).all()
        
        if crisis_alerts:
            concerns.append({
                'type': 'crisis_episodes',
                'severity': 'high',
                'description': f'{len(crisis_alerts)} crisis episodes this week',
                'priority': 'critical'
            })
        
        # Check for low engagement
        if len(mood_entries) < 3 and len(exercise_sessions) < 2:
            concerns.append({
                'type': 'low_engagement',
                'severity': 'moderate',
                'description': 'Low overall engagement with treatment activities',
                'priority': 'medium'
            })
        
        return concerns
    
    def _get_progress_highlights(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get progress highlights and positive trends"""
        highlights = []
        week_ago = datetime.now() - timedelta(days=7)
        
        # Check for mood improvements
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        if len(mood_entries) >= 3:
            recent_avg = np.mean([entry.intensity_level for entry in mood_entries[-3:]])
            earlier_avg = np.mean([entry.intensity_level for entry in mood_entries[:3]])
            if recent_avg > earlier_avg + 1:
                highlights.append({
                    'type': 'mood_improvement',
                    'description': 'Mood showing consistent improvement',
                    'evidence': f'Average mood increased from {earlier_avg:.1f} to {recent_avg:.1f}',
                    'significance': 'high'
                })
        
        # Check for exercise consistency
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            )
        ).all()
        
        completed_exercises = [s for s in exercise_sessions if s.completion_status == 'completed']
        if len(completed_exercises) >= 5:
            highlights.append({
                'type': 'exercise_consistency',
                'description': 'Strong exercise completion rate',
                'evidence': f'{len(completed_exercises)} exercises completed this week',
                'significance': 'medium'
            })
        
        # Check for skill development
        thought_records = ThoughtRecord.query.filter(
            and_(
                ThoughtRecord.patient_id == patient_id,
                ThoughtRecord.created_at >= week_ago
            )
        ).all()
        
        if thought_records:
            avg_insight = np.mean([r.insight_score for r in thought_records if r.insight_score])
            if avg_insight and avg_insight >= 7:
                highlights.append({
                    'type': 'skill_development',
                    'description': 'Strong cognitive insight development',
                    'evidence': f'Average insight score of {avg_insight:.1f}/10',
                    'significance': 'high'
                })
        
        # Check for crisis reduction
        crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= week_ago
            )
        ).all()
        
        if not crisis_alerts:
            highlights.append({
                'type': 'crisis_reduction',
                'description': 'No crisis episodes this week',
                'evidence': 'Crisis-free week - safety planning working',
                'significance': 'high'
            })
        
        return highlights
    
    def _suggest_session_focus(self, patient_id: int) -> Dict[str, Any]:
        """Suggest session focus based on recent data"""
        concerns = self._identify_key_concerns(patient_id)
        highlights = self._get_progress_highlights(patient_id)
        
        # Determine primary focus
        primary_focus = 'general_progress'
        if any(c['priority'] == 'critical' for c in concerns):
            primary_focus = 'crisis_management'
        elif any(c['type'] == 'mood_decline' for c in concerns):
            primary_focus = 'mood_stabilization'
        elif any(c['type'] == 'exercise_avoidance' for c in concerns):
            primary_focus = 'engagement_improvement'
        
        # Generate specific focus areas
        focus_areas = []
        if primary_focus == 'crisis_management':
            focus_areas.extend([
                'Safety planning review',
                'Crisis prevention strategies',
                'Emergency contact verification'
            ])
        elif primary_focus == 'mood_stabilization':
            focus_areas.extend([
                'Recent stressors exploration',
                'Coping strategy review',
                'Mood regulation techniques'
            ])
        elif primary_focus == 'engagement_improvement':
            focus_areas.extend([
                'Barriers to engagement',
                'Motivation enhancement',
                'Treatment goal review'
            ])
        else:
            focus_areas.extend([
                'Progress celebration',
                'Skill reinforcement',
                'Next steps planning'
            ])
        
        return {
            'primary_focus': primary_focus,
            'focus_areas': focus_areas,
            'priority_level': 'high' if primary_focus == 'crisis_management' else 'medium'
        }
    
    def _get_treatment_plan_updates(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get recommended treatment plan updates"""
        updates = []
        week_ago = datetime.now() - timedelta(days=7)
        
        # Analyze treatment response
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago,
                ExerciseSession.effectiveness_rating.isnot(None)
            )
        ).all()
        
        if exercise_sessions:
            avg_effectiveness = np.mean([s.effectiveness_rating for s in exercise_sessions])
            if avg_effectiveness < 6:
                updates.append({
                    'type': 'exercise_adjustment',
                    'recommendation': 'Simplify exercise recommendations',
                    'reasoning': f'Low effectiveness rating ({avg_effectiveness:.1f}/10)',
                    'priority': 'medium'
                })
            elif avg_effectiveness >= 8:
                updates.append({
                    'type': 'exercise_advancement',
                    'recommendation': 'Consider more advanced exercises',
                    'reasoning': f'High effectiveness rating ({avg_effectiveness:.1f}/10)',
                    'priority': 'low'
                })
        
        # Analyze engagement patterns
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).count()
        
        if mood_entries < 3:
            updates.append({
                'type': 'monitoring_adjustment',
                'recommendation': 'Increase mood tracking reminders',
                'reasoning': f'Only {mood_entries} mood entries this week',
                'priority': 'medium'
            })
        
        return updates
    
    def _get_last_session_date(self, patient_id: int) -> Optional[str]:
        """Get date of last session"""
        # This would typically query a sessions table
        # For now, return None
        return None
    
    def _analyze_mood_patterns_for_talking_points(self, patient_id: int) -> Dict[str, Any]:
        """Analyze mood patterns for talking points"""
        week_ago = datetime.now() - timedelta(days=7)
        
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= week_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        patterns = {
            'day_patterns': {},
            'time_patterns': {},
            'context_patterns': {},
            'trend': 'stable'
        }
        
        if mood_entries:
            # Day of week patterns
            day_patterns = defaultdict(list)
            for entry in mood_entries:
                day = entry.timestamp.strftime('%A')
                day_patterns[day].append(entry.intensity_level)
            
            patterns['day_patterns'] = {day: np.mean(levels) for day, levels in day_patterns.items()}
            
            # Time patterns
            time_patterns = defaultdict(list)
            for entry in mood_entries:
                hour = entry.timestamp.hour
                if hour < 12:
                    time_slot = 'morning'
                elif hour < 17:
                    time_slot = 'afternoon'
                else:
                    time_slot = 'evening'
                time_patterns[time_slot].append(entry.intensity_level)
            
            patterns['time_patterns'] = {time: np.mean(levels) for time, levels in time_patterns.items()}
            
            # Context patterns
            context_patterns = defaultdict(list)
            for entry in mood_entries:
                if entry.social_context:
                    context_patterns[entry.social_context].append(entry.intensity_level)
            
            patterns['context_patterns'] = {context: np.mean(levels) for context, levels in context_patterns.items()}
            
            # Trend analysis
            if len(mood_entries) >= 3:
                recent_avg = np.mean([entry.intensity_level for entry in mood_entries[-3:]])
                earlier_avg = np.mean([entry.intensity_level for entry in mood_entries[:3]])
                if recent_avg > earlier_avg + 1:
                    patterns['trend'] = 'improving'
                elif recent_avg < earlier_avg - 1:
                    patterns['trend'] = 'declining'
        
        return patterns
    
    def _analyze_exercise_patterns_for_talking_points(self, patient_id: int) -> Dict[str, Any]:
        """Analyze exercise patterns for talking points"""
        week_ago = datetime.now() - timedelta(days=7)
        
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= week_ago
            )
        ).all()
        
        patterns = {
            'completion_rate': 0,
            'effectiveness': None,
            'preferred_types': [],
            'barriers': []
        }
        
        if exercise_sessions:
            completed = [s for s in exercise_sessions if s.completion_status == 'completed']
            patterns['completion_rate'] = len(completed) / len(exercise_sessions)
            
            # Analyze effectiveness
            rated_sessions = [s for s in completed if s.effectiveness_rating is not None]
            if rated_sessions:
                patterns['effectiveness'] = np.mean([s.effectiveness_rating for s in rated_sessions])
            
            # Analyze preferred types
            type_counts = defaultdict(int)
            for session in completed:
                if session.exercise and session.exercise.type:
                    type_counts[session.exercise.type] += 1
            
            if type_counts:
                patterns['preferred_types'] = [t for t, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)]
            
            # Identify barriers
            abandoned = [s for s in exercise_sessions if s.completion_status == 'abandoned']
            if abandoned:
                patterns['barriers'].append(f"{len(abandoned)} exercises were started but not completed")
        
        return patterns
    
    def _analyze_cbt_patterns_for_talking_points(self, patient_id: int) -> Dict[str, Any]:
        """Analyze CBT patterns for talking points"""
        month_ago = datetime.now() - timedelta(days=30)
        
        thought_records = ThoughtRecord.query.filter(
            and_(
                ThoughtRecord.patient_id == patient_id,
                ThoughtRecord.created_at >= month_ago
            )
        ).all()
        
        patterns = {
            'distortion_types': [],
            'insight_development': None,
            'skill_mastery': 'beginner',
            'challenges': []
        }
        
        if thought_records:
            # Analyze distortion types
            distortion_counts = defaultdict(int)
            for record in thought_records:
                if record.cognitive_distortion:
                    distortion_counts[record.cognitive_distortion] += 1
            
            patterns['distortion_types'] = [d for d, c in sorted(distortion_counts.items(), key=lambda x: x[1], reverse=True)]
            
            # Analyze insight development
            insight_scores = [r.insight_score for r in thought_records if r.insight_score]
            if insight_scores:
                patterns['insight_development'] = np.mean(insight_scores)
                
                if patterns['insight_development'] >= 8:
                    patterns['skill_mastery'] = 'advanced'
                elif patterns['insight_development'] >= 6:
                    patterns['skill_mastery'] = 'intermediate'
            
            # Identify challenges
            if len(thought_records) < 5:
                patterns['challenges'].append("Limited thought record practice")
            
            if patterns['insight_development'] and patterns['insight_development'] < 5:
                patterns['challenges'].append("Difficulty developing cognitive insight")
        
        return patterns
    
    def _analyze_crisis_patterns_for_talking_points(self, patient_id: int) -> Dict[str, Any]:
        """Analyze crisis patterns for talking points"""
        month_ago = datetime.now() - timedelta(days=30)
        
        crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= month_ago
            )
        ).all()
        
        patterns = {
            'frequency': len(crisis_alerts),
            'triggers': [],
            'timing': {},
            'intervention_effectiveness': 'unknown'
        }
        
        if crisis_alerts:
            # Analyze timing patterns
            time_patterns = defaultdict(int)
            for alert in crisis_alerts:
                hour = alert.created_at.hour
                if hour < 12:
                    time_slot = 'morning'
                elif hour < 17:
                    time_slot = 'afternoon'
                else:
                    time_slot = 'evening'
                time_patterns[time_slot] += 1
            
            patterns['timing'] = dict(time_patterns)
            
            # Check intervention effectiveness
            if len(crisis_alerts) == 0:
                patterns['intervention_effectiveness'] = 'good'
            elif len(crisis_alerts) <= 2:
                patterns['intervention_effectiveness'] = 'moderate'
            else:
                patterns['intervention_effectiveness'] = 'poor'
        
        return patterns
    
    def _generate_talking_points(self, patient_id: int, mood_patterns: Dict, 
                               exercise_patterns: Dict, cbt_patterns: Dict, 
                               crisis_patterns: Dict) -> Dict[str, Any]:
        """Generate session talking points"""
        talking_points = {
            'mood': [],
            'exercise': [],
            'cbt': [],
            'crisis': [],
            'general': [],
            'evidence': []
        }
        
        # Mood-focused talking points
        if mood_patterns['day_patterns']:
            worst_day = min(mood_patterns['day_patterns'].items(), key=lambda x: x[1])
            best_day = max(mood_patterns['day_patterns'].items(), key=lambda x: x[1])
            
            talking_points['mood'].append(f"Mood data shows {worst_day[0]} tends to be challenging - what happens on {worst_day[0]}s?")
            talking_points['mood'].append(f"Your mood is consistently better on {best_day[0]}s - what makes {best_day[0]}s different?")
        
        if mood_patterns['trend'] == 'declining':
            talking_points['mood'].append("I notice your mood has been declining recently - what's been happening?")
        elif mood_patterns['trend'] == 'improving':
            talking_points['mood'].append("Your mood has been improving - what's been working well for you?")
        
        # Exercise-focused talking points
        if exercise_patterns['completion_rate'] >= 0.8:
            talking_points['exercise'].append("You've been very consistent with your exercises - how are they helping you?")
        elif exercise_patterns['completion_rate'] < 0.5:
            talking_points['exercise'].append("I notice you've been having trouble completing exercises - what barriers are you encountering?")
        
        if exercise_patterns['effectiveness'] and exercise_patterns['effectiveness'] >= 8:
            talking_points['exercise'].append("The exercises seem to be very effective for you - which ones are most helpful?")
        elif exercise_patterns['effectiveness'] and exercise_patterns['effectiveness'] < 6:
            talking_points['exercise'].append("Some exercises don't seem to be working well - let's figure out what would be more helpful")
        
        # CBT-focused talking points
        if cbt_patterns['distortion_types']:
            most_common = cbt_patterns['distortion_types'][0]
            talking_points['cbt'].append(f"Your thought records show a lot of {most_common} thinking - let's explore this pattern")
        
        if cbt_patterns['skill_mastery'] == 'advanced':
            talking_points['cbt'].append("You're really mastering the CBT techniques - how can we build on this progress?")
        elif cbt_patterns['skill_mastery'] == 'beginner':
            talking_points['cbt'].append("Let's review the CBT concepts and make sure they're clear")
        
        # Crisis-focused talking points
        if crisis_patterns['frequency'] > 0:
            talking_points['crisis'].append(f"I noticed you accessed crisis tools {crisis_patterns['frequency']} times recently - let's talk about that")
        
        if crisis_patterns['intervention_effectiveness'] == 'poor':
            talking_points['crisis'].append("The crisis interventions don't seem to be working well - let's develop a better safety plan")
        
        # General talking points
        talking_points['general'].append("How have things been going since our last session?")
        talking_points['general'].append("What would be most helpful to focus on today?")
        
        # Evidence basis
        talking_points['evidence'].append("All recommendations based on your actual usage data and patterns")
        
        return talking_points
    
    def _get_correlation_data(self, patient_id: int) -> Dict[str, Any]:
        """Get correlation data between activities and outcomes"""
        month_ago = datetime.now() - timedelta(days=30)
        
        # Get mood and exercise data
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= month_ago
            )
        ).order_by(MoodEntry.timestamp).all()
        
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago,
                ExerciseSession.completion_status == 'completed'
            )
        ).order_by(ExerciseSession.start_time).all()
        
        correlations = {
            'mood_exercise_correlation': None,
            'exercise_effectiveness_correlation': None,
            'timing_effectiveness': None
        }
        
        # Calculate mood-exercise correlation
        if mood_entries and exercise_sessions:
            # Create daily mood averages
            daily_mood = defaultdict(list)
            for entry in mood_entries:
                date = entry.timestamp.date()
                daily_mood[date].append(entry.intensity_level)
            
            daily_mood_avg = {date: np.mean(levels) for date, levels in daily_mood.items()}
            
            # Create daily exercise counts
            daily_exercise = defaultdict(int)
            for session in exercise_sessions:
                date = session.start_time.date()
                daily_exercise[date] += 1
            
            # Calculate correlation
            common_dates = set(daily_mood_avg.keys()) & set(daily_exercise.keys())
            if len(common_dates) >= 5:
                mood_values = [daily_mood_avg[date] for date in common_dates]
                exercise_values = [daily_exercise[date] for date in common_dates]
                
                correlation = np.corrcoef(mood_values, exercise_values)[0, 1]
                if not np.isnan(correlation):
                    correlations['mood_exercise_correlation'] = round(correlation, 3)
        
        return correlations
    
    def _get_pattern_recognition(self, patient_id: int) -> Dict[str, Any]:
        """Get pattern recognition insights"""
        month_ago = datetime.now() - timedelta(days=30)
        
        patterns = {
            'crisis_triggers': [],
            'optimal_timing': [],
            'barrier_patterns': [],
            'success_patterns': []
        }
        
        # Analyze crisis triggers
        crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= month_ago
            )
        ).all()
        
        if crisis_alerts:
            # Look for timing patterns
            crisis_times = [alert.created_at.hour for alert in crisis_alerts]
            if crisis_times:
                most_common_hour = max(set(crisis_times), key=crisis_times.count)
                patterns['crisis_triggers'].append(f"Crisis episodes most common around {most_common_hour}:00")
        
        # Analyze optimal timing
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago,
                ExerciseSession.completion_status == 'completed',
                ExerciseSession.effectiveness_rating.isnot(None)
            )
        ).all()
        
        if exercise_sessions:
            # Find most effective time
            time_effectiveness = defaultdict(list)
            for session in exercise_sessions:
                hour = session.start_time.hour
                if hour < 12:
                    time_slot = 'morning'
                elif hour < 17:
                    time_slot = 'afternoon'
                else:
                    time_slot = 'evening'
                time_effectiveness[time_slot].append(session.effectiveness_rating)
            
            if time_effectiveness:
                avg_effectiveness = {time: np.mean(ratings) for time, ratings in time_effectiveness.items()}
                best_time = max(avg_effectiveness.items(), key=lambda x: x[1])
                patterns['optimal_timing'].append(f"Exercises most effective in {best_time[0]} ({best_time[1]:.1f}/10)")
        
        return patterns
    
    def _get_skill_development_metrics(self, patient_id: int) -> Dict[str, Any]:
        """Get skill development metrics"""
        month_ago = datetime.now() - timedelta(days=30)
        
        thought_records = ThoughtRecord.query.filter(
            and_(
                ThoughtRecord.patient_id == patient_id,
                ThoughtRecord.created_at >= month_ago
            )
        ).order_by(ThoughtRecord.created_at).all()
        
        metrics = {
            'cbt_mastery': 0,
            'insight_development': 0,
            'skill_consistency': 0,
            'readiness_for_advancement': False
        }
        
        if thought_records:
            # Calculate CBT mastery
            insight_scores = [r.insight_score for r in thought_records if r.insight_score]
            if insight_scores:
                metrics['cbt_mastery'] = round(np.mean(insight_scores) * 10, 1)  # Convert to percentage
                metrics['insight_development'] = round(np.mean(insight_scores) * 10, 1)
            
            # Calculate skill consistency
            if len(thought_records) >= 5:
                metrics['skill_consistency'] = min(100, len(thought_records) * 10)
            
            # Determine readiness for advancement
            if metrics['cbt_mastery'] >= 70 and metrics['skill_consistency'] >= 50:
                metrics['readiness_for_advancement'] = True
        
        return metrics
    
    def _get_treatment_response_data(self, patient_id: int) -> Dict[str, Any]:
        """Get treatment response data"""
        month_ago = datetime.now() - timedelta(days=30)
        
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago,
                ExerciseSession.effectiveness_rating.isnot(None)
            )
        ).all()
        
        response_data = {
            'overall_effectiveness': None,
            'effectiveness_trend': 'stable',
            'best_interventions': [],
            'areas_for_improvement': []
        }
        
        if exercise_sessions:
            # Calculate overall effectiveness
            effectiveness_scores = [s.effectiveness_rating for s in exercise_sessions]
            response_data['overall_effectiveness'] = round(np.mean(effectiveness_scores), 2)
            
            # Determine trend
            if len(exercise_sessions) >= 6:
                recent_avg = np.mean([s.effectiveness_rating for s in exercise_sessions[-3:]])
                earlier_avg = np.mean([s.effectiveness_rating for s in exercise_sessions[:3]])
                if recent_avg > earlier_avg + 1:
                    response_data['effectiveness_trend'] = 'improving'
                elif recent_avg < earlier_avg - 1:
                    response_data['effectiveness_trend'] = 'declining'
            
            # Identify best interventions
            type_effectiveness = defaultdict(list)
            for session in exercise_sessions:
                if session.exercise and session.exercise.type:
                    type_effectiveness[session.exercise.type].append(session.effectiveness_rating)
            
            if type_effectiveness:
                avg_by_type = {t: np.mean(ratings) for t, ratings in type_effectiveness.items()}
                best_types = sorted(avg_by_type.items(), key=lambda x: x[1], reverse=True)
                response_data['best_interventions'] = [t[0] for t in best_types[:3]]
            
            # Identify areas for improvement
            if response_data['overall_effectiveness'] and response_data['overall_effectiveness'] < 6:
                response_data['areas_for_improvement'].append("Exercise effectiveness below target")
        
        return response_data
    
    def _generate_session_planning_insights(self, patient_id: int, correlations: Dict, 
                                          patterns: Dict, skill_development: Dict, 
                                          treatment_response: Dict) -> List[str]:
        """Generate session planning insights"""
        insights = []
        
        # Correlation insights
        if correlations['mood_exercise_correlation'] and correlations['mood_exercise_correlation'] > 0.5:
            insights.append(f"Strong positive correlation ({correlations['mood_exercise_correlation']}) between exercise completion and mood improvement")
        
        # Pattern insights
        if patterns['optimal_timing']:
            insights.append(f"Optimal timing identified: {patterns['optimal_timing'][0]}")
        
        if patterns['crisis_triggers']:
            insights.append(f"Crisis pattern identified: {patterns['crisis_triggers'][0]}")
        
        # Skill development insights
        if skill_development['cbt_mastery'] >= 70:
            insights.append(f"CBT mastery at {skill_development['cbt_mastery']}% - ready for advanced techniques")
        elif skill_development['cbt_mastery'] < 50:
            insights.append(f"CBT mastery at {skill_development['cbt_mastery']}% - focus on basic concepts")
        
        # Treatment response insights
        if treatment_response['effectiveness_trend'] == 'improving':
            insights.append("Treatment effectiveness improving - continue current approach")
        elif treatment_response['effectiveness_trend'] == 'declining':
            insights.append("Treatment effectiveness declining - evaluate and adjust approach")
        
        if treatment_response['best_interventions']:
            insights.append(f"Most effective interventions: {', '.join(treatment_response['best_interventions'])}")
        
        return insights

# API Routes
@session_preparation.route('/api/pre-session-brief/<int:patient_id>')
@login_required
def get_pre_session_brief(patient_id):
    """Get pre-session intelligence brief"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    system = ProviderSessionPreparationSystem()
    brief = system.generate_pre_session_brief(patient_id)
    return jsonify(brief)

@session_preparation.route('/api/session-talking-points/<int:patient_id>')
@login_required
def get_session_talking_points(patient_id):
    """Get session-specific talking points"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    system = ProviderSessionPreparationSystem()
    talking_points = system.generate_session_talking_points(patient_id)
    return jsonify(talking_points)

@session_preparation.route('/api/evidence-based-session-plan/<int:patient_id>')
@login_required
def get_evidence_based_session_plan(patient_id):
    """Get evidence-based session planning"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Unauthorized'}), 403
    
    system = ProviderSessionPreparationSystem()
    session_plan = system.generate_evidence_based_session_plan(patient_id)
    return jsonify(session_plan)
