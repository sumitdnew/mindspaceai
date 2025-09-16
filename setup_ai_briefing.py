#!/usr/bin/env python3
"""
Setup script for AI Session Briefing System
"""

import os
import sys

def setup_environment():
    """Set up environment variables for AI briefing system"""
    print("🔧 Setting up AI Session Briefing System...")
    
    # Check if OpenAI API key is already set
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OpenAI API key already configured")
        return True
    
    # Prompt for API key
    print("\n📝 OpenAI API Key Configuration")
    print("You can get your API key from: https://platform.openai.com/api-keys")
    
    api_key = input("\nEnter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. AI briefing will use fallback mode.")
        return False
    
    # Set environment variable
    os.environ['OPENAI_API_KEY'] = api_key
    
    # Optionally save to .env file
    save_to_env = input("Save API key to .env file? (y/n): ").lower().strip()
    if save_to_env == 'y':
        try:
            with open('.env', 'a') as f:
                f.write(f"\nOPENAI_API_KEY={api_key}\n")
            print("✅ API key saved to .env file")
        except Exception as e:
            print(f"⚠️ Could not save to .env file: {e}")
    
    print("✅ OpenAI API key configured successfully!")
    return True

def test_connection():
    """Test OpenAI API connection"""
    print("\n🧪 Testing OpenAI API connection...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        
        print("✅ OpenAI API connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI Session Briefing System Setup")
    print("=" * 40)
    
    # Set up environment
    if not setup_environment():
        print("\n⚠️ Setup incomplete. AI briefing will use fallback mode.")
        return
    
    # Test connection
    if test_connection():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start your Flask application")
        print("2. Navigate to the Comprehensive Provider Dashboard")
        print("3. Go to the Session Prep tab")
        print("4. Select a patient and click 'Generate AI Briefing'")
    else:
        print("\n💥 Setup failed. Please check your API key and try again.")

if __name__ == "__main__":
    main()

