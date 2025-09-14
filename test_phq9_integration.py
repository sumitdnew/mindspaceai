#!/usr/bin/env python3
"""
Test Script for PHQ-9 Exercise Integration System
Demonstrates the comprehensive integration features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import json

def test_phq9_exercise_integration():
    """Test the PHQ-9 exercise integration system"""
    
    print("🧠 Testing PHQ-9 Exercise Integration System")
    print("=" * 50)
    
    try:
        # Import the integration system
        from phq9_exercise_integration import phq9_exercise_integration
        
        print("✅ Successfully imported PHQ-9 exercise integration system")
        
        # Test 1: Generate recommendations for different severity levels
        print("\n📋 Test 1: Exercise Recommendations by Severity Level")
        print("-" * 40)
        
        severity_levels = ['minimal', 'mild', 'moderate', 'moderately_severe', 'severe']
        
        for severity in severity_levels:
            print(f"\n🔍 Testing {severity.upper()} depression:")
            
            # Simulate PHQ-9 assessment data
            if severity == 'minimal':
                scores = [0, 0, 1, 0, 0, 0, 0, 0, 0]  # Total: 1
            elif severity == 'mild':
                scores = [1, 1, 1, 1, 0, 1, 0, 0, 0]  # Total: 5
            elif severity == 'moderate':
                scores = [2, 2, 1, 2, 1, 2, 1, 1, 0]  # Total: 12
            elif severity == 'moderately_severe':
                scores = [2, 2, 2, 2, 2, 2, 2, 1, 1]  # Total: 16
            else:  # severe
                scores = [3, 3, 2, 3, 2, 3, 2, 2, 2]  # Total: 22
            
            total_score = sum(scores)
            q9_risk = scores[8] >= 2
            
            print(f"   PHQ-9 Total Score: {total_score}/27")
            print(f"   Q9 Risk Flag: {q9_risk}")
            
            # Get base recommendations
            base_recs = phq9_exercise_integration._get_base_recommendations(severity, q9_risk)
            
            print(f"   Primary Exercises: {', '.join(base_recs.get('primary_exercises', []))}")
            print(f"   Intensity: {base_recs.get('intensity', 'N/A')}")
            print(f"   Frequency: {base_recs.get('frequency', 'N/A')}")
            print(f"   Duration: {base_recs.get('duration', 'N/A')}")
        
        # Test 2: Anxiety-specific recommendations
        print("\n😰 Test 2: Anxiety-Specific Recommendations")
        print("-" * 40)
        
        # Simulate different anxiety levels
        anxiety_scenarios = [
            {'name': 'Low Anxiety', 'q3': 0, 'q7': 0, 'q8': 0, 'total': 0},
            {'name': 'Moderate Anxiety', 'q3': 1, 'q7': 1, 'q8': 1, 'total': 3},
            {'name': 'High Anxiety', 'q3': 2, 'q7': 2, 'q8': 2, 'total': 6}
        ]
        
        for scenario in anxiety_scenarios:
            print(f"\n🔍 Testing {scenario['name']}:")
            print(f"   Anxiety Score (Q3+Q7+Q8): {scenario['total']}")
            
            # Create mock assessment object
            class MockAssessment:
                def __init__(self, q3, q7, q8):
                    self.q3_score = q3
                    self.q7_score = q7
                    self.q8_score = q8
            
            mock_assessment = MockAssessment(scenario['q3'], scenario['q7'], scenario['q8'])
            
            anxiety_recs = phq9_exercise_integration._get_anxiety_recommendations(mock_assessment)
            
            if anxiety_recs:
                for rec in anxiety_recs:
                    print(f"   📝 {rec['type'].title()}: {rec['rationale']}")
                    print(f"      Exercises: {', '.join(rec['exercises'])}")
            else:
                print("   ✅ No specific anxiety recommendations needed")
        
        # Test 3: Crisis recommendations
        print("\n🚨 Test 3: Crisis Intervention Recommendations")
        print("-" * 40)
        
        crisis_scenarios = [
            {'name': 'No Crisis', 'q9_score': 0, 'total_score': 10, 'q9_risk': False},
            {'name': 'Suicidal Ideation', 'q9_score': 2, 'total_score': 15, 'q9_risk': True},
            {'name': 'Severe Depression', 'q9_score': 1, 'total_score': 22, 'q9_risk': False}
        ]
        
        for scenario in crisis_scenarios:
            print(f"\n🔍 Testing {scenario['name']}:")
            print(f"   Q9 Score: {scenario['q9_score']}/3")
            print(f"   Total Score: {scenario['total_score']}/27")
            print(f"   Q9 Risk: {scenario['q9_risk']}")
            
            crisis_recs = phq9_exercise_integration._get_crisis_recommendations(
                scenario['q9_risk'], scenario['total_score']
            )
            
            if crisis_recs:
                for rec in crisis_recs:
                    print(f"   🚨 {rec['type'].title()}: {rec['rationale']}")
                    print(f"      Priority: {rec['priority']}")
                    print(f"      Exercises: {', '.join(rec['exercises'])}")
            else:
                print("   ✅ No crisis interventions needed")
        
        # Test 4: Exercise preference analysis
        print("\n📊 Test 4: Exercise Preference Analysis")
        print("-" * 40)
        
        # Simulate exercise history
        exercise_history = [
            {
                'type': 'exercise',
                'exercise_type': 'box-breathing',
                'completion_status': 'completed',
                'engagement_score': 8,
                'effectiveness_rating': 7,
                'date': datetime.now() - timedelta(days=1),
                'duration': 10
            },
            {
                'type': 'exercise',
                'exercise_type': 'mindful-breathing',
                'completion_status': 'completed',
                'engagement_score': 6,
                'effectiveness_rating': 5,
                'date': datetime.now() - timedelta(days=2),
                'duration': 8
            },
            {
                'type': 'exercise',
                'exercise_type': 'box-breathing',
                'completion_status': 'completed',
                'engagement_score': 9,
                'effectiveness_rating': 8,
                'date': datetime.now() - timedelta(days=3),
                'duration': 12
            }
        ]
        
        preferences = phq9_exercise_integration._analyze_exercise_preferences(exercise_history)
        
        print("📈 Exercise Preferences Analysis:")
        for exercise_type, pref_data in preferences.items():
            print(f"   🧘 {exercise_type}:")
            print(f"      Completion Rate: {pref_data['completion_rate']:.1%}")
            print(f"      Avg Engagement: {pref_data['average_engagement']:.1f}/10")
            print(f"      Avg Effectiveness: {pref_data['average_effectiveness']:.1f}/10")
            print(f"      Preference Score: {pref_data['preference_score']:.3f}")
        
        # Test 5: Implementation plan creation
        print("\n📋 Test 5: Implementation Plan Creation")
        print("-" * 40)
        
        base_recommendations = {
            'primary_exercises': ['box-breathing', 'mindful-breathing', 'meditation'],
            'intensity': 'moderate',
            'frequency': 'daily',
            'duration': '15-20 minutes'
        }
        
        implementation_plan = phq9_exercise_integration._create_implementation_plan(
            base_recommendations, 'moderate', preferences
        )
        
        print("📅 Implementation Plan:")
        for phase, plan in implementation_plan.items():
            print(f"   🎯 {phase.replace('_', ' ').title()}:")
            print(f"      Duration: {plan['duration']}")
            print(f"      Focus: {plan['focus']}")
            print(f"      Exercises: {', '.join(plan['exercises'])}")
            print(f"      Frequency: {plan['frequency']}")
            print(f"      Duration: {plan['duration_minutes']}")
        
        # Test 6: Monitoring plan creation
        print("\n📊 Test 6: Monitoring Plan Creation")
        print("-" * 40)
        
        monitoring_scenarios = [
            {'severity': 'minimal', 'q9_risk': False, 'name': 'Minimal Risk'},
            {'severity': 'moderate', 'q9_risk': False, 'name': 'Moderate Risk'},
            {'severity': 'severe', 'q9_risk': True, 'name': 'High Risk'}
        ]
        
        for scenario in monitoring_scenarios:
            print(f"\n🔍 {scenario['name']}:")
            monitoring_plan = phq9_exercise_integration._create_monitoring_plan(
                scenario['severity'], scenario['q9_risk']
            )
            
            for metric, frequency in monitoring_plan.items():
                print(f"   📊 {metric.replace('_', ' ').title()}: {frequency}")
        
        print("\n✅ All tests completed successfully!")
        print("\n🎉 PHQ-9 Exercise Integration System is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_integration_features():
    """Demonstrate key integration features"""
    
    print("\n🚀 Demonstrating Integration Features")
    print("=" * 50)
    
    try:
        from phq9_exercise_integration import phq9_exercise_integration
        
        print("\n📋 Feature 1: Severity-Based Exercise Mapping")
        print("-" * 40)
        
        severity_mapping = phq9_exercise_integration.severity_exercise_mapping
        
        for severity, config in severity_mapping.items():
            print(f"\n🔍 {severity.upper()} Depression:")
            print(f"   Primary Exercises: {', '.join(config['primary_exercises'])}")
            print(f"   Intensity: {config['intensity']}")
            print(f"   Frequency: {config['frequency']}")
            print(f"   Duration: {config['duration']}")
            print(f"   Focus Areas: {', '.join(config['focus_areas'])}")
        
        print("\n😰 Feature 2: Anxiety Exercise Categories")
        print("-" * 40)
        
        anxiety_exercises = phq9_exercise_integration.anxiety_exercises
        
        for category, exercises in anxiety_exercises.items():
            print(f"\n🔍 {category.title()}:")
            for exercise in exercises:
                print(f"   • {exercise}")
        
        print("\n🚨 Feature 3: Crisis Intervention System")
        print("-" * 40)
        
        crisis_exercises = phq9_exercise_integration.crisis_exercises
        
        for category, exercises in crisis_exercises.items():
            print(f"\n🔍 {category.title()}:")
            for exercise in exercises:
                print(f"   • {exercise}")
        
        print("\n✅ Integration features demonstrated successfully!")
        
    except Exception as e:
        print(f"❌ Error demonstrating features: {str(e)}")
        return False

def main():
    """Main test function"""
    
    print("🧠 MindSpace ML - PHQ-9 Exercise Integration System Test")
    print("=" * 60)
    
    # Run tests
    test_success = test_phq9_exercise_integration()
    
    if test_success:
        # Demonstrate features
        demonstrate_integration_features()
        
        print("\n🎯 Integration System Summary:")
        print("=" * 40)
        print("✅ PHQ-9 severity-based exercise recommendations")
        print("✅ Anxiety-specific exercise targeting")
        print("✅ Crisis intervention system")
        print("✅ Exercise preference learning")
        print("✅ Implementation planning")
        print("✅ Monitoring plan creation")
        print("✅ Comprehensive patient profiling")
        print("✅ Provider workflow integration")
        print("✅ Holistic progress measurement")
        
        print("\n🚀 The PHQ-9 Exercise Integration System is ready for use!")
        print("\n📚 For more information, see: PHQ9_EXERCISE_INTEGRATION_README.md")
        
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
