#!/usr/bin/env python3
"""
AI-Powered Pre-Session Intelligence Briefing System
Generates intelligent briefings based on patient exercise activity using OpenAI API
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import and_, desc, func
from collections import defaultdict
import numpy as np
import openai
from openai import OpenAI

# Import database models - will be imported dynamically to avoid circular imports

class AISessionBriefingSystem:
    """AI-powered session briefing system using OpenAI API"""
    
    def __init__(self):
        # Initialize OpenAI client with robust API key handling
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Fallback API key if environment variable is not set
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
            print("⚠️ Using fallback API key - consider setting OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4"  # Use GPT-4 for better analysis
        
    def generate_session_briefing(self, patient_id: int, models=None) -> Dict[str, Any]:
        """Generate comprehensive AI-powered session briefing"""
        try:
            # Import database models directly
            from app_ml_complete import (
                db, Patient, PHQ9Assessment, ExerciseSession, MoodEntry, 
                CrisisAlert, MindfulnessSession, MicroAssessment, ThoughtRecord
            )
            
            # Get patient data
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Collect comprehensive patient data
            patient_data = self._collect_patient_data(patient_id, models)
            
            # Generate AI briefing
            briefing = self._generate_ai_briefing(patient_data)
            
            return {
                'success': True,
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'patient_id': patient_id,
                'data_summary': patient_data['summary'],
                'briefing_text': briefing['full_briefing'],
                'sections': briefing['sections'],
                'key_insights': briefing['key_insights'],
                'recommendations': briefing['recommendations'],
                'generated_at': datetime.now().isoformat(),
                'is_mock': False
            }
            
        except Exception as e:
            logging.error(f"Error generating AI briefing: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to generate briefing: {str(e)}',
                'is_mock': True
            }
    
    def _collect_patient_data(self, patient_id: int, models=None) -> Dict[str, Any]:
        """Collect comprehensive patient data for analysis"""
        # Import database models directly
        from app_ml_complete import (
            db, Patient, PHQ9Assessment, ExerciseSession, MoodEntry, 
            CrisisAlert, MindfulnessSession, MicroAssessment, ThoughtRecord
        )
        
        # Time ranges
        week_ago = datetime.now() - timedelta(days=7)
        month_ago = datetime.now() - timedelta(days=30)
        
        # Get mood entries
        mood_entries = MoodEntry.query.filter(
            and_(
                MoodEntry.patient_id == patient_id,
                MoodEntry.timestamp >= month_ago
            )
        ).order_by(MoodEntry.timestamp.desc()).all()
        
        # Get exercise sessions
        exercise_sessions = ExerciseSession.query.filter(
            and_(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.start_time >= month_ago
            )
        ).order_by(ExerciseSession.start_time.desc()).all()
        
        # Get thought records
        thought_records = ThoughtRecord.query.filter(
            and_(
                ThoughtRecord.patient_id == patient_id,
                ThoughtRecord.created_at >= month_ago
            )
        ).order_by(ThoughtRecord.created_at.desc()).all()
        
        # Get crisis alerts
        crisis_alerts = CrisisAlert.query.filter(
            and_(
                CrisisAlert.patient_id == patient_id,
                CrisisAlert.created_at >= month_ago
            )
        ).order_by(CrisisAlert.created_at.desc()).all()
        
        # Get PHQ-9 assessments
        phq9_assessments = PHQ9Assessment.query.filter(
            and_(
                PHQ9Assessment.patient_id == patient_id,
                PHQ9Assessment.assessment_date >= month_ago
            )
        ).order_by(PHQ9Assessment.assessment_date.desc()).all()
        
        # Analyze patterns
        mood_trend = self._analyze_mood_trend(mood_entries)
        exercise_patterns = self._analyze_exercise_patterns(exercise_sessions)
        engagement_metrics = self._calculate_engagement_metrics(exercise_sessions, mood_entries)
        crisis_patterns = self._analyze_crisis_patterns(crisis_alerts)
        cbt_patterns = self._analyze_cbt_patterns(thought_records)
        
        return {
            'patient_id': patient_id,
            'mood_entries': [self._serialize_mood_entry(entry) for entry in mood_entries],
            'exercise_sessions': [self._serialize_exercise_session(session) for session in exercise_sessions],
            'thought_records': [self._serialize_thought_record(record) for record in thought_records],
            'crisis_alerts': [self._serialize_crisis_alert(alert) for alert in crisis_alerts],
            'phq9_assessments': [self._serialize_phq9_assessment(assessment) for assessment in phq9_assessments],
            'mood_trend': mood_trend,
            'exercise_patterns': exercise_patterns,
            'engagement_metrics': engagement_metrics,
            'crisis_patterns': crisis_patterns,
            'cbt_patterns': cbt_patterns,
            'summary': {
                'mood_entries_count': len(mood_entries),
                'exercise_sessions_count': len(exercise_sessions),
                'thought_records_count': len(thought_records),
                'crisis_alerts_count': len(crisis_alerts),
                'phq9_assessments_count': len(phq9_assessments),
                'analysis_period_days': 30
            }
        }
    
    def _generate_ai_briefing(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI briefing using OpenAI API"""
        
        # Create comprehensive prompt
        prompt = self._create_analysis_prompt(patient_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert clinical psychologist analyzing patient data to generate pre-session intelligence briefings. 
                        Your analysis should be:
                        1. Clinically accurate and evidence-based
                        2. Actionable for the provider
                        3. Focused on patterns and insights
                        4. Structured and easy to read
                        5. Empathetic and patient-centered
                        
                        Provide insights in these key areas:
                        - Mood and emotional patterns
                        - Exercise engagement and effectiveness
                        - Cognitive patterns (CBT work)
                        - Crisis indicators and safety
                        - Treatment progress and recommendations
                        - Session focus suggestions"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            briefing_text = response.choices[0].message.content
            
            # Parse the response into structured sections
            sections = self._parse_briefing_sections(briefing_text)
            
            return {
                'full_briefing': briefing_text,
                'sections': sections,
                'key_insights': self._extract_key_insights(briefing_text),
                'recommendations': self._extract_recommendations(briefing_text)
            }
            
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            # Return fallback briefing
            return self._generate_fallback_briefing(patient_data)
    
    def _create_analysis_prompt(self, patient_data: Dict[str, Any]) -> str:
        """Create comprehensive prompt for AI analysis"""
        
        prompt = f"""
        Analyze the following patient data and generate a pre-session intelligence briefing for a mental health provider.
        
        PATIENT DATA SUMMARY:
        - Analysis Period: Last 30 days
        - Mood Entries: {patient_data['summary']['mood_entries_count']}
        - Exercise Sessions: {patient_data['summary']['exercise_sessions_count']}
        - Thought Records: {patient_data['summary']['thought_records_count']}
        - Crisis Alerts: {patient_data['summary']['crisis_alerts_count']}
        - PHQ-9 Assessments: {patient_data['summary']['phq9_assessments_count']}
        
        MOOD TREND ANALYSIS:
        {json.dumps(patient_data['mood_trend'], indent=2)}
        
        EXERCISE PATTERNS:
        {json.dumps(patient_data['exercise_patterns'], indent=2)}
        
        ENGAGEMENT METRICS:
        {json.dumps(patient_data['engagement_metrics'], indent=2)}
        
        CRISIS PATTERNS:
        {json.dumps(patient_data['crisis_patterns'], indent=2)}
        
        CBT PATTERNS:
        {json.dumps(patient_data['cbt_patterns'], indent=2)}
        
        RECENT MOOD ENTRIES (Last 10):
        {json.dumps(patient_data['mood_entries'][:10], indent=2)}
        
        RECENT EXERCISE SESSIONS (Last 10):
        {json.dumps(patient_data['exercise_sessions'][:10], indent=2)}
        
        RECENT THOUGHT RECORDS (Last 5):
        {json.dumps(patient_data['thought_records'][:5], indent=2)}
        
        CRISIS ALERTS:
        {json.dumps(patient_data['crisis_alerts'], indent=2)}
        
        PHQ-9 ASSESSMENTS:
        {json.dumps(patient_data['phq9_assessments'], indent=2)}
        
        Please provide a structured briefing with the following sections:
        1. **Executive Summary** - Key findings and overall patient status
        2. **Mood & Emotional Patterns** - Analysis of mood trends and emotional indicators
        3. **Exercise Engagement Analysis** - Patterns in exercise completion and effectiveness
        4. **Cognitive Work Progress** - CBT thought record analysis and skill development
        5. **Crisis & Safety Assessment** - Risk factors and safety considerations
        6. **Treatment Progress** - Overall progress and areas of improvement
        7. **Session Focus Recommendations** - Specific areas to address in upcoming session
        8. **Clinical Insights** - Evidence-based observations and patterns
        """
        
        return prompt
    
    def _parse_briefing_sections(self, briefing_text: str) -> Dict[str, str]:
        """Parse briefing text into structured sections"""
        sections = {}
        
        # Split by section headers
        section_patterns = [
            "**Executive Summary**",
            "**Mood & Emotional Patterns**",
            "**Exercise Engagement Analysis**",
            "**Cognitive Work Progress**",
            "**Crisis & Safety Assessment**",
            "**Treatment Progress**",
            "**Session Focus Recommendations**",
            "**Clinical Insights**"
        ]
        
        current_section = None
        current_content = []
        
        lines = briefing_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(pattern in line for pattern in section_patterns):
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.replace('**', '').strip()
                current_content = []
            elif current_section and line:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_key_insights(self, briefing_text: str) -> List[str]:
        """Extract key insights from briefing text"""
        insights = []
        
        # Look for key phrases that indicate insights
        key_phrases = [
            "significant improvement",
            "concerning pattern",
            "high engagement",
            "low engagement",
            "crisis indicators",
            "skill development",
            "mood stabilization",
            "treatment response"
        ]
        
        lines = briefing_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(phrase in line.lower() for phrase in key_phrases):
                insights.append(line)
        
        return insights[:5]  # Return top 5 insights
    
    def _extract_recommendations(self, briefing_text: str) -> List[str]:
        """Extract recommendations from briefing text"""
        recommendations = []
        
        # Look for recommendation indicators
        rec_indicators = [
            "recommend",
            "suggest",
            "consider",
            "focus on",
            "address",
            "explore",
            "review"
        ]
        
        lines = briefing_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(indicator in line.lower() for indicator in rec_indicators):
                recommendations.append(line)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_fallback_briefing(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback briefing when AI is unavailable"""
        
        summary = patient_data['summary']
        mood_trend = patient_data['mood_trend']
        exercise_patterns = patient_data['exercise_patterns']
        
        briefing_text = f"""
        **Executive Summary**
        Patient has completed {summary['exercise_sessions_count']} exercise sessions and {summary['mood_entries_count']} mood entries in the last 30 days.
        
        **Mood & Emotional Patterns**
        Mood trend: {mood_trend.get('trend', 'stable')}
        Average mood level: {mood_trend.get('average_level', 'N/A')}
        
        **Exercise Engagement Analysis**
        Completion rate: {exercise_patterns.get('completion_rate', 0):.1%}
        Average effectiveness: {exercise_patterns.get('avg_effectiveness', 'N/A')}
        
        **Session Focus Recommendations**
        - Review recent exercise effectiveness
        - Discuss mood patterns and triggers
        - Address any engagement barriers
        """
        
        return {
            'full_briefing': briefing_text,
            'sections': {
                'Executive Summary': f"Patient has completed {summary['exercise_sessions_count']} exercise sessions and {summary['mood_entries_count']} mood entries in the last 30 days.",
                'Mood & Emotional Patterns': f"Mood trend: {mood_trend.get('trend', 'stable')}",
                'Exercise Engagement Analysis': f"Completion rate: {exercise_patterns.get('completion_rate', 0):.1%}",
                'Session Focus Recommendations': "Review recent exercise effectiveness, discuss mood patterns and triggers, address any engagement barriers"
            },
            'key_insights': [f"Completed {summary['exercise_sessions_count']} exercises", f"Mood trend: {mood_trend.get('trend', 'stable')}"],
            'recommendations': ["Review exercise effectiveness", "Discuss mood patterns", "Address engagement barriers"]
        }
    
    def _analyze_mood_trend(self, mood_entries: List) -> Dict[str, Any]:
        """Analyze mood trend patterns"""
        if not mood_entries:
            return {'trend': 'no_data', 'average_level': None, 'volatility': None}
        
        levels = [entry.intensity_level for entry in mood_entries]
        avg_level = sum(levels) / len(levels)
        
        # Calculate trend
        if len(levels) >= 3:
            recent_avg = sum(levels[:3]) / 3
            earlier_avg = sum(levels[-3:]) / 3
            if recent_avg > earlier_avg + 1:
                trend = 'improving'
            elif recent_avg < earlier_avg - 1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        # Calculate volatility
        volatility = max(levels) - min(levels) if len(levels) > 1 else 0
        
        return {
            'trend': trend,
            'average_level': round(avg_level, 2),
            'volatility': volatility,
            'entries_count': len(levels)
        }
    
    def _analyze_exercise_patterns(self, exercise_sessions: List) -> Dict[str, Any]:
        """Analyze exercise completion and effectiveness patterns"""
        if not exercise_sessions:
            return {'completion_rate': 0, 'avg_effectiveness': None, 'preferred_types': []}
        
        completed = [s for s in exercise_sessions if s.completion_status == 'completed']
        completion_rate = len(completed) / len(exercise_sessions)
        
        # Calculate average effectiveness
        rated_sessions = [s for s in completed if s.effectiveness_rating is not None]
        avg_effectiveness = sum(s.effectiveness_rating for s in rated_sessions) / len(rated_sessions) if rated_sessions else None
        
        # Analyze preferred types
        type_counts = {}
        for session in completed:
            if session.exercise and session.exercise.type:
                type_counts[session.exercise.type] = type_counts.get(session.exercise.type, 0) + 1
        
        preferred_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'completion_rate': completion_rate,
            'avg_effectiveness': round(avg_effectiveness, 2) if avg_effectiveness else None,
            'preferred_types': [t[0] for t in preferred_types],
            'total_sessions': len(exercise_sessions),
            'completed_sessions': len(completed)
        }
    
    def _calculate_engagement_metrics(self, exercise_sessions: List, mood_entries: List) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        week_ago = datetime.now() - timedelta(days=7)
        
        recent_exercises = [s for s in exercise_sessions if s.start_time >= week_ago]
        recent_moods = [m for m in mood_entries if m.timestamp >= week_ago]
        
        return {
            'weekly_exercise_count': len(recent_exercises),
            'weekly_mood_entries': len(recent_moods),
            'engagement_level': 'high' if len(recent_exercises) >= 5 and len(recent_moods) >= 3 else 'low'
        }
    
    def _analyze_crisis_patterns(self, crisis_alerts: List) -> Dict[str, Any]:
        """Analyze crisis patterns and risk factors"""
        if not crisis_alerts:
            return {'frequency': 0, 'risk_level': 'low', 'patterns': []}
        
        # Analyze timing patterns
        crisis_times = [alert.created_at.hour for alert in crisis_alerts]
        most_common_hour = max(set(crisis_times), key=crisis_times.count) if crisis_times else None
        
        # Determine risk level
        if len(crisis_alerts) >= 3:
            risk_level = 'high'
        elif len(crisis_alerts) >= 1:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        patterns = []
        if most_common_hour:
            patterns.append(f"Most common crisis time: {most_common_hour}:00")
        
        return {
            'frequency': len(crisis_alerts),
            'risk_level': risk_level,
            'patterns': patterns,
            'recent_crises': len([a for a in crisis_alerts if a.created_at >= datetime.now() - timedelta(days=7)])
        }
    
    def _analyze_cbt_patterns(self, thought_records: List) -> Dict[str, Any]:
        """Analyze CBT patterns for talking points"""
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
                if record.distortions_identified:
                    # Parse JSON string if it's stored as JSON
                    try:
                        import json
                        distortions = json.loads(record.distortions_identified) if isinstance(record.distortions_identified, str) else record.distortions_identified
                        if isinstance(distortions, list):
                            for distortion in distortions:
                                distortion_counts[distortion] += 1
                    except:
                        # If not JSON, treat as single string
                        distortion_counts[record.distortions_identified] += 1
            
            patterns['distortion_types'] = [d for d, c in sorted(distortion_counts.items(), key=lambda x: x[1], reverse=True)]
            
            # Analyze insight development using outcome_rating
            outcome_scores = [r.outcome_rating for r in thought_records if r.outcome_rating]
            if outcome_scores:
                patterns['insight_development'] = np.mean(outcome_scores)
                
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
    
    def _serialize_mood_entry(self, entry) -> Dict[str, Any]:
        """Serialize mood entry for JSON"""
        return {
            'timestamp': entry.timestamp.isoformat(),
            'intensity_level': entry.intensity_level,
            'mood_emoji': entry.mood_emoji,
            'energy_level': entry.energy_level,
            'sleep_quality': entry.sleep_quality,
            'social_context': entry.social_context,
            'weather_mood_metaphor': entry.weather_mood_metaphor,
            'color_selection': entry.color_selection,
            'notes_brief': entry.notes_brief
        }
    
    def _serialize_exercise_session(self, session) -> Dict[str, Any]:
        """Serialize exercise session for JSON"""
        # Calculate duration if both start and completion times exist
        duration_minutes = None
        if session.completion_time and session.start_time:
            duration = session.completion_time - session.start_time
            duration_minutes = int(duration.total_seconds() / 60)
        
        return {
            'start_time': session.start_time.isoformat(),
            'completion_status': session.completion_status,
            'effectiveness_rating': session.effectiveness_rating,
            'exercise_type': session.exercise.type if session.exercise else None,
            'duration_minutes': duration_minutes,
            'engagement_score': session.engagement_score,
            'collected_data': session.collected_data
        }
    
    def _serialize_thought_record(self, record) -> Dict[str, Any]:
        """Serialize thought record for JSON"""
        return {
            'created_at': record.created_at.isoformat(),
            'timestamp': record.timestamp.isoformat(),
            'situation_category': record.situation_category,
            'situation_description': record.situation_description,
            'primary_emotion': record.primary_emotion,
            'emotion_intensity': record.emotion_intensity,
            'initial_thought': record.initial_thought,
            'thought_confidence': record.thought_confidence,
            'distortions_identified': record.distortions_identified,
            'balanced_thought': record.balanced_thought,
            'balanced_confidence': record.balanced_confidence,
            'outcome_rating': record.outcome_rating,
            'mood_improvement': record.mood_improvement,
            'difficulty_level': record.difficulty_level,
            'completion_time': record.completion_time
        }
    
    def _serialize_crisis_alert(self, alert) -> Dict[str, Any]:
        """Serialize crisis alert for JSON"""
        return {
            'created_at': alert.created_at.isoformat(),
            'alert_type': alert.alert_type,
            'alert_message': alert.alert_message,
            'severity_level': alert.severity_level,
            'acknowledged': alert.acknowledged,
            'acknowledged_by': alert.acknowledged_by,
            'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
        }
    
    def _serialize_phq9_assessment(self, assessment) -> Dict[str, Any]:
        """Serialize PHQ-9 assessment for JSON"""
        return {
            'assessment_date': assessment.assessment_date.isoformat(),
            'total_score': assessment.total_score,
            'severity_level': assessment.severity_level,
            'individual_scores': {
                'q1_interest_pleasure': assessment.q1_score,
                'q2_mood_depressed': assessment.q2_score,
                'q3_sleep_problems': assessment.q3_score,
                'q4_fatigue': assessment.q4_score,
                'q5_appetite': assessment.q5_score,
                'q6_self_worth': assessment.q6_score,
                'q7_concentration': assessment.q7_score,
                'q8_psychomotor': assessment.q8_score,
                'q9_suicidal_ideation': assessment.q9_score
            },
            'q9_risk_flag': assessment.q9_risk_flag,
            'crisis_alert_triggered': assessment.crisis_alert_triggered,
            'notes': assessment.notes
        }
