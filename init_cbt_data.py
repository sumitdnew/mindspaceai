#!/usr/bin/env python3
"""
Initialize CBT Thought Record System Data
"""

import json
from datetime import datetime
from app_ml_complete import app, db, CognitiveDistortion, ThoughtRecordTemplate

def init_cognitive_distortions():
    """Initialize cognitive distortion reference data"""
    
    distortions = [
        {
            "name": "all_or_nothing",
            "description": "Seeing things as black or white, with no middle ground. If you're not perfect, you're a failure.",
            "examples": json.dumps([
                "I must be perfect or I'm worthless",
                "If I don't get an A, I'm a complete failure",
                "Either I'm loved or I'm hated"
            ]),
            "difficulty_level": "beginner"
        },
        {
            "name": "catastrophizing",
            "description": "Expecting the worst-case scenario to happen. Making mountains out of molehills.",
            "examples": json.dumps([
                "If I make a mistake at work, I'll get fired and never find another job",
                "If my partner is late, they must have been in a terrible accident",
                "This headache means I have a brain tumor"
            ]),
            "difficulty_level": "beginner"
        },
        {
            "name": "overgeneralization",
            "description": "Making broad conclusions based on a single event or piece of evidence.",
            "examples": json.dumps([
                "I failed this test, so I'm bad at everything",
                "Nobody likes me because one person was rude",
                "I always mess things up"
            ]),
            "difficulty_level": "beginner"
        },
        {
            "name": "mental_filter",
            "description": "Focusing only on the negative aspects of a situation while ignoring the positive.",
            "examples": json.dumps([
                "My presentation was terrible (ignoring the positive feedback)",
                "I only remember the times I failed, not when I succeeded",
                "Everything about this day was awful (ignoring good moments)"
            ]),
            "difficulty_level": "intermediate"
        },
        {
            "name": "disqualifying_positive",
            "description": "Dismissing positive experiences or feedback as irrelevant or unimportant.",
            "examples": json.dumps([
                "Anyone could have done that, it's not special",
                "They're just being nice, they don't really mean it",
                "That doesn't count because it was easy"
            ]),
            "difficulty_level": "intermediate"
        },
        {
            "name": "mind_reading",
            "description": "Assuming you know what others are thinking without evidence.",
            "examples": json.dumps([
                "They think I'm stupid",
                "She's probably judging me",
                "He doesn't like me"
            ]),
            "difficulty_level": "intermediate"
        },
        {
            "name": "fortune_telling",
            "description": "Predicting negative outcomes without evidence.",
            "examples": json.dumps([
                "I'll never find a good job",
                "This relationship is doomed to fail",
                "I'll always be alone"
            ]),
            "difficulty_level": "intermediate"
        },
        {
            "name": "emotional_reasoning",
            "description": "Believing that your feelings reflect reality.",
            "examples": json.dumps([
                "I feel stupid, so I must be stupid",
                "I feel anxious, so something bad must be about to happen",
                "I feel guilty, so I must have done something wrong"
            ]),
            "difficulty_level": "advanced"
        },
        {
            "name": "should_statements",
            "description": "Using 'should', 'must', or 'ought' statements that create unrealistic expectations.",
            "examples": json.dumps([
                "I should be able to handle this",
                "I must be perfect",
                "I ought to be more successful"
            ]),
            "difficulty_level": "advanced"
        },
        {
            "name": "labeling",
            "description": "Attaching negative labels to yourself or others based on behavior.",
            "examples": json.dumps([
                "I'm a failure",
                "I'm stupid",
                "They're a jerk"
            ]),
            "difficulty_level": "advanced"
        },
        {
            "name": "personalization",
            "description": "Taking responsibility for events outside your control.",
            "examples": json.dumps([
                "It's my fault the team lost",
                "If I had been there, this wouldn't have happened",
                "I caused their bad mood"
            ]),
            "difficulty_level": "advanced"
        }
    ]
    
    for distortion_data in distortions:
        # Check if distortion already exists
        existing = CognitiveDistortion.query.filter_by(name=distortion_data["name"]).first()
        if not existing:
            distortion = CognitiveDistortion(**distortion_data)
            db.session.add(distortion)
            print(f"✅ Added cognitive distortion: {distortion_data['name']}")
        else:
            print(f"⏭️ Cognitive distortion already exists: {distortion_data['name']}")

def init_thought_record_templates():
    """Initialize thought record templates for different difficulty levels"""
    
    templates = [
        {
            "name": "Beginner Work Situation",
            "description": "A simple template for work-related thoughts and situations.",
            "difficulty_level": "beginner",
            "situation_prompts": json.dumps([
                "What happened at work today?",
                "Who was involved?",
                "When and where did this occur?"
            ]),
            "emotion_prompts": json.dumps([
                "How did this make you feel?",
                "What was the strongest emotion?",
                "How intense was this feeling (1-10)?"
            ]),
            "thought_prompts": json.dumps([
                "What thoughts went through your mind?",
                "What did you tell yourself about this situation?",
                "How confident are you in this thought (1-10)?"
            ]),
            "evidence_prompts": json.dumps([
                "What facts support your thought?",
                "What facts contradict your thought?",
                "What would someone else say about this?"
            ])
        },
        {
            "name": "Social Anxiety Template",
            "description": "Template for social situations that cause anxiety.",
            "difficulty_level": "intermediate",
            "situation_prompts": json.dumps([
                "Describe the social situation that triggered anxiety",
                "What were you doing when you felt anxious?",
                "Who else was present?"
            ]),
            "emotion_prompts": json.dumps([
                "What specific emotions did you experience?",
                "How intense was your anxiety (1-10)?",
                "What physical sensations did you notice?"
            ]),
            "thought_prompts": json.dumps([
                "What were you thinking about yourself?",
                "What did you think others were thinking?",
                "What did you predict would happen?"
            ]),
            "evidence_prompts": json.dumps([
                "What evidence suggests your fears were accurate?",
                "What evidence suggests they weren't?",
                "What would a friend say about this situation?"
            ])
        },
        {
            "name": "Relationship Conflict Template",
            "description": "Template for challenging relationship situations.",
            "difficulty_level": "advanced",
            "situation_prompts": json.dumps([
                "Describe the conflict or disagreement",
                "What was said or done?",
                "What was the context of this situation?"
            ]),
            "emotion_prompts": json.dumps([
                "What emotions did you experience?",
                "How did your emotions change during the situation?",
                "What emotions do you think the other person felt?"
            ]),
            "thought_prompts": json.dumps([
                "What did you think about the other person's intentions?",
                "What did you think about yourself in this situation?",
                "What did you think would happen next?"
            ]),
            "evidence_prompts": json.dumps([
                "What evidence supports your interpretation?",
                "What evidence suggests alternative explanations?",
                "What patterns do you notice in similar situations?"
            ])
        }
    ]
    
    for template_data in templates:
        # Check if template already exists
        existing = ThoughtRecordTemplate.query.filter_by(name=template_data["name"]).first()
        if not existing:
            template = ThoughtRecordTemplate(**template_data)
            db.session.add(template)
            print(f"✅ Added template: {template_data['name']}")
        else:
            print(f"⏭️ Template already exists: {template_data['name']}")

def main():
    """Initialize all CBT data"""
    print("🚀 Initializing CBT Thought Record System Data...")
    
    with app.app_context():
        # Initialize cognitive distortions
        print("\n📚 Initializing Cognitive Distortions...")
        init_cognitive_distortions()
        
        # Initialize thought record templates
        print("\n📋 Initializing Thought Record Templates...")
        init_thought_record_templates()
        
        # Commit all changes
        db.session.commit()
        
        print("\n✅ CBT Thought Record System initialization complete!")
        print(f"📊 Created {CognitiveDistortion.query.count()} cognitive distortions")
        print(f"📋 Created {ThoughtRecordTemplate.query.count()} templates")

if __name__ == "__main__":
    main()
