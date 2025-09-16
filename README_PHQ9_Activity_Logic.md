# PHQ-9 Based Activity Suggestion Logic

A comprehensive documentation of how the MindSpace AI system suggests personalized activities to patients based on their PHQ-9 depression assessment scores.

## Overview

The system transforms PHQ-9 assessment results into actionable, personalized activity recommendations that adapt in real-time based on patient engagement, mood trends, and clinical safety requirements.

## Core Logic Flow

```
PHQ-9 Assessment → Severity Calculation → Base Activity Mapping → Adaptive Logic → Personalized Recommendations
```

## PHQ-9 Severity Classification

The system uses a **5-tier severity classification** based on total PHQ-9 scores:

| Severity Level | Score Range | Color Code | Description |
|----------------|-------------|------------|-------------|
| **Minimal** | 0-4 | 🟢 Green | Minimal depression |
| **Mild** | 5-9 | 🟡 Yellow | Mild depression |
| **Moderate** | 10-14 | 🟠 Orange | Moderate depression |
| **Moderately Severe** | 15-19 | 🔴 Red | Moderately severe depression |
| **Severe** | 20-27 | 🟣 Purple | Severe depression |

## Activity Prescription by Severity Level

### 🟢 Minimal Depression (0-4 points)

**Focus:** Maintenance and prevention

```python
{
    'daily': ['mood_check_in'],
    'weekly': ['gratitude_exercise', 'wellness_tracking'],
    'frequency': 'low',
    'focus': 'maintenance',
    'duration': '30_seconds_to_5_minutes'
}
```

**Activities:**
- **Daily:** Quick mood check-in (30 seconds)
- **Weekly:** Gratitude exercises, wellness tracking
- **Goal:** Maintain current mental health status

### 🟡 Mild Depression (5-9 points)

**Focus:** Skill building and early intervention

```python
{
    'daily': ['mood_tracking', 'cbt_thought_record'],
    'weekly': ['mindfulness_exercise', 'activity_planning'],
    'frequency': 'moderate',
    'focus': 'skill_building',
    'duration': '5_to_15_minutes'
}
```

**Activities:**
- **Daily:** Mood tracking, CBT thought records
- **Weekly:** Mindfulness exercises, activity planning
- **Goal:** Build coping skills and prevent worsening

### 🟠 Moderate Depression (10-14 points)

**Focus:** Active treatment and skill development

```python
{
    'daily': ['mood_tracking', 'behavioral_activation', 'cbt_exercises'],
    'weekly': ['mindfulness_exercises', 'activity_scheduling'],
    'frequency': 'high',
    'focus': 'active_treatment',
    'duration': '15_to_30_minutes'
}
```

**Activities:**
- **Daily:** Mood tracking, behavioral activation, CBT exercises
- **Weekly:** Mindfulness exercises, activity scheduling
- **Goal:** Active treatment and symptom reduction

### 🔴 Moderately Severe (15-19 points)

**Focus:** Crisis management and intensive monitoring

```python
{
    'daily': ['crisis_monitoring', 'structured_activities', 'cbt_intensive'],
    'micro_moments': ['safety_check_ins'],
    'emergency': ['breathing_grounding'],
    'frequency': 'intensive',
    'focus': 'crisis_management',
    'duration': '30_to_45_minutes'
}
```

**Activities:**
- **Daily:** Crisis monitoring, structured activities, intensive CBT
- **Micro-moments:** Safety check-ins throughout the day
- **Emergency:** Breathing and grounding techniques (24/7)
- **Goal:** Crisis prevention and safety maintenance

### 🟣 Severe Depression (20-27 points)

**Focus:** Crisis intervention and immediate safety

```python
{
    'daily': ['crisis_intervention', 'safety_planning', 'provider_alerts'],
    'micro_moments': ['multiple_safety_checks'],
    'emergency': ['immediate_crisis_exercises'],
    'frequency': 'crisis_level',
    'focus': 'crisis_intervention',
    'duration': 'as_needed'
}
```

**Activities:**
- **Daily:** Crisis intervention, safety planning, provider alerts
- **Micro-moments:** Multiple safety checks throughout the day
- **Emergency:** Immediate crisis exercises (24/7)
- **Goal:** Immediate safety and crisis intervention

## Exercise Types & Specifications

| Exercise Type | Duration | Difficulty | Category | Description |
|---------------|----------|------------|----------|-------------|
| `mood_check_in` | 30 seconds | Beginner | Assessment | Quick mood assessment |
| `cbt_thought_record` | 10 minutes | Intermediate | Cognitive | Challenge negative thoughts |
| `mindfulness_exercise` | 5 minutes | Beginner | Mindfulness | Present moment awareness |
| `behavioral_activation` | 15 minutes | Intermediate | Behavioral | Plan meaningful activities |
| `crisis_monitoring` | 2 minutes | Advanced | Crisis | Safety and crisis assessment |
| `breathing_grounding` | 3 minutes | Beginner | Crisis | Immediate crisis intervention |

## Adaptive Logic System

The system continuously adapts recommendations based on patient response patterns:

### 📈 Improvement Detection

**Triggers:**
- **7+ consecutive days** of mood improvement
- **>85% exercise completion** for 2 weeks
- **Crisis exercise usage drops to zero** for 2 weeks

**Actions:**
- Reduce exercise intensity by 25%
- Offer advanced exercises
- Step down monitoring frequency

### 📉 Deterioration Detection

**Triggers:**
- **5+ days of declining mood**
- **<50% exercise completion**
- **>3 crisis exercises in one week**

**Actions:**
- Increase exercise frequency
- Switch to easier exercises
- Immediate provider alert

### 🎯 Engagement-Based Adaptation

**Low Engagement (<50% completion):**
- Simplify exercises
- Reduce duration
- Switch to easier activities
- Increase support

**High Engagement (>85% completion):**
- Offer advanced exercises
- Increase duration
- Add reflection components
- Celebrate progress

## Time-Based Scheduling

The system optimizes activity timing based on clinical best practices:

### 🌅 Morning (8:00-10:00 AM)
- **Activities:** Quick mood check-in, breathing exercises
- **Rationale:** Start day with mood assessment and grounding

### ☀️ Midday (12:00-2:00 PM)
- **Activities:** Micro-moment assessment, thought records
- **Rationale:** Midday check-in and intervention

### 🌆 Evening (6:00-8:00 PM)
- **Activities:** Activity completion review, planning
- **Rationale:** Evening reflection and next-day planning

### 🚨 Emergency (24/7)
- **Activities:** Crisis breathing, grounding techniques
- **Rationale:** Immediate crisis support

## Crisis Detection & Safety Protocols

### 🚨 Crisis Triggers

**Automatic Detection:**
- Mood score ≤ 2
- Recent crisis alerts
- Q9 risk flag (suicidal ideation)
- >3 crisis exercises in one week
- Missed exercises in severe patients

**Manual Indicators:**
- Patient self-reports crisis
- Provider-identified concerns
- Family/friend alerts

### 🛡️ Crisis Response Protocol

**Immediate Actions:**
1. Execute crisis intervention exercises
2. Create crisis alert record
3. Notify provider within 2 hours
4. Activate emergency contact system
5. Implement intensive monitoring

**Follow-up Actions:**
- Daily crisis check-ins
- Provider session scheduling
- Safety plan review
- Medication review (if applicable)

## Continuous Learning & Optimization

### 📊 Data Collection

**Patient Metrics:**
- Exercise completion rates
- Engagement scores
- Mood improvement trends
- Crisis intervention usage
- Optimal timing patterns

**System Metrics:**
- Exercise effectiveness ratings
- Provider feedback
- Clinical outcome correlations
- Algorithm performance

### 🔄 Feedback Loops

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

## Provider Integration

### 📊 Daily Dashboard

**Alert System:**
- **🔴 Red Alerts:** Crisis situations requiring immediate action
- **🟡 Yellow Alerts:** Concerning trends needing attention
- **🟢 Green Status:** Good progress and engagement

### 📈 Weekly Reports

**Comprehensive Analysis:**
- Exercise completion summaries
- Effectiveness metrics
- Mood trend analysis
- Recommended adjustments
- Patient session preparation

### 🚨 Crisis Escalation

**Immediate Notifications:**
- Crisis situation alerts
- Urgent appointment scheduling
- Crisis resource recommendations
- Emergency contact activation

## Clinical Safety Features

### 🛡️ Safety Protocols

1. **Crisis Override:** Suicidal ideation triggers immediate intensive plan
2. **Provider Notification:** Alerts sent within 2 hours for severe situations
3. **Treatment Boundaries:** Exercises supplement, don't replace provider care
4. **Evidence-Based:** All adaptations based on clinical research
5. **Regular Validation:** Continuous effectiveness monitoring

### 📋 Treatment Boundaries

- **Supplemental Care:** Activities enhance but never replace provider treatment
- **Clear Guidelines:** Patients know when to contact providers
- **Escalation Protocols:** Clear procedures for crisis situations
- **Provider Override:** Providers can modify or override recommendations

## Implementation Details

### 🏗️ System Architecture

```
PHQ-9 Assessment → Integration Engine → Exercise Recommendations
                                        ↓
Provider Dashboard ← Execution Engine ← Exercise Sessions
                                        ↓
Motivation System ← Progress Tracking ← Patient Engagement
```

### 🔧 Key Components

1. **PHQ-9 Exercise Integration** (`phq9_exercise_integration.py`)
2. **Exercise Execution Engine** (`exercise_execution_engine.py`)
3. **Provider Dashboard** (`provider_dashboard.py`)
4. **Patient Motivation System** (`patient_motivation_system.py`)
5. **Main Integration System** (`phq9_exercise_main.py`)

### 📊 Database Schema

**Core Tables:**
- `Patient` - Patient information
- `PHQ9Assessment` - Assessment results and severity levels
- `Exercise` - Available exercise definitions
- `ExerciseSession` - Individual session records
- `MoodEntry` - Daily mood tracking
- `CrisisAlert` - Crisis situation alerts

## Usage Examples

### Process PHQ-9 Assessment
```python
from phq9_exercise_main import phq9_exercise_main

# Process a new PHQ-9 assessment
result = phq9_exercise_main.process_phq9_assessment(patient_id=1, assessment_id=1)
print(result)
```

### Execute Exercise Session
```python
# Execute a mood check-in exercise
result = phq9_exercise_main.execute_exercise_session(
    patient_id=1, 
    exercise_type='mood_check_in'
)
print(result)
```

### Get Provider Insights
```python
# Get comprehensive provider dashboard
insights = phq9_exercise_main.get_provider_insights()
print(insights)
```

## Future Enhancements

### 🚀 Planned Improvements

1. **Machine Learning:** Advanced prediction models for exercise effectiveness
2. **Mobile Integration:** Native mobile app for patient engagement
3. **Telehealth Integration:** Direct provider communication features
4. **Research Integration:** Clinical trial data integration
5. **Multi-language Support:** International deployment capabilities

### 🔬 Research Opportunities

- **Personalization Algorithms:** Individual preference learning
- **Cultural Adaptation:** Culturally sensitive activity recommendations
- **Comorbidity Integration:** Multi-condition activity planning
- **Medication Integration:** Drug-effect activity optimization

## Support and Maintenance

### 🔧 System Health Monitoring

- Regular system performance monitoring
- Provider feedback integration
- Clinical effectiveness validation
- Security and privacy audits
- Continuous improvement based on outcomes

### 📚 Documentation

- Comprehensive API documentation
- Clinical implementation guides
- Provider training materials
- Patient education resources
- Technical troubleshooting guides

---

**Note:** This system represents a comprehensive approach to connecting PHQ-9 depression assessment with personalized, adaptive activity recommendations that prioritize patient safety, engagement, and clinical effectiveness.

**Last Updated:** January 2025  
**Version:** 1.0  
**Status:** Production Ready
