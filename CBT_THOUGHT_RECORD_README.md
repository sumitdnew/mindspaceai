# CBT Thought Record System - "Thought Detective"

## Overview

The CBT Thought Record System is an engaging, gamified cognitive behavioral therapy tool designed to help users identify, challenge, and restructure negative thoughts through guided interactions. Built with a "Thought Detective" theme, the system provides step-by-step guidance for cognitive restructuring while tracking progress and providing AI-powered insights.

## 🎯 Key Features

### 1. Step-by-Step Thought Record Interface
- **Situation Description**: Dropdown categories + brief context input
- **Interactive Emotion Wheel**: Visual emotion selection with intensity ratings
- **Smart Thought Prompting**: Guided prompts instead of free-form essays
- **Evidence Evaluation**: Drag-and-drop pros/cons lists with strength meters
- **Balanced Thought Creation**: AI-suggested alternatives with reasoning

### 2. Cognitive Distortion Detection
- **Pattern Recognition**: Identifies 11 common cognitive distortions
- **Educational Tooltips**: Explains distortion types with examples
- **Progress Tracking**: Monitors distortion awareness over time
- **Achievement System**: Rewards cognitive flexibility improvements
- **Provider Reports**: Personalized distortion pattern analysis

### 3. Engagement Mechanics
- **"Thought Detective" Theme**: Gamified interface with detective terminology
- **Evidence Strength Meters**: Visual feedback on evidence quality
- **Alternative Thought Engine**: AI-powered balanced thought suggestions
- **Progress Celebration**: Achievement badges and completion celebrations
- **Weekly Cognitive Flexibility Scores**: Track skill development

### 4. Data Collection Framework
- **Distortion Pattern Tracking**: Monitor cognitive distortion frequency
- **Skill Development Metrics**: Measure thought challenging effectiveness
- **Alternative Thought Effectiveness**: Track which balanced thoughts work best
- **Emotional Regulation Monitoring**: Measure mood improvement
- **Provider Insights**: Generate clinical reports on cognitive patterns

### 5. Smart Guidance Features
- **Context-Aware Prompts**: Adapts based on previous entries
- **Difficulty Level Adaptation**: Adjusts complexity based on user skill
- **Emergency Thought Challenging**: Quick access for crisis moments
- **Mood Data Integration**: Links with existing mood tracking

### 6. Clinical Validity
- **Evidence-Based CBT**: Uses proven cognitive restructuring techniques
- **Structured Format**: Prevents rumination through guided process
- **Educational Components**: Teaches cognitive distortion recognition
- **Provider-Reviewable Data**: Clear summaries for clinical review

## 🏗️ System Architecture

### Database Models

#### Core Models
- **ThoughtRecord**: Main thought record entries with situation, emotions, thoughts, evidence, and outcomes
- **EvidenceItem**: Individual evidence items with strength ratings and categories
- **DistortionAnalysis**: Analysis of cognitive distortions in thoughts
- **CognitiveDistortion**: Reference table for distortion types and examples
- **ThoughtRecordProgress**: User progress tracking and achievement system
- **ThoughtRecordTemplate**: Guided templates for different difficulty levels

#### Key Features
- **JSON Storage**: Flexible evidence and distortion data storage
- **Relationship Management**: Proper foreign key relationships
- **Validation Constraints**: Data integrity through database constraints
- **Indexing**: Optimized queries for performance

### Routes and Endpoints

#### Main Routes
- `/thought_record` - Main dashboard with progress tracking
- `/thought_record/new` - Create new thought record (step-by-step)
- `/thought_record/<id>/evidence` - Evidence analysis with drag-and-drop
- `/thought_record/<id>/balanced` - Balanced thought creation

#### API Endpoints
- `/api/cognitive_distortions` - AI-powered distortion analysis
- `/api/suggest_balanced_thought` - AI-balanced thought suggestions

### Frontend Components

#### Templates
- **thought_record_dashboard.html**: Main dashboard with progress tracking
- **new_thought_record.html**: Step-by-step thought record creation
- **thought_record_evidence.html**: Evidence analysis with drag-and-drop
- **thought_record_balanced.html**: Balanced thought creation with AI suggestions

#### Key Features
- **Responsive Design**: Works on desktop and mobile devices
- **Interactive Elements**: Drag-and-drop, sliders, emotion wheels
- **Real-time Feedback**: Immediate visual feedback on user actions
- **AI Integration**: Seamless AI-powered suggestions and analysis

## 🎮 Gamification Elements

### Detective Theme
- **Progress Levels**: Novice → Apprentice → Detective → Expert
- **Achievement Badges**: First Case Solved, 3-Day Streak, Week Warrior, etc.
- **Streak Tracking**: Daily completion streaks with milestones
- **Skill Metrics**: Balanced thinking scores and distortion detection accuracy

### Visual Feedback
- **Evidence Strength Meters**: 1-5 scale visual indicators
- **Confidence Sliders**: Interactive confidence ratings
- **Progress Animations**: Celebration animations for completions
- **Color-Coded Elements**: Supporting vs. contradicting evidence

## 🤖 AI Integration

### Cognitive Distortion Analysis
- **Real-time Analysis**: Analyzes thoughts as users type
- **Multiple Distortion Detection**: Identifies up to 11 distortion types
- **Confidence Scoring**: Provides confidence levels for each detection
- **Educational Explanations**: Explains why distortions were detected

### Balanced Thought Suggestions
- **Context-Aware Suggestions**: Based on initial thought and evidence
- **Multiple Alternatives**: Provides 3 different balanced perspectives
- **Reasoning Explanations**: Explains why suggestions are balanced
- **Evidence Integration**: Incorporates user-provided evidence

## 📊 Data Analytics

### User Progress Tracking
- **Completion Metrics**: Total records, average completion time
- **Skill Development**: Distortion identification accuracy, balanced thinking scores
- **Pattern Recognition**: Most common distortions, effective strategies
- **Trend Analysis**: Progress over time, skill improvement rates

### Clinical Insights
- **Provider Reports**: Comprehensive cognitive pattern analysis
- **Distortion Frequency**: Which distortions appear most often
- **Intervention Effectiveness**: Which strategies work best
- **Risk Assessment**: Patterns that may indicate need for additional support

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Flask application with existing user authentication
- SQLAlchemy database setup
- Claude API key (optional, for AI features)

### Installation

1. **Add Models to Database**
   ```python
   # The models are already added to app_ml_complete.py
   # Run database migrations to create new tables
   ```

2. **Initialize CBT Data**
   ```bash
   python init_cbt_data.py
   ```

3. **Add Navigation Links**
   ```html
   <!-- Add to navigation templates -->
   <a class="nav-link" href="{{ url_for('thought_record_dashboard') }}">🔍 Thought Detective</a>
   ```

4. **Configure AI Integration** (Optional)
   ```python
   # Set ANTHROPIC_API_KEY environment variable
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

### Usage

1. **Access Thought Detective**
   - Navigate to the Thought Detective section
   - View progress dashboard and recent records

2. **Create New Thought Record**
   - Click "New Investigation"
   - Follow 4-step guided process
   - Get AI-powered insights and suggestions

3. **Track Progress**
   - Monitor achievement badges
   - View cognitive distortion patterns
   - Track skill development over time

## 🎯 Clinical Benefits

### For Users
- **Structured Learning**: Guided approach to cognitive restructuring
- **Immediate Feedback**: Real-time AI analysis and suggestions
- **Progress Tracking**: Visual representation of skill development
- **Engagement**: Gamified elements increase motivation and adherence

### For Providers
- **Comprehensive Data**: Detailed cognitive pattern analysis
- **Progress Monitoring**: Track client skill development over time
- **Intervention Insights**: Identify most effective strategies
- **Risk Assessment**: Early identification of concerning patterns

## 🔧 Customization

### Adding New Cognitive Distortions
```python
# Add to init_cbt_data.py
{
    "name": "new_distortion",
    "description": "Description of the distortion",
    "examples": json.dumps(["Example 1", "Example 2"]),
    "difficulty_level": "beginner"
}
```

### Creating Custom Templates
```python
# Add to init_cbt_data.py
{
    "name": "Custom Template",
    "description": "Template description",
    "difficulty_level": "intermediate",
    "situation_prompts": json.dumps(["Prompt 1", "Prompt 2"]),
    # ... other prompt arrays
}
```

### Modifying Gamification Elements
- Update achievement criteria in `ThoughtRecordProgress` model
- Modify level progression logic in dashboard
- Customize visual elements in CSS

## 📈 Future Enhancements

### Planned Features
- **Mobile App**: Native mobile application
- **Group Sessions**: Collaborative thought challenging
- **Advanced Analytics**: Machine learning insights
- **Integration**: Connect with other mental health apps
- **Multilingual Support**: Multiple language options

### Technical Improvements
- **Performance Optimization**: Database query optimization
- **Real-time Collaboration**: WebSocket integration
- **Offline Support**: Local storage for offline use
- **API Expansion**: RESTful API for third-party integration

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- Follow PEP 8 Python style guidelines
- Add docstrings for all functions
- Include type hints where appropriate
- Write comprehensive tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CBT Foundation**: Based on established cognitive behavioral therapy principles
- **Claude AI**: Powered by Anthropic's Claude for intelligent analysis
- **Flask Community**: Built on the Flask web framework
- **Mental Health Professionals**: Clinical guidance and validation

---

**Note**: This system is designed as a therapeutic tool and should be used under appropriate clinical supervision. It is not a replacement for professional mental health treatment.
