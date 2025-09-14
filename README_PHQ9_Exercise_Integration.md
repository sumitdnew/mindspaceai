# PHQ-9 Exercise Integration System

A comprehensive system that connects PHQ-9 depression severity scores to personalized, adaptive daily exercise recommendations with continuous optimization based on patient response patterns.

## System Overview

This system transforms PHQ-9 assessment results into actionable, personalized exercise recommendations that adapt in real-time based on patient engagement, mood trends, and clinical safety requirements.

## Core Components

### 1. PHQ-9 Exercise Integration (`phq9_exercise_integration.py`)
**Severity-based exercise prescription system** that maps PHQ-9 scores to personalized exercise plans:

- **Minimal Depression (0-4)**: Maintenance focus with light exercises
- **Mild Depression (5-9)**: Skill building with moderate engagement
- **Moderate Depression (10-14)**: Active treatment with high engagement
- **Moderately Severe (15-19)**: Crisis management with intensive monitoring
- **Severe Depression (20-27)**: Crisis intervention with immediate provider alerts

**Key Features:**
- Adaptive recommendation logic based on improvement/deterioration detection
- Exercise scheduling algorithms for optimal timing
- Feedback loop systems for continuous optimization
- Provider integration with real-time alerts

### 2. Exercise Execution Engine (`exercise_execution_engine.py`)
**Real-time exercise delivery and adaptation system** that:

- Executes exercises with patient-specific adaptations
- Monitors crisis triggers and provides immediate intervention
- Adapts exercise difficulty based on engagement patterns
- Saves session data for continuous learning
- Generates next recommendations based on performance

**Exercise Types:**
- Mood check-ins (30 seconds)
- CBT thought records (10 minutes)
- Mindfulness exercises (5 minutes)
- Behavioral activation (15 minutes)
- Crisis monitoring (2 minutes)
- Breathing & grounding (3 minutes)

### 3. Provider Dashboard (`provider_dashboard.py`)
**Comprehensive monitoring and reporting system** that provides:

- **Daily Dashboard**: Real-time patient status and alerts
- **Crisis Escalation Reports**: Immediate attention requirements
- **Weekly Reports**: Comprehensive progress analysis
- **Patient Detailed Views**: Individual patient insights
- **Engagement Trends**: Practice-wide analytics

**Alert System:**
- **Red Alerts**: Crisis situations requiring immediate action
- **Yellow Alerts**: Concerning trends needing attention
- **Green Status**: Good progress and engagement

### 4. Patient Motivation System (`patient_motivation_system.py`)
**Smart notification and progress visualization system** that:

- Generates personalized smart notifications
- Creates progress visualizations and milestones
- Tracks engagement patterns and achievements
- Provides adaptive encouragement
- Celebrates progress and skill development

**Motivation Features:**
- Personalized timing based on patient activity patterns
- Progress-based messaging
- Milestone celebrations
- Engagement-based encouragement

### 5. Main Integration System (`phq9_exercise_main.py`)
**Orchestrates all components** to provide:

- Complete PHQ-9 assessment processing workflow
- Exercise session execution with real-time adaptation
- Comprehensive provider insights
- Patient progress reports
- Crisis situation handling

## System Architecture

```
PHQ-9 Assessment → Integration Engine → Exercise Recommendations
                                        ↓
Provider Dashboard ← Execution Engine ← Exercise Sessions
                                        ↓
Motivation System ← Progress Tracking ← Patient Engagement
```

## Key Features

### 1. Severity-Based Exercise Prescription
- **Minimal (0-4)**: Daily mood check-in, weekly wellness tracking
- **Mild (5-9)**: Daily mood tracking + CBT, weekly mindfulness
- **Moderate (10-14)**: Daily behavioral activation, 5x/week mindfulness
- **Moderately Severe (15-19)**: Crisis monitoring, 2x daily safety checks
- **Severe (20-27)**: Crisis intervention, multiple daily safety checks

### 2. Adaptive Recommendation Logic
**Improvement Detection:**
- 7+ consecutive days of mood improvement → reduce frequency by 25%
- >85% exercise completion for 2 weeks → offer advanced exercises
- Crisis exercise usage drops to zero for 2 weeks → step down intensity

**Deterioration Detection:**
- 5+ days of declining mood → increase exercise frequency
- <50% exercise completion → switch to easier exercises
- >3 crisis exercises in one week → immediate provider alert

### 3. Exercise Scheduling Algorithm
- **Morning (8-10 AM)**: Quick mood check-in, breathing exercises
- **Midday (12-2 PM)**: Micro-moment assessment, thought records
- **Evening (6-8 PM)**: Activity completion review, planning
- **Emergency (24/7)**: Crisis breathing, grounding techniques

### 4. Feedback Loop System
**Weekly Analysis:**
- Mood improvement calculation
- Exercise effectiveness measurement
- Completion rate analysis
- Next week recommendations

**Monthly PHQ-9 Preparation:**
- Engagement trend analysis
- Mood-exercise correlation
- PHQ-9 score prediction
- Provider progress summary

### 5. Provider Integration
**Daily Dashboard:**
- Red alerts for crisis situations
- Yellow alerts for concerning trends
- Green status for good progress

**Weekly Reports:**
- Exercise completion summaries
- Effectiveness metrics
- Mood trend analysis
- Recommended adjustments

**Crisis Escalation:**
- Immediate notifications for severe deterioration
- Automatic urgent appointment scheduling
- Crisis resource recommendations

### 6. Patient Motivation System
**Smart Notifications:**
- Personalized timing based on activity patterns
- Progress-based motivational messages
- Reminder escalation (gentle → concerned → provider alert)

**Progress Visualization:**
- Exercise-mood correlation display
- Milestone celebrations
- Skill development progress

**Adaptive Encouragement:**
- Mood-based messaging tone
- Effective exercise highlighting
- PHQ-9 improvement connections

### 7. Clinical Safety Protocols
**Crisis Override Protocols:**
- Suicidal ideation triggers immediate intensive plan
- Provider notification within 2 hours
- Emergency contact integration

**Treatment Boundaries:**
- Exercises supplement but never replace provider care
- Clear contact guidelines
- Escalation protocols

**Evidence-Based Adaptations:**
- Clinical research-based modifications
- Provider override capabilities
- Regular effectiveness validation

## Usage Examples

### 1. Process PHQ-9 Assessment
```python
from phq9_exercise_main import phq9_exercise_main

# Process a new PHQ-9 assessment
result = phq9_exercise_main.process_phq9_assessment(patient_id=1, assessment_id=1)
print(result)
```

### 2. Execute Exercise Session
```python
# Execute a mood check-in exercise
result = phq9_exercise_main.execute_exercise_session(
    patient_id=1, 
    exercise_type='mood_check_in'
)
print(result)
```

### 3. Get Provider Insights
```python
# Get comprehensive provider dashboard
insights = phq9_exercise_main.get_provider_insights()
print(insights)
```

### 4. Generate Patient Report
```python
# Generate detailed patient report
report = phq9_exercise_main.generate_patient_report(patient_id=1)
print(report)
```

### 5. Handle Crisis Situation
```python
# Handle crisis with immediate intervention
crisis_result = phq9_exercise_main.handle_crisis_situation(
    patient_id=1,
    crisis_data={'indicators': ['very_low_mood', 'missed_exercises']}
)
print(crisis_result)
```

## Database Schema Requirements

The system requires the following database tables (from `app_ml_complete.py`):

- `Patient`: Patient information
- `PHQ9Assessment`: PHQ-9 assessment results
- `Exercise`: Exercise definitions
- `ExerciseSession`: Exercise session records
- `MoodEntry`: Daily mood tracking
- `CrisisAlert`: Crisis situation alerts
- `RecommendationResult`: AI-generated recommendations
- `MindfulnessSession`: Mindfulness practice records
- `BehavioralActivationProgress`: Behavioral activation tracking

## Clinical Safety Features

1. **Crisis Detection**: Automatic detection of crisis indicators
2. **Provider Alerts**: Immediate notifications for severe situations
3. **Safety Protocols**: Clear escalation procedures
4. **Treatment Boundaries**: Exercises supplement, don't replace care
5. **Evidence-Based**: All adaptations based on clinical research

## Continuous Learning

The system continuously learns and adapts based on:

- Patient engagement patterns
- Exercise effectiveness data
- Mood improvement correlations
- Crisis prevention success rates
- Provider feedback and overrides

## Implementation Notes

1. **Database Connection**: Ensure proper database connection and schema
2. **Error Handling**: All components include comprehensive error handling
3. **Logging**: Detailed logging for debugging and monitoring
4. **Scalability**: Designed to handle multiple patients and providers
5. **Security**: Follow healthcare data security best practices

## Future Enhancements

1. **Machine Learning**: Advanced prediction models for exercise effectiveness
2. **Mobile Integration**: Native mobile app for patient engagement
3. **Telehealth Integration**: Direct provider communication features
4. **Research Integration**: Clinical trial data integration
5. **Multi-language Support**: International deployment capabilities

## Support and Maintenance

- Regular system health monitoring
- Provider feedback integration
- Clinical effectiveness validation
- Security and privacy audits
- Continuous improvement based on outcomes

This system represents a comprehensive approach to connecting PHQ-9 depression assessment with personalized, adaptive exercise recommendations that prioritize patient safety, engagement, and clinical effectiveness.
