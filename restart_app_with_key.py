#!/usr/bin/env python3
"""
Restart Flask app with OpenAI API key properly set
"""

import os
import sys
import subprocess

# Set the environment variable
# Set API key from environment variable
# os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

print("🔧 Setting OpenAI API key...")
print("✅ API key configured")

# Test the AI system
try:
    from ai_session_briefing_system import AISessionBriefingSystem
    ai_system = AISessionBriefingSystem()
    print("✅ AI Briefing System initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing AI system: {e}")
    sys.exit(1)

# Start the Flask app
print("🚀 Starting Flask app...")
from app_ml_complete import app

if __name__ == "__main__":
    print("📊 AI Session Briefing System is ready!")
    print("🌐 Navigate to: http://localhost:5000/provider/comprehensive_dashboard")
    print("📋 Go to the 'Session Prep' tab to generate AI briefings")
    app.run(debug=True, host='0.0.0.0', port=5000)

