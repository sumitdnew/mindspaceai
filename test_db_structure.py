#!/usr/bin/env python3
"""
Test script to verify database structure and new models
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_ml_complete import app, db
from sqlalchemy import inspect

def test_database_structure():
    """Test the database structure and verify all models exist"""
    
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("📊 Database Tables Found:")
        for table in sorted(tables):
            print(f"  - {table}")
        
        print(f"\n✅ Total tables: {len(tables)}")
        
        # Check for specific new tables
        new_tables = [
            'exercise', 'exercise_session', 'mood_entry', 
            'thought_record', 'mindfulness_session', 'exercise_streak',
            'achievement_unlocked', 'personalization_data'
        ]
        
        print(f"\n🔍 Checking for new exercise models:")
        for table in new_tables:
            if table in tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - MISSING")
        
        # Check table columns for mood_entry
        if 'mood_entry' in tables:
            print(f"\n📋 mood_entry table columns:")
            columns = inspector.get_columns('mood_entry')
            for column in columns:
                print(f"  - {column['name']}: {column['type']}")

if __name__ == "__main__":
    test_database_structure()
