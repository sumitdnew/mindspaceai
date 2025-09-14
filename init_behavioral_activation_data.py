#!/usr/bin/env python3
"""
Initialize Behavioral Activation Data
Populates the database with activity categories, activities, and achievements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_ml_complete import app, db, ActivityCategory, Activity, ActivityAchievement
import json

def create_activity_categories():
    """Create activity categories"""
    categories = [
        {
            'name': 'Social',
            'description': 'Activities involving interaction with others',
            'icon': '👥',
            'color': '#2196F3',
            'energy_level': 6,
            'social_factor': 0.9
        },
        {
            'name': 'Physical',
            'description': 'Exercise and movement activities',
            'icon': '🏃‍♂️',
            'color': '#4CAF50',
            'energy_level': 7,
            'social_factor': 0.3
        },
        {
            'name': 'Creative',
            'description': 'Artistic and creative expression activities',
            'icon': '🎨',
            'color': '#9C27B0',
            'energy_level': 4,
            'social_factor': 0.2
        },
        {
            'name': 'Self-Care',
            'description': 'Personal wellness and relaxation activities',
            'icon': '🧘‍♀️',
            'color': '#FF9800',
            'energy_level': 3,
            'social_factor': 0.1
        },
        {
            'name': 'Learning',
            'description': 'Educational and skill-building activities',
            'icon': '📚',
            'color': '#607D8B',
            'energy_level': 5,
            'social_factor': 0.2
        },
        {
            'name': 'Nature',
            'description': 'Outdoor and nature-based activities',
            'icon': '🌿',
            'color': '#8BC34A',
            'energy_level': 5,
            'social_factor': 0.4
        }
    ]
    
    for cat_data in categories:
        category = ActivityCategory.query.filter_by(name=cat_data['name']).first()
        if not category:
            category = ActivityCategory(**cat_data)
            db.session.add(category)
            print(f"✅ Created category: {cat_data['name']}")
        else:
            print(f"⚠️ Category already exists: {cat_data['name']}")
    
    db.session.commit()

def create_activities():
    """Create sample activities"""
    activities = [
        # Social Activities
        {
            'name': 'Call a Friend',
            'category_name': 'Social',
            'description': 'Reach out to a friend or family member for a chat',
            'estimated_duration': 30,
            'energy_cost': 3,
            'typical_enjoyment': 8,
            'social_level': 0.9,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'free',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'any',
            'mood_boost_potential': 8,
            'anxiety_reduction_potential': 7,
            'depression_combat_potential': 8
        },
        {
            'name': 'Join a Group Activity',
            'category_name': 'Social',
            'description': 'Participate in a group class, club, or social event',
            'estimated_duration': 90,
            'energy_cost': 6,
            'typical_enjoyment': 7,
            'social_level': 1.0,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'low',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'evening',
            'mood_boost_potential': 8,
            'anxiety_reduction_potential': 6,
            'depression_combat_potential': 9
        },
        {
            'name': 'Volunteer',
            'category_name': 'Social',
            'description': 'Help others through community service',
            'estimated_duration': 120,
            'energy_cost': 5,
            'typical_enjoyment': 8,
            'social_level': 0.8,
            'weather_dependent': False,
            'indoor_outdoor': 'both',
            'cost_level': 'free',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'afternoon',
            'mood_boost_potential': 9,
            'anxiety_reduction_potential': 7,
            'depression_combat_potential': 9
        },
        
        # Physical Activities
        {
            'name': 'Walking',
            'category_name': 'Physical',
            'description': 'Take a leisurely walk around your neighborhood',
            'estimated_duration': 30,
            'energy_cost': 4,
            'typical_enjoyment': 7,
            'social_level': 0.2,
            'weather_dependent': True,
            'indoor_outdoor': 'outdoor',
            'cost_level': 'free',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'morning',
            'mood_boost_potential': 7,
            'anxiety_reduction_potential': 8,
            'depression_combat_potential': 8
        },
        {
            'name': 'Yoga',
            'category_name': 'Physical',
            'description': 'Practice gentle yoga poses and stretching',
            'estimated_duration': 45,
            'energy_cost': 3,
            'typical_enjoyment': 6,
            'social_level': 0.1,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'free',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'morning',
            'mood_boost_potential': 7,
            'anxiety_reduction_potential': 9,
            'depression_combat_potential': 7
        },
        {
            'name': 'Dancing',
            'category_name': 'Physical',
            'description': 'Dance to your favorite music at home',
            'estimated_duration': 20,
            'energy_cost': 6,
            'typical_enjoyment': 8,
            'social_level': 0.1,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'free',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'any',
            'mood_boost_potential': 8,
            'anxiety_reduction_potential': 7,
            'depression_combat_potential': 8
        },
        
        # Creative Activities
        {
            'name': 'Drawing/Painting',
            'category_name': 'Creative',
            'description': 'Express yourself through art',
            'estimated_duration': 60,
            'energy_cost': 3,
            'typical_enjoyment': 7,
            'social_level': 0.1,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'low',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'afternoon',
            'mood_boost_potential': 7,
            'anxiety_reduction_potential': 8,
            'depression_combat_potential': 6
        },
        {
            'name': 'Writing',
            'category_name': 'Creative',
            'description': 'Write stories, poetry, or journal entries',
            'estimated_duration': 45,
            'energy_cost': 4,
            'typical_enjoyment': 6,
            'social_level': 0.0,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'free',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'evening',
            'mood_boost_potential': 6,
            'anxiety_reduction_potential': 7,
            'depression_combat_potential': 7
        },
        {
            'name': 'Cooking',
            'category_name': 'Creative',
            'description': 'Prepare a meal or try a new recipe',
            'estimated_duration': 60,
            'energy_cost': 5,
            'typical_enjoyment': 7,
            'social_level': 0.2,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'low',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'afternoon',
            'mood_boost_potential': 6,
            'anxiety_reduction_potential': 6,
            'depression_combat_potential': 5
        },
        
        # Self-Care Activities
        {
            'name': 'Bubble Bath',
            'category_name': 'Self-Care',
            'description': 'Relax in a warm bath with bubbles or bath salts',
            'estimated_duration': 30,
            'energy_cost': 2,
            'typical_enjoyment': 8,
            'social_level': 0.0,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'low',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'evening',
            'mood_boost_potential': 7,
            'anxiety_reduction_potential': 9,
            'depression_combat_potential': 6
        },
        {
            'name': 'Reading',
            'category_name': 'Self-Care',
            'description': 'Read a book, magazine, or interesting article',
            'estimated_duration': 45,
            'energy_cost': 2,
            'typical_enjoyment': 7,
            'social_level': 0.0,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'free',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'evening',
            'mood_boost_potential': 6,
            'anxiety_reduction_potential': 8,
            'depression_combat_potential': 5
        },
        {
            'name': 'Meditation',
            'category_name': 'Self-Care',
            'description': 'Practice mindfulness or guided meditation',
            'estimated_duration': 20,
            'energy_cost': 1,
            'typical_enjoyment': 5,
            'social_level': 0.0,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'free',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'morning',
            'mood_boost_potential': 6,
            'anxiety_reduction_potential': 9,
            'depression_combat_potential': 6
        },
        
        # Learning Activities
        {
            'name': 'Online Course',
            'category_name': 'Learning',
            'description': 'Take an online class or tutorial',
            'estimated_duration': 60,
            'energy_cost': 5,
            'typical_enjoyment': 6,
            'social_level': 0.1,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'low',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'afternoon',
            'mood_boost_potential': 6,
            'anxiety_reduction_potential': 5,
            'depression_combat_potential': 7
        },
        {
            'name': 'Puzzle Solving',
            'category_name': 'Learning',
            'description': 'Work on a crossword, sudoku, or jigsaw puzzle',
            'estimated_duration': 30,
            'energy_cost': 3,
            'typical_enjoyment': 6,
            'social_level': 0.1,
            'weather_dependent': False,
            'indoor_outdoor': 'indoor',
            'cost_level': 'low',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'any',
            'mood_boost_potential': 5,
            'anxiety_reduction_potential': 6,
            'depression_combat_potential': 4
        },
        
        # Nature Activities
        {
            'name': 'Gardening',
            'category_name': 'Nature',
            'description': 'Plant flowers, herbs, or tend to a garden',
            'estimated_duration': 45,
            'energy_cost': 5,
            'typical_enjoyment': 7,
            'social_level': 0.1,
            'weather_dependent': True,
            'indoor_outdoor': 'outdoor',
            'cost_level': 'low',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall']),
            'time_of_day_preference': 'morning',
            'mood_boost_potential': 7,
            'anxiety_reduction_potential': 8,
            'depression_combat_potential': 7
        },
        {
            'name': 'Bird Watching',
            'category_name': 'Nature',
            'description': 'Observe birds in your backyard or local park',
            'estimated_duration': 30,
            'energy_cost': 2,
            'typical_enjoyment': 6,
            'social_level': 0.1,
            'weather_dependent': True,
            'indoor_outdoor': 'outdoor',
            'cost_level': 'free',
            'seasonal_availability': json.dumps(['spring', 'summer', 'fall', 'winter']),
            'time_of_day_preference': 'morning',
            'mood_boost_potential': 6,
            'anxiety_reduction_potential': 7,
            'depression_combat_potential': 5
        }
    ]
    
    for activity_data in activities:
        # Get category
        category = ActivityCategory.query.filter_by(name=activity_data['category_name']).first()
        if not category:
            print(f"⚠️ Category not found: {activity_data['category_name']}")
            continue
        
        # Check if activity already exists
        existing_activity = Activity.query.filter_by(name=activity_data['name']).first()
        if existing_activity:
            print(f"⚠️ Activity already exists: {activity_data['name']}")
            continue
        
        # Create activity
        activity = Activity(
            activity_id=f"activity_{activity_data['name'].lower().replace(' ', '_').replace('/', '_')}",
            name=activity_data['name'],
            category_id=category.id,
            description=activity_data['description'],
            estimated_duration=activity_data['estimated_duration'],
            energy_cost=activity_data['energy_cost'],
            typical_enjoyment=activity_data['typical_enjoyment'],
            social_level=activity_data['social_level'],
            weather_dependent=activity_data['weather_dependent'],
            indoor_outdoor=activity_data['indoor_outdoor'],
            cost_level=activity_data['cost_level'],
            seasonal_availability=activity_data['seasonal_availability'],
            time_of_day_preference=activity_data['time_of_day_preference'],
            mood_boost_potential=activity_data['mood_boost_potential'],
            anxiety_reduction_potential=activity_data['anxiety_reduction_potential'],
            depression_combat_potential=activity_data['depression_combat_potential']
        )
        
        db.session.add(activity)
        print(f"✅ Created activity: {activity_data['name']}")
    
    db.session.commit()

def create_achievements():
    """Create achievement system"""
    achievements = [
        {
            'achievement_id': 'first_activity',
            'name': 'First Steps',
            'description': 'Complete your first activity',
            'category': 'explorer',
            'icon': '🎯',
            'points': 10,
            'requirements': json.dumps({'activities_completed': 1}),
            'is_hidden': False
        },
        {
            'achievement_id': 'week_streak',
            'name': 'Week Warrior',
            'description': 'Complete activities for 7 days in a row',
            'category': 'explorer',
            'icon': '🔥',
            'points': 50,
            'requirements': json.dumps({'streak_days': 7}),
            'is_hidden': False
        },
        {
            'achievement_id': 'prediction_master',
            'name': 'Prediction Master',
            'description': 'Accurately predict enjoyment for 10 activities',
            'category': 'predictor',
            'icon': '🔮',
            'points': 30,
            'requirements': json.dumps({'accurate_predictions': 10}),
            'is_hidden': False
        },
        {
            'achievement_id': 'social_butterfly',
            'name': 'Social Butterfly',
            'description': 'Complete 10 social activities',
            'category': 'social',
            'icon': '🦋',
            'points': 40,
            'requirements': json.dumps({'social_activities': 10}),
            'is_hidden': False
        },
        {
            'achievement_id': 'energy_balancer',
            'name': 'Energy Balancer',
            'description': 'Maintain good energy balance for a week',
            'category': 'energy',
            'icon': '⚖️',
            'points': 25,
            'requirements': json.dumps({'energy_balance_week': 7}),
            'is_hidden': False
        },
        {
            'achievement_id': 'variety_seeker',
            'name': 'Variety Seeker',
            'description': 'Try activities from 5 different categories',
            'category': 'variety',
            'icon': '🌈',
            'points': 35,
            'requirements': json.dumps({'categories_tried': 5}),
            'is_hidden': False
        },
        {
            'achievement_id': 'mood_booster',
            'name': 'Mood Booster',
            'description': 'Complete 5 activities that significantly improved your mood',
            'category': 'explorer',
            'icon': '😊',
            'points': 45,
            'requirements': json.dumps({'high_mood_activities': 5}),
            'is_hidden': False
        },
        {
            'achievement_id': 'avoidance_breaker',
            'name': 'Avoidance Breaker',
            'description': 'Complete an activity you initially wanted to avoid',
            'category': 'explorer',
            'icon': '💪',
            'points': 20,
            'requirements': json.dumps({'avoided_activity_completed': 1}),
            'is_hidden': False
        }
    ]
    
    for achievement_data in achievements:
        achievement = ActivityAchievement.query.filter_by(achievement_id=achievement_data['achievement_id']).first()
        if not achievement:
            achievement = ActivityAchievement(**achievement_data)
            db.session.add(achievement)
            print(f"✅ Created achievement: {achievement_data['name']}")
        else:
            print(f"⚠️ Achievement already exists: {achievement_data['name']}")
    
    db.session.commit()

def main():
    """Initialize all behavioral activation data"""
    print("🚀 Initializing Behavioral Activation Data...")
    
    with app.app_context():
        print("\n📂 Creating activity categories...")
        create_activity_categories()
        
        print("\n🎯 Creating activities...")
        create_activities()
        
        print("\n🏆 Creating achievements...")
        create_achievements()
        
        print("\n✅ Behavioral activation data initialization complete!")
        print(f"📊 Created {ActivityCategory.query.count()} categories")
        print(f"🎯 Created {Activity.query.count()} activities")
        print(f"🏆 Created {ActivityAchievement.query.count()} achievements")

if __name__ == '__main__':
    main()
