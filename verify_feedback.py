#!/usr/bin/env python3
"""
Script to verify that provider feedback is being recorded correctly in the database
"""

import sqlite3
import json
from datetime import datetime

def verify_feedback():
    """Check the feedback records in the database"""
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/mindspace_ml_new.db')
        cursor = conn.cursor()
        
        print("🔍 Checking Provider Exercise Feedback Records...")
        print("=" * 60)
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='provider_exercise_feedback'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ Table 'provider_exercise_feedback' does not exist!")
            return
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM provider_exercise_feedback")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total feedback records: {total_count}")
        
        if total_count == 0:
            print("⚠️  No feedback records found. Try submitting some feedback first!")
            return
        
        # Get recent feedback
        cursor.execute("""
            SELECT 
                pef.id,
                pef.patient_id,
                pef.provider_id,
                pef.exercise_type,
                pef.action,
                pef.feedback_text,
                pef.submitted_at,
                p.first_name,
                p.last_name,
                u.username as provider_username
            FROM provider_exercise_feedback pef
            LEFT JOIN patient p ON pef.patient_id = p.id
            LEFT JOIN user u ON pef.provider_id = u.id
            ORDER BY pef.submitted_at DESC
            LIMIT 10
        """)
        
        recent_feedback = cursor.fetchall()
        
        print(f"\n📋 Recent Feedback Records (Last 10):")
        print("-" * 60)
        
        for record in recent_feedback:
            feedback_id, patient_id, provider_id, exercise_type, action, feedback_text, submitted_at, first_name, last_name, provider_username = record
            
            print(f"ID: {feedback_id}")
            print(f"Patient: {first_name} {last_name} (ID: {patient_id})")
            print(f"Provider: {provider_username} (ID: {provider_id})")
            print(f"Exercise Type: {exercise_type}")
            print(f"Action: {action}")
            print(f"Feedback: {feedback_text}")
            print(f"Submitted: {submitted_at}")
            print("-" * 40)
        
        # Get feedback by action type
        cursor.execute("""
            SELECT action, COUNT(*) as count 
            FROM provider_exercise_feedback 
            GROUP BY action
        """)
        
        action_counts = cursor.fetchall()
        
        print(f"\n📈 Feedback by Action Type:")
        print("-" * 30)
        for action, count in action_counts:
            print(f"{action.capitalize()}: {count}")
        
        # Get feedback by exercise type
        cursor.execute("""
            SELECT exercise_type, COUNT(*) as count 
            FROM provider_exercise_feedback 
            GROUP BY exercise_type
        """)
        
        exercise_counts = cursor.fetchall()
        
        print(f"\n🏃 Exercise Type Distribution:")
        print("-" * 30)
        for exercise_type, count in exercise_counts:
            print(f"{exercise_type}: {count}")
        
        # Get feedback by patient
        cursor.execute("""
            SELECT 
                p.first_name, 
                p.last_name, 
                COUNT(*) as feedback_count
            FROM provider_exercise_feedback pef
            LEFT JOIN patient p ON pef.patient_id = p.id
            GROUP BY pef.patient_id, p.first_name, p.last_name
            ORDER BY feedback_count DESC
        """)
        
        patient_counts = cursor.fetchall()
        
        print(f"\n👥 Feedback by Patient:")
        print("-" * 30)
        for first_name, last_name, count in patient_counts:
            print(f"{first_name} {last_name}: {count} feedback records")
        
        print(f"\n✅ Database verification complete!")
        print(f"💡 This data can be used to train the reinforcement learning model")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying feedback: {str(e)}")

if __name__ == "__main__":
    verify_feedback()

