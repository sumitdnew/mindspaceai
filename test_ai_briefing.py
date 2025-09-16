#!/usr/bin/env python3
"""
Test script for AI Session Briefing System
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append('.')

# Set up environment
os.environ['OPENAI_API_KEY'] = input("Enter your OpenAI API key: ")

try:
    from ai_session_briefing_system import AISessionBriefingSystem
    from app_ml_complete import app, db, Patient, ExerciseSession, MoodEntry, ThoughtRecord, CrisisAlert, PHQ9Assessment
    
    def test_ai_briefing():
        """Test the AI briefing system"""
        print("🧪 Testing AI Session Briefing System...")
        
        # Initialize the system
        ai_system = AISessionBriefingSystem()
        
        # Test with a sample patient ID (assuming patient ID 1 exists)
        patient_id = 1
        
        print(f"📊 Generating briefing for patient ID: {patient_id}")
        
        try:
            # Generate briefing
            briefing = ai_system.generate_session_briefing(patient_id)
            
            if briefing.get('error'):
                print(f"❌ Error: {briefing['error']}")
                return False
            
            print("✅ AI Briefing generated successfully!")
            print(f"📋 Patient: {briefing.get('patient_name', 'Unknown')}")
            print(f"📈 Data Summary: {briefing.get('data_summary', {})}")
            
            # Display sections if available
            sections = briefing.get('sections', {})
            if sections:
                print("\n📑 Briefing Sections:")
                for section_name, content in sections.items():
                    print(f"\n--- {section_name} ---")
                    print(content[:200] + "..." if len(content) > 200 else content)
            
            # Display key insights
            insights = briefing.get('key_insights', [])
            if insights:
                print("\n💡 Key Insights:")
                for insight in insights:
                    print(f"• {insight}")
            
            # Display recommendations
            recommendations = briefing.get('recommendations', [])
            if recommendations:
                print("\n🎯 Recommendations:")
                for rec in recommendations:
                    print(f"• {rec}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating briefing: {str(e)}")
            return False
    
    if __name__ == "__main__":
        with app.app_context():
            success = test_ai_briefing()
            if success:
                print("\n🎉 AI Briefing System test completed successfully!")
            else:
                print("\n💥 AI Briefing System test failed!")
                sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed and the database is set up.")
    sys.exit(1)

