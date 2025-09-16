#!/usr/bin/env python3
"""
Start Flask app with OpenAI API key configured
"""

import os
import sys

# Set the OpenAI API key
# Set API key from environment variable
# os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

# Import and start the Flask app
if __name__ == "__main__":
    from app_ml_complete import app
    print("🚀 Starting Flask app with OpenAI API key configured...")
    print("📊 AI Session Briefing System is ready!")
    print("🌐 Navigate to: http://localhost:5000/provider/comprehensive_dashboard")
    print("📋 Go to the 'Session Prep' tab to generate AI briefings")
    app.run(debug=True, host='0.0.0.0', port=5000)

