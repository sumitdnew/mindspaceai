# Behavioral Activation System - MindSpace ML

## Overview

The Behavioral Activation System is a comprehensive, interactive tool designed to help users overcome depression and improve mental health through structured activity planning and mood correlation tracking. Built on evidence-based behavioral activation principles, this system provides a gamified approach to increasing engagement in meaningful activities.

## Key Features

### 1. Activity Planning Interface
- **Drag-and-Drop Weekly Calendar**: Intuitive weekly planning with visual activity scheduling
- **Activity Categories**: 6 main categories (Social, Physical, Creative, Self-Care, Learning, Nature)
- **Enjoyment Prediction Sliders**: Pre-activity enjoyment, energy cost, and mood boost predictions
- **Energy Cost/Benefit Estimation**: Visual tools to estimate activity energy requirements
- **Social vs. Solo Balance Tracking**: Monitor social connection vs. solo activity balance

### 2. Smart Recommendation Engine
- **AI-Powered Suggestions**: Personalized activity recommendations based on:
  - Current mood and energy levels
  - Historical activity-mood correlations
  - Weather conditions
  - Time of day preferences
  - Social preferences
- **Weather-Appropriate Activities**: Automatic filtering based on weather conditions
- **Energy-Level Matching**: Activities matched to current energy levels
- **Social Connection Opportunities**: Recommendations to reduce isolation risk
- **Seasonal Adaptations**: Activities adjusted for seasonal availability

### 3. Gamification System
- **"Activity Explorer" Achievements**: 8 different achievement categories
- **Enjoyment Prediction Accuracy Scoring**: Track how well users predict activity outcomes
- **Activity Variety Bonus Points**: Rewards for trying different types of activities
- **Social Connection Streak Tracking**: Gamified social activity engagement
- **Energy Management Skill Development**: Badges for maintaining good energy balance

### 4. Comprehensive Tracking
- **Pre-Activity Predictions**: Rate expected enjoyment, energy cost, and mood boost
- **Post-Activity Ratings**: Actual enjoyment, energy impact, and mood improvement
- **Activity Completion Rates**: Track completion patterns and trends
- **Mood Impact Correlation Analysis**: Statistical analysis of activity-mood relationships
- **Avoidance Behavior Identification**: Track and intervene on avoidance patterns

### 5. Engagement Features
- **Visual Activity Completion Celebrations**: Animated celebrations for completed activities
- **Weekly Activity Variety Reports**: Comprehensive weekly activity summaries
- **Personalized Effectiveness Insights**: AI-generated insights about what works best
- **Social Activity Matching**: Suggestions for social connection opportunities
- **Progress Visualization**: Mood correlation graphs and trend analysis

### 6. Provider Insights
- **Behavioral Activation Effectiveness Reports**: Clinical effectiveness metrics
- **Activity-Mood Correlation Analysis**: Statistical analysis for providers
- **Avoidance Pattern Identification**: Early detection of avoidance behaviors
- **Social Isolation Risk Assessment**: Monitor social connection patterns
- **Treatment Progress Measurement**: Quantified behavioral change tracking

## Database Schema

### Core Models

#### ActivityCategory
- `name`: Category name (Social, Physical, Creative, etc.)
- `description`: Category description
- `icon`: Emoji or icon representation
- `color`: Hex color code
- `energy_level`: Typical energy requirement (1-10)
- `social_factor`: Social interaction level (0-1)

#### Activity
- `name`: Activity name
- `category_id`: Reference to ActivityCategory
- `description`: Detailed activity description
- `estimated_duration`: Duration in minutes
- `energy_cost`: Energy requirement (1-10)
- `typical_enjoyment`: Expected enjoyment (1-10)
- `social_level`: Social interaction level (0-1)
- `weather_dependent`: Boolean for weather sensitivity
- `indoor_outdoor`: Indoor, outdoor, or both
- `cost_level`: Free, low, medium, or high cost
- `mood_boost_potential`: Expected mood improvement (1-10)
- `anxiety_reduction_potential`: Expected anxiety reduction (1-10)
- `depression_combat_potential`: Expected depression combat (1-10)

#### ActivityPlan
- `patient_id`: Reference to Patient
- `week_start_date`: Start of planning week
- `week_end_date`: End of planning week
- `plan_status`: Draft, active, completed, or archived
- `total_activities_planned`: Number of planned activities
- `activities_completed`: Number of completed activities
- `completion_rate`: Percentage completion
- `social_activities_count`: Count of social activities
- `physical_activities_count`: Count of physical activities
- `creative_activities_count`: Count of creative activities
- `self_care_activities_count`: Count of self-care activities

#### ScheduledActivity
- `plan_id`: Reference to ActivityPlan
- `activity_id`: Reference to Activity
- `scheduled_date`: Planned date
- `scheduled_time`: Planned time
- `duration_planned`: Planned duration
- `predicted_enjoyment`: User's enjoyment prediction
- `predicted_energy_cost`: User's energy cost prediction
- `predicted_mood_boost`: User's mood boost prediction
- `completion_status`: Scheduled, in_progress, completed, skipped, rescheduled
- `actual_enjoyment`: Actual enjoyment rating
- `actual_energy_cost`: Actual energy cost rating
- `actual_mood_boost`: Actual mood boost rating
- `actual_energy_after`: Energy level after activity

#### ActivityMoodCorrelation
- `patient_id`: Reference to Patient
- `activity_id`: Reference to Activity
- `correlation_strength`: Statistical correlation (-1 to 1)
- `sample_size`: Number of data points
- `confidence_level`: Statistical confidence (0-1)
- `average_mood_before`: Average mood before activity
- `average_mood_after`: Average mood after activity
- `average_mood_change`: Average mood improvement
- `completion_rate`: Activity completion rate
- `best_time_of_day`: Optimal time for activity
- `best_day_of_week`: Optimal day for activity

#### BehavioralActivationProgress
- `patient_id`: Reference to Patient
- `total_activities_completed`: Total completed activities
- `current_streak`: Current completion streak
- `longest_streak`: Longest completion streak
- `total_points`: Gamification points
- `level`: Current level (novice, explorer, adventurer, master)
- `prediction_accuracy_score`: Accuracy of predictions
- `variety_score`: Activity variety score
- `social_connection_score`: Social activity engagement
- `energy_management_score`: Energy balance skills

#### ActivityAchievement
- `achievement_id`: Unique achievement identifier
- `name`: Achievement name
- `description`: Achievement description
- `category`: Achievement category (explorer, predictor, social, energy, variety)
- `icon`: Achievement icon
- `points`: Points awarded
- `requirements`: JSON requirements object
- `is_hidden`: Hidden until unlocked

## API Endpoints

### Main Routes
- `GET /behavioral_activation` - Main dashboard
- `GET /behavioral_activation/plan` - Activity planning interface
- `GET /behavioral_activation/activities` - Activity library
- `GET /behavioral_activation/track/<activity_id>` - Activity tracking

### API Endpoints
- `POST /api/behavioral_activation/recommendations` - Get AI recommendations
- `GET /api/behavioral_activation/insights` - Provider insights (provider only)

## Usage Instructions

### For Patients

1. **Access the System**
   - Navigate to "🚀 Activities" in the main navigation
   - Or click "Plan Activities" from the patient dashboard

2. **Plan Your Week**
   - Use the drag-and-drop calendar to schedule activities
   - Set enjoyment predictions for each activity
   - Monitor energy balance and social connection

3. **Track Activities**
   - Complete scheduled activities
   - Rate actual enjoyment, energy cost, and mood boost
   - Compare predictions with reality
   - Earn points and achievements

4. **View Progress**
   - Check your completion streaks
   - Review mood correlation analysis
   - See personalized insights and recommendations

### For Providers

1. **Access Insights**
   - Use the provider dashboard
   - View behavioral activation effectiveness reports
   - Monitor patient progress and patterns

2. **Track Progress**
   - Review activity-mood correlations
   - Identify avoidance patterns
   - Assess social isolation risk
   - Measure treatment effectiveness

## Achievement System

### Achievement Categories

1. **Explorer Achievements**
   - First Steps: Complete first activity
   - Week Warrior: 7-day completion streak
   - Mood Booster: 5 high-mood activities
   - Avoidance Breaker: Complete avoided activity

2. **Predictor Achievements**
   - Prediction Master: Accurate predictions

3. **Social Achievements**
   - Social Butterfly: 10 social activities

4. **Energy Achievements**
   - Energy Balancer: Good energy balance

5. **Variety Achievements**
   - Variety Seeker: 5 different categories

## Technical Implementation

### Frontend Technologies
- **Bootstrap 5**: Responsive UI framework
- **SortableJS**: Drag-and-drop functionality
- **Chart.js**: Data visualization
- **Font Awesome**: Icons and visual elements

### Backend Technologies
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Database (can be upgraded to PostgreSQL/MySQL)

### Key Features
- **Real-time Updates**: Live activity tracking and progress updates
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: WCAG compliant design
- **Data Visualization**: Interactive charts and graphs
- **Gamification**: Points, badges, and progress tracking

## Data Initialization

To populate the system with sample data:

```bash
python init_behavioral_activation_data.py
```

This creates:
- 6 activity categories
- 16 sample activities
- 8 achievement types

## Clinical Benefits

### Evidence-Based Approach
- **Behavioral Activation**: Based on proven depression treatment
- **Activity Scheduling**: Structured approach to increasing engagement
- **Mood Tracking**: Correlation analysis for personalized treatment
- **Avoidance Reduction**: Systematic approach to overcoming avoidance

### Measurable Outcomes
- **Activity Completion Rates**: Quantified engagement metrics
- **Mood Improvement**: Statistical mood correlation analysis
- **Social Connection**: Measured social activity engagement
- **Energy Management**: Balanced activity scheduling
- **Treatment Progress**: Objective behavioral change measurement

## Future Enhancements

### Planned Features
- **Mobile App**: Native iOS/Android applications
- **Wearable Integration**: Smartwatch activity tracking
- **Weather API**: Real-time weather-based recommendations
- **Social Features**: Group activities and challenges
- **Advanced Analytics**: Machine learning insights
- **Provider Dashboard**: Enhanced clinical tools

### Integration Opportunities
- **Electronic Health Records**: EHR system integration
- **Telehealth Platforms**: Video consultation integration
- **Fitness Trackers**: Activity data synchronization
- **Calendar Systems**: Calendar integration for scheduling
- **Messaging Platforms**: Reminder and notification systems

## Support and Documentation

For technical support or clinical questions:
- Review the main application documentation
- Check the database schema documentation
- Contact the development team for technical issues
- Consult with mental health professionals for clinical guidance

## License and Compliance

This system is designed for mental health applications and should be used in compliance with:
- HIPAA regulations (for US healthcare)
- GDPR requirements (for EU users)
- Local mental health regulations
- Clinical practice guidelines

---

*The Behavioral Activation System is part of the MindSpace ML mental health platform, designed to provide evidence-based tools for depression treatment and mental health improvement.*
