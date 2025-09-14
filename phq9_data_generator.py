#!/usr/bin/env python3
"""
PHQ-9 Data Generator for Realistic Patient Scenarios
Simulates EHR data with diverse depression patterns and temporal progressions
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PHQ9ResponseGenerator:
    """Generates realistic PHQ-9 responses based on patient personas and scenarios"""
    
    def __init__(self):
        # Question correlations based on clinical research
        self.question_correlations = {
            # Core depression symptoms (high correlation)
            'core_depression': [1, 2, 6],  # Interest, depressed mood, self-worth
            'somatic_symptoms': [3, 4, 5],  # Sleep, energy, appetite
            'cognitive_motor': [7, 8],      # Concentration, psychomotor
            'suicidal': [9]                 # Suicidal ideation (special handling)
        }
        
        # Base patterns for different severity levels
        self.severity_patterns = {
            'minimal': {
                'base_scores': [0, 0, 1, 0, 0, 0, 0, 0, 0],
                'variation': 1,
                'correlation_strength': 0.3
            },
            'mild': {
                'base_scores': [1, 1, 1, 1, 0, 1, 0, 0, 0],
                'variation': 1,
                'correlation_strength': 0.4
            },
            'moderate': {
                'base_scores': [2, 2, 1, 2, 1, 2, 1, 1, 0],
                'variation': 1,
                'correlation_strength': 0.5
            },
            'moderately_severe': {
                'base_scores': [2, 2, 2, 2, 2, 2, 2, 1, 1],
                'variation': 1,
                'correlation_strength': 0.6
            },
            'severe': {
                'base_scores': [3, 3, 2, 3, 2, 3, 2, 2, 2],
                'variation': 1,
                'correlation_strength': 0.7
            }
        }
    
    def generate_correlated_scores(self, base_pattern: List[int], correlation_strength: float) -> List[int]:
        """Generate correlated scores based on clinical patterns"""
        scores = []
        
        for i, base_score in enumerate(base_pattern):
            # Add correlation-based variation
            if i in self.question_correlations['core_depression']:
                # Core depression symptoms tend to move together
                core_variation = np.random.normal(0, 0.5) * correlation_strength
                score = base_score + int(round(core_variation))
            elif i in self.question_correlations['somatic_symptoms']:
                # Somatic symptoms have moderate correlation
                somatic_variation = np.random.normal(0, 0.7) * correlation_strength
                score = base_score + int(round(somatic_variation))
            elif i in self.question_correlations['cognitive_motor']:
                # Cognitive/motor symptoms have lower correlation
                cognitive_variation = np.random.normal(0, 0.8) * correlation_strength
                score = base_score + int(round(cognitive_variation))
            else:  # Question 9 - suicidal ideation
                # Special handling for suicidal ideation
                score = base_score
            
            # Ensure scores are within valid range (0-3)
            score = max(0, min(3, score))
            scores.append(score)
        
        return scores
    
    def calculate_severity(self, total_score: int) -> str:
        """Calculate severity level from total score"""
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

class PatientPersona:
    """Defines patient personas with specific depression patterns"""
    
    def __init__(self, name: str, age: int, gender: str, scenario: str):
        self.name = name
        self.age = age
        self.gender = gender
        self.scenario = scenario
        self.generator = PHQ9ResponseGenerator()
        
    def generate_assessment_series(self, duration_weeks: int, frequency: str = 'weekly') -> List[Dict]:
        """Generate a series of PHQ-9 assessments over time"""
        assessments = []
        
        if frequency == 'weekly':
            interval_days = 7
        elif frequency == 'biweekly':
            interval_days = 14
        else:
            interval_days = 7
        
        start_date = datetime.now() - timedelta(weeks=duration_weeks)
        
        for week in range(duration_weeks):
            assessment_date = start_date + timedelta(weeks=week)
            scores = self.generate_weekly_scores(week, duration_weeks)
            
            assessment = {
                'patient_name': self.name,
                'patient_age': self.age,
                'patient_gender': self.gender,
                'scenario': self.scenario,
                'assessment_date': assessment_date.strftime('%Y-%m-%d'),
                'week_number': week + 1,
                'q1_score': scores[0],  # Little interest or pleasure
                'q2_score': scores[1],  # Feeling down, depressed, or hopeless
                'q3_score': scores[2],  # Trouble falling/staying asleep
                'q4_score': scores[3],  # Feeling tired or having little energy
                'q5_score': scores[4],  # Poor appetite or overeating
                'q6_score': scores[5],  # Feeling bad about yourself
                'q7_score': scores[6],  # Trouble concentrating
                'q8_score': scores[7],  # Moving or speaking slowly/being fidgety
                'q9_score': scores[8],  # Thoughts of self-harm
                'total_score': sum(scores),
                'severity_level': self.generator.calculate_severity(sum(scores)),
                'q9_risk_flag': scores[8] >= 2,
                'crisis_alert': scores[8] >= 2 or sum(scores) >= 20
            }
            
            assessments.append(assessment)
        
        return assessments
    
    def generate_weekly_scores(self, week: int, total_weeks: int) -> List[int]:
        """Generate scores for a specific week based on scenario progression"""
        raise NotImplementedError("Subclasses must implement this method")

class CollegeStudentSeasonal(PatientPersona):
    """College student with seasonal depression pattern"""
    
    def __init__(self):
        super().__init__("Sarah Chen", 20, "Female", "College student with seasonal depression")
        self.base_severity = 'mild'
        self.seasonal_peak = 16  # Week 16 (winter peak)
    
    def generate_weekly_scores(self, week: int, total_weeks: int) -> List[int]:
        # Seasonal pattern: worse in winter (weeks 12-20)
        seasonal_factor = 1 + 0.5 * np.sin(2 * np.pi * (week - 12) / 52)
        
        if week < 8:  # Fall semester start
            base_severity = 'mild'
        elif 8 <= week <= 20:  # Winter months
            base_severity = 'moderate'
        else:  # Spring improvement
            base_severity = 'mild'
        
        pattern = self.generator.severity_patterns[base_severity]
        base_scores = pattern['base_scores'].copy()
        
        # Apply seasonal variation
        for i in range(9):
            if i != 8:  # Don't modify suicidal ideation for seasonal pattern
                variation = int(round(seasonal_factor * 0.5))
                base_scores[i] = max(0, min(3, base_scores[i] + variation))
        
        return self.generator.generate_correlated_scores(base_scores, pattern['correlation_strength'])

class NewMotherPostpartum(PatientPersona):
    """New mother with postpartum depression"""
    
    def __init__(self):
        super().__init__("Emily Rodriguez", 28, "Female", "New mother with postpartum depression")
        self.delivery_week = 0
        self.peak_weeks = [2, 3, 4]  # Peak symptoms 2-4 weeks postpartum
    
    def generate_weekly_scores(self, week: int, total_weeks: int) -> List[int]:
        if week == 0:  # Delivery week
            base_severity = 'mild'
        elif week in self.peak_weeks:  # Peak postpartum symptoms
            base_severity = 'moderately_severe'
        elif 5 <= week <= 12:  # Gradual improvement
            base_severity = 'moderate'
        else:  # Continued improvement
            base_severity = 'mild'
        
        pattern = self.generator.severity_patterns[base_severity]
        base_scores = pattern['base_scores'].copy()
        
        # Postpartum-specific patterns
        if week in self.peak_weeks:
            # Higher scores on sleep (q3), energy (q4), and self-worth (q6)
            base_scores[2] = min(3, base_scores[2] + 1)  # Sleep
            base_scores[3] = min(3, base_scores[3] + 1)  # Energy
            base_scores[5] = min(3, base_scores[5] + 1)  # Self-worth
        
        return self.generator.generate_correlated_scores(base_scores, pattern['correlation_strength'])

class ElderlyChronicDepression(PatientPersona):
    """Elderly patient with chronic depression"""
    
    def __init__(self):
        super().__init__("Robert Thompson", 72, "Male", "Elderly patient with chronic depression")
        self.base_severity = 'moderate'
        self.fluctuation_weeks = [3, 7, 11, 15]  # Weeks with worsening
    
    def generate_weekly_scores(self, week: int, total_weeks: int) -> List[int]:
        if week in self.fluctuation_weeks:
            base_severity = 'moderately_severe'
        else:
            base_severity = 'moderate'
        
        pattern = self.generator.severity_patterns[base_severity]
        base_scores = pattern['base_scores'].copy()
        
        # Elderly-specific patterns: higher somatic symptoms
        base_scores[2] = min(3, base_scores[2] + 1)  # Sleep
        base_scores[3] = min(3, base_scores[3] + 1)  # Energy
        base_scores[6] = min(3, base_scores[6] + 1)  # Concentration
        
        return self.generator.generate_correlated_scores(base_scores, pattern['correlation_strength'])

class AdolescentAcuteEpisode(PatientPersona):
    """Adolescent with acute depressive episode"""
    
    def __init__(self):
        super().__init__("Alex Johnson", 16, "Non-binary", "Adolescent with acute depressive episode")
        self.onset_week = 4
        self.peak_week = 8
    
    def generate_weekly_scores(self, week: int, total_weeks: int) -> List[int]:
        if week < self.onset_week:
            base_severity = 'minimal'
        elif week == self.peak_week:
            base_severity = 'severe'
        elif week < 12:
            base_severity = 'moderately_severe'
        else:
            base_severity = 'moderate'
        
        pattern = self.generator.severity_patterns[base_severity]
        base_scores = pattern['base_scores'].copy()
        
        # Adolescent-specific patterns: higher scores on self-worth and concentration
        if week >= self.onset_week:
            base_scores[5] = min(3, base_scores[5] + 1)  # Self-worth
            base_scores[6] = min(3, base_scores[6] + 1)  # Concentration
        
        return self.generator.generate_correlated_scores(base_scores, pattern['correlation_strength'])

class TreatmentResponder(PatientPersona):
    """Patient responding well to treatment"""
    
    def __init__(self):
        super().__init__("Maria Garcia", 35, "Female", "Patient responding well to treatment")
        self.treatment_start_week = 2
        self.initial_severity = 'moderately_severe'
    
    def generate_weekly_scores(self, week: int, total_weeks: int) -> List[int]:
        if week < self.treatment_start_week:
            base_severity = self.initial_severity
        elif week < 6:
            base_severity = 'moderate'
        elif week < 12:
            base_severity = 'mild'
        else:
            base_severity = 'minimal'
        
        pattern = self.generator.severity_patterns[base_severity]
        base_scores = pattern['base_scores'].copy()
        
        # Treatment response pattern: gradual improvement across all domains
        improvement_factor = max(0, (week - self.treatment_start_week) / 10)
        for i in range(9):
            if i != 8:  # Don't modify suicidal ideation for treatment response
                improvement = int(round(improvement_factor * 2))
                base_scores[i] = max(0, base_scores[i] - improvement)
        
        return self.generator.generate_correlated_scores(base_scores, pattern['correlation_strength'])

class TreatmentResistant(PatientPersona):
    """Treatment-resistant patient"""
    
    def __init__(self):
        super().__init__("David Wilson", 45, "Male", "Treatment-resistant patient")
        self.base_severity = 'moderately_severe'
        self.fluctuation_weeks = [5, 9, 13, 17]
    
    def generate_weekly_scores(self, week: int, total_weeks: int) -> List[int]:
        if week in self.fluctuation_weeks:
            base_severity = 'severe'
        else:
            base_severity = self.base_severity
        
        pattern = self.generator.severity_patterns[base_severity]
        base_scores = pattern['base_scores'].copy()
        
        # Treatment-resistant pattern: persistent high scores
        if week > 4:  # After initial treatment attempt
            for i in range(9):
                if i != 8:  # Don't modify suicidal ideation
                    base_scores[i] = min(3, base_scores[i] + 1)
        
        return self.generator.generate_correlated_scores(base_scores, pattern['correlation_strength'])

class CrisisPatient(PatientPersona):
    """Patient in crisis with escalating suicidal ideation"""
    
    def __init__(self):
        super().__init__("Jordan Smith", 22, "Male", "Patient in crisis")
        self.crisis_onset_week = 6
        self.escalation_weeks = [6, 7, 8, 9]
    
    def generate_weekly_scores(self, week: int, total_weeks: int) -> List[int]:
        if week < self.crisis_onset_week:
            base_severity = 'moderate'
        elif week in self.escalation_weeks:
            base_severity = 'severe'
        else:
            base_severity = 'moderately_severe'
        
        pattern = self.generator.severity_patterns[base_severity]
        base_scores = pattern['base_scores'].copy()
        
        # Crisis pattern: escalating suicidal ideation
        if week >= self.crisis_onset_week:
            base_scores[8] = min(3, base_scores[8] + (week - self.crisis_onset_week + 1))
            # Escalating depression symptoms
            for i in range(8):
                base_scores[i] = min(3, base_scores[i] + 1)
        
        return self.generator.generate_correlated_scores(base_scores, pattern['correlation_strength'])

class PHQ9DataGenerator:
    """Main class for generating comprehensive PHQ-9 datasets"""
    
    def __init__(self):
        self.personas = {
            'college_seasonal': CollegeStudentSeasonal(),
            'postpartum': NewMotherPostpartum(),
            'elderly_chronic': ElderlyChronicDepression(),
            'adolescent_acute': AdolescentAcuteEpisode(),
            'treatment_responder': TreatmentResponder(),
            'treatment_resistant': TreatmentResistant(),
            'crisis_patient': CrisisPatient()
        }
    
    def generate_complete_dataset(self, duration_weeks: int = 24) -> List[Dict]:
        """Generate complete dataset with all patient scenarios"""
        all_assessments = []
        
        for persona_name, persona in self.personas.items():
            logger.info(f"Generating data for {persona.name} ({persona.scenario})")
            assessments = persona.generate_assessment_series(duration_weeks)
            all_assessments.extend(assessments)
        
        return all_assessments
    
    def generate_crisis_testing_scenarios(self) -> List[Dict]:
        """Generate specific crisis testing scenarios"""
        crisis_scenarios = []
        
        # Scenario 1: Gradual escalation of suicidal ideation
        for week in range(12):
            scores = [1, 1, 1, 1, 1, 1, 1, 1, min(3, week // 3)]  # Escalating Q9
            assessment = {
                'patient_name': 'Crisis Test 1',
                'scenario': 'Gradual Q9 escalation',
                'assessment_date': (datetime.now() - timedelta(weeks=12-week)).strftime('%Y-%m-%d'),
                'week_number': week + 1,
                'q1_score': scores[0], 'q2_score': scores[1], 'q3_score': scores[2],
                'q4_score': scores[3], 'q5_score': scores[4], 'q6_score': scores[5],
                'q7_score': scores[6], 'q8_score': scores[7], 'q9_score': scores[8],
                'total_score': sum(scores),
                'severity_level': PHQ9ResponseGenerator().calculate_severity(sum(scores)),
                'q9_risk_flag': scores[8] >= 2,
                'crisis_alert': scores[8] >= 2 or sum(scores) >= 20
            }
            crisis_scenarios.append(assessment)
        
        # Scenario 2: Sudden severe increase
        for week in range(12):
            if week < 8:
                scores = [1, 1, 1, 1, 1, 1, 1, 1, 0]
            else:
                scores = [3, 3, 3, 3, 3, 3, 3, 3, 3]  # Sudden severe increase
            
            assessment = {
                'patient_name': 'Crisis Test 2',
                'scenario': 'Sudden severe increase',
                'assessment_date': (datetime.now() - timedelta(weeks=12-week)).strftime('%Y-%m-%d'),
                'week_number': week + 1,
                'q1_score': scores[0], 'q2_score': scores[1], 'q3_score': scores[2],
                'q4_score': scores[3], 'q5_score': scores[4], 'q6_score': scores[5],
                'q7_score': scores[6], 'q8_score': scores[7], 'q9_score': scores[8],
                'total_score': sum(scores),
                'severity_level': PHQ9ResponseGenerator().calculate_severity(sum(scores)),
                'q9_risk_flag': scores[8] >= 2,
                'crisis_alert': scores[8] >= 2 or sum(scores) >= 20
            }
            crisis_scenarios.append(assessment)
        
        return crisis_scenarios
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Save generated data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data saved to {filename}")
    
    def generate_summary_statistics(self, data: List[Dict]) -> Dict:
        """Generate summary statistics for the dataset"""
        total_assessments = len(data)
        patients = set(assessment['patient_name'] for assessment in data)
        
        severity_counts = {}
        crisis_alerts = 0
        q9_risk_flags = 0
        
        for assessment in data:
            severity = assessment['severity_level']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if assessment['crisis_alert']:
                crisis_alerts += 1
            
            if assessment['q9_risk_flag']:
                q9_risk_flags += 1
        
        return {
            'total_assessments': total_assessments,
            'unique_patients': len(patients),
            'severity_distribution': severity_counts,
            'crisis_alerts': crisis_alerts,
            'q9_risk_flags': q9_risk_flags,
            'crisis_rate': crisis_alerts / total_assessments * 100,
            'q9_risk_rate': q9_risk_flags / total_assessments * 100
        }

def main():
    """Generate and save comprehensive PHQ-9 dataset"""
    generator = PHQ9DataGenerator()
    
    # Generate main dataset
    logger.info("Generating comprehensive PHQ-9 dataset...")
    main_data = generator.generate_complete_dataset(duration_weeks=24)
    
    # Generate crisis testing scenarios
    logger.info("Generating crisis testing scenarios...")
    crisis_data = generator.generate_crisis_testing_scenarios()
    
    # Combine datasets
    all_data = main_data + crisis_data
    
    # Save to files
    generator.save_to_json(main_data, 'phq9_realistic_data.json')
    generator.save_to_json(crisis_data, 'phq9_crisis_scenarios.json')
    generator.save_to_json(all_data, 'phq9_complete_dataset.json')
    
    # Generate and display summary statistics
    summary = generator.generate_summary_statistics(all_data)
    logger.info("Dataset Summary:")
    logger.info(f"Total assessments: {summary['total_assessments']}")
    logger.info(f"Unique patients: {summary['unique_patients']}")
    logger.info(f"Severity distribution: {summary['severity_distribution']}")
    logger.info(f"Crisis alerts: {summary['crisis_alerts']} ({summary['crisis_rate']:.1f}%)")
    logger.info(f"Q9 risk flags: {summary['q9_risk_flags']} ({summary['q9_risk_rate']:.1f}%)")
    
    # Save summary
    with open('phq9_dataset_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info("PHQ-9 data generation completed successfully!")

if __name__ == "__main__":
    main()
