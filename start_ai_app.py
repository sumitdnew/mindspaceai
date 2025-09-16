#!/usr/bin/env python3
"""
Start Flask app with OpenAI API key - No .env file dependency
"""

import os
import sys

# Set the OpenAI API key directly
# Set API key from environment variable
# os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

print("🔧 Setting OpenAI API key...")
print("✅ API key configured")

# Test the AI system first
try:
    from ai_session_briefing_system import AISessionBriefingSystem
    ai_system = AISessionBriefingSystem()
    print("✅ AI Briefing System initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing AI system: {e}")
    sys.exit(1)

# Import and start the Flask app
from app_ml_complete import app

if __name__ == "__main__":
    print("🚀 Starting Flask app with AI briefing system...")
    print("📊 AI Session Briefing System is ready!")
    print("🌐 Navigate to: http://localhost:5000/provider/comprehensive_dashboard")
    print("📋 Go to the 'Session Prep' tab to generate AI briefings")
    print("👤 Login: provider1 / password123")
    print("=" * 60)
    
    # Start the app without debug mode to avoid .env issues
    app.run(debug=False, host='0.0.0.0', port=5000)

