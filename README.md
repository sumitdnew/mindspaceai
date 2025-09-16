# 🧠 MindSpace ML - Advanced Mental Health Support System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Machine Learning](https://img.shields.io/badge/ML-BERT%20%7C%20XGBoost-orange.svg)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Overview

**MindSpace ML** is a comprehensive machine learning platform for mental health risk assessment, crisis detection, and condition classification. It leverages both internal (Kaggle/synthetic) and real-world external datasets, supports robust model validation, and enables fine-tuning for real-world deployment.

## 🎯 Key Features

### **🤖 AI-Powered Risk Assessment**
- **Hybrid Crisis Detection System**: Combines rule-based clinical assessment with XGBoost ML models
- **Real-time Crisis Detection**: Identifies immediate crisis indicators like "suicide", "kill myself", "want to die"
- **Multi-level Risk Classification**: MINIMAL, LOW, MEDIUM, HIGH, CRITICAL with probability scores
- **Contextual Analysis**: Considers text, mood patterns, behavioral data, and temporal factors
- **Personalized Responses**: AI-generated responses based on risk level and user context
- **70/30 Weighted Predictions**: 70% ML model + 30% rule-based for optimal accuracy

### **👨‍⚕️ Provider Dashboard**
- **Patient Overview**: Real-time monitoring of all patients with risk levels
- **Clickable Patient Cards**: Detailed patient views with comprehensive data
- **Crisis Alerts**: Immediate notifications for high-risk patients
- **Treatment Recommendations**: AI-generated intervention strategies
- **Progress Tracking**: Patient improvement metrics and trends
- **🤖 AI Session Briefing**: Pre-session intelligence system that generates comprehensive patient briefings using OpenAI GPT-4
- **🚨 Crisis Detection Management**: Dedicated interface for managing ML crisis detection alerts and model training
- **📊 Hybrid Prediction Display**: Shows rule-based, ML model, and combined predictions for each patient

### **👤 Patient Support Features**
- **💬 AI Chat**: Intelligent conversations with crisis detection and OpenAI-powered contextual responses
- **📖 Journal Entries**: Mood-scored journaling with sentiment analysis
- **😊 Mood Tracking**: Daily mood logging with pattern recognition
- **🎯 Goal Setting**: Mental health goal management with progress tracking
- **📈 Insights**: AI-powered analysis of mental health patterns
- **🧘‍♀️ Meditation Timer**: Guided meditation sessions with background sounds

### **🤖 AI Session Briefing System**
- **Pre-Session Intelligence**: Generates comprehensive patient briefings before therapy sessions
- **Multi-Source Data Analysis**: Analyzes mood entries, exercise sessions, PHQ-9 assessments, thought records, crisis alerts, and mindfulness sessions
- **OpenAI GPT-4 Integration**: Uses advanced AI to synthesize clinical data into actionable insights
- **Clinical Insights**: Provides key insights, risk assessments, and treatment recommendations
- **Real-time Generation**: Instant briefing generation with response times under 5 seconds
- **Provider-Focused**: Designed specifically for healthcare providers to prepare for patient sessions
- **Comprehensive Documentation**: Complete system documentation with API references and usage examples

### **🔒 Security & Privacy**
- **User Authentication**: Secure login system with role-based access
- **Data Encryption**: Protected patient information
- **Provider Access Control**: Secure provider dashboard with patient data
- **Audit Trail**: Complete activity logging for compliance

### **🤖 Fine-tuned ML Models**
- **Fine-tuned ML models** using both internal and real external data
- **External Data Integration**: Reddit, clinical, survey, and suicide prevention datasets
- **Cross-Validation**: Robust k-fold evaluation for generalization
- **Automated Validation Pipeline**: Test on real external datasets
- **Easy Model Deployment**: Use `finetuned_logreg_model.joblib` and `finetuned_vectorizer.joblib`

### **🚨 Advanced Crisis Detection System**
- **Hybrid Architecture**: Combines rule-based clinical assessment with XGBoost ML models
- **19+ Feature Engineering**: PHQ-9 scores, mood patterns, exercise data, crisis history, demographics
- **Real-time Assessment**: Automatic crisis detection on PHQ-9 assessment submission
- **Multi-tier Predictions**: Rule-based (30%), ML model (70%), and combined predictions
- **Crisis Alert Management**: Automated alert generation with provider notification system
- **Model Training Interface**: Built-in model training and validation capabilities
- **Performance Monitoring**: Real-time model status and accuracy tracking

## 🛠️ Technology Stack

### **Backend Framework**
- **Flask 2.0+**: Modern Python web framework
- **SQLAlchemy**: Advanced database ORM with relationship management
- **Flask-Login**: Secure user authentication and session management
- **Werkzeug**: Security utilities and password hashing

### **Machine Learning & AI**
- **BERT (Transformers)**: Advanced text analysis and semantic understanding
- **XGBoost**: Gradient boosting for risk classification and crisis detection
- **Scikit-learn**: Traditional ML algorithms and model evaluation
- **Pandas/NumPy**: Data processing, analysis, and numerical computations
- **Joblib**: Model serialization and persistence
- **Hybrid Prediction Engine**: 70% ML + 30% rule-based weighted combination

### **Natural Language Processing**
- **HuggingFace Transformers**: Pre-trained BERT models for text analysis
- **TextBlob**: Sentiment analysis and text processing
- **NLTK**: Advanced text preprocessing and tokenization
- **Custom Keyword Detection**: Specialized crisis and mental health keyword analysis
- **OpenAI GPT-4**: Advanced AI for clinical briefing generation and analysis

### **Database & Data Management**
- **SQLite**: Lightweight, serverless database for development
- **Structured Data Models**: Comprehensive user, chat, mood, risk assessment schemas
- **Data Migration**: Automated database initialization and population

### **Frontend & UI**
- **Bootstrap 5**: Modern, responsive UI components
- **Custom CSS**: Gradient backgrounds and professional styling
- **JavaScript**: Interactive features and real-time updates
- **Chart.js**: Data visualization for insights and trends

## 📊 Datasets & Training Data

### **Primary Dataset: Kaggle Sentiment Analysis**
- **Source**: Downloaded sentiment analysis dataset from Kaggle
- **Size**: 54,043+ mental health samples
- **Features**: Text content, sentiment labels, mental health conditions
- **Integration**: Direct integration with ML pipeline for model training

### **Additional Training Data**
- **Synthetic Mental Health Data**: 2000+ realistic samples
- **Mental Health Conditions**: Healthy, Depression, Anxiety, Bipolar, Crisis
- **Text Patterns**: Realistic chat messages and journal entries
- **Behavioral Metrics**: Sleep, activity, social interaction, mood scores

### **Data Processing Pipeline**
```python
# Feature Engineering
- Text length and word count analysis
- Crisis keyword detection (weighted scoring)
- Depression and anxiety keyword analysis
- Sentiment analysis integration
- Temporal pattern recognition
- User behavior modeling
```

## 🤖 Machine Learning Models

### **1. Hybrid Crisis Detection System (XGBoost + Rule-based)**
- **Purpose**: Comprehensive crisis risk assessment using hybrid approach
- **Features**: 19+ engineered features including PHQ-9 scores, mood patterns, exercise data, crisis history
- **Architecture**: 70% XGBoost ML model + 30% rule-based clinical assessment
- **Output**: Risk levels (MINIMAL, LOW, MEDIUM, HIGH, CRITICAL) with confidence scores
- **Performance**: High accuracy with clinical validation and early warning detection
- **Integration**: Real-time assessment on PHQ-9 submission with automated alert generation

### **2. XGBoost Crisis Detection Model**
- **Purpose**: Advanced pattern recognition for crisis prediction
- **Features**: PHQ-9 data, mood trends, exercise patterns, behavioral indicators
- **Output**: Crisis probability (0-1) and risk level classification
- **Performance**: High precision for crisis detection with 19+ feature analysis
- **Training**: 81 samples with 22 crisis cases (27.2% crisis rate)

### **3. Rule-Based Clinical Assessment**
- **Purpose**: Traditional PHQ-9 severity-based risk assessment
- **Features**: PHQ-9 total score, Q9 suicidal ideation score, severity levels
- **Output**: Clinical risk levels based on established thresholds
- **Performance**: 100% accuracy on PHQ-9 clinical criteria
- **Integration**: Provides clinical validation for ML model predictions

### **4. Condition Classification Model (XGBoost)**
- **Purpose**: Mental health condition prediction
- **Features**: Text content, behavioral patterns, mood scores
- **Output**: Predicted conditions (Depression, Anxiety, Normal, etc.)
- **Performance**: Multi-class classification with confidence scores

### **5. BERT Text Analysis**
- **Purpose**: Advanced semantic understanding and context analysis
- **Features**: Pre-trained BERT embeddings for text processing
- **Output**: Semantic meaning extraction and context-aware analysis
- **Performance**: State-of-the-art text understanding capabilities

## 📈 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   ML Models     │
│   (Bootstrap)   │◄──►│   (Flask)       │◄──►│   (BERT/XGBoost)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Interface│    │   Database      │    │   Model Storage │
│   (HTML/CSS/JS) │    │   (SQLite)      │    │   (Joblib)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Crisis        │    │   Hybrid        │    │   Alert         │
│   Detection     │    │   Prediction    │    │   System        │
│   Interface     │    │   Engine        │    │   (Real-time)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Hybrid Prediction Flow**
```
Patient Data → Rule-Based Assessment (30%) → Combined Prediction
             → XGBoost ML Model (70%)     → Crisis Alert Generation
```

## 🚀 Getting Started

### **Prerequisites**
```bash
Python 3.8+
Virtual environment
Git
```

### **Installation**

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd mindspace-ml
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements_ml.txt
   ```

4. **Set up OpenAI (Optional - for enhanced chat responses):**
   ```bash
   # Create a .env file in the project root
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```
   Get your API key from: https://platform.openai.com/api-keys

5. **Initialize Database**
   ```bash
   python app_ml_complete.py
   ```

5. **Run the Application**
   ```bash
   python app_ml_complete.py
   ```

### **Access the System**
- **Application URL**: http://127.0.0.1:5000
- **Patient Login**: `patient1` / `password123`
- **Provider Login**: `provider1` / `password123`

## 🧪 Testing & Usage

### **Patient Features Testing**
1. **Login as Patient**: Use `patient1` / `password123`
2. **Test Chat Feature**: Try crisis keywords like "suicide", "kill myself"
3. **Journal Entries**: Write entries with mood scores
4. **Mood Tracking**: Log daily moods and view patterns
5. **Goal Setting**: Create and track mental health goals
6. **Insights**: View AI-generated mental health analysis

### **Provider Features Testing**
1. **Login as Provider**: Use `provider1` / `password123`
2. **View Patient Dashboard**: See all patients with risk levels
3. **Click Patient Cards**: Access detailed patient information
4. **Monitor Risk Levels**: Track patient risk assessments
5. **Review Patient Data**: View journals, moods, goals, and chat history
6. **Test AI Briefing System**: 
   - Click "AI Briefing Test" button on main dashboard
   - Select a patient from the dropdown
   - Click "Test AI Briefing" to generate comprehensive patient briefings
   - Review key insights, recommendations, and full briefing text
7. **Test Crisis Detection System**:
   - Navigate to `/provider/crisis_detection` for crisis management
   - View hybrid predictions (rule-based, ML, combined) on patient cards
   - Train ML model using current data
   - Test batch crisis assessment for all patients

## 📁 Project Structure

```
mindspace-ml/
├── app_ml_complete.py                    # Main Flask application with ML
├── crisis_detector_xgboost.py           # XGBoost crisis detection model
├── ml_models.py                          # ML model implementation
├── train_models.py                       # Model training script
├── ai_session_briefing_system.py         # AI briefing system core
├── comprehensive_provider_dashboard.py   # Provider dashboard with AI briefing
├── requirements_ml.txt                   # ML dependencies
├── templates/                            # HTML templates
│   ├── patient_dashboard.html            # Patient dashboard
│   ├── provider_dashboard.html           # Provider dashboard with hybrid predictions
│   ├── crisis_detection_management.html  # Crisis detection management interface
│   ├── comprehensive_provider_dashboard.html # Comprehensive dashboard
│   ├── ai_briefing_test.html            # AI briefing test interface
│   ├── patient_detail.html              # Detailed patient view
│   ├── chat.html                        # AI chat interface
│   ├── journal.html                     # Journal entries
│   ├── mood_tracker.html                # Mood tracking
│   ├── goals.html                       # Goal management
│   └── insights.html                    # AI insights
├── models/                               # Trained ML models
│   ├── crisis_detector_model.pkl        # XGBoost crisis detection model
│   ├── crisis_detection.joblib
│   ├── condition_classifier.joblib
│   └── risk_assessment.joblib
├── data/                                 # Dataset files
├── static/                               # CSS, JS, images
├── README_Crisis_Detection_Complete.md  # Complete crisis detection documentation
└── README_AI_Briefing_System.md         # AI Briefing System documentation
```

## 🎯 Key Features in Detail

### **Hybrid Crisis Detection System**
- **Architecture**: 70% XGBoost ML model + 30% rule-based clinical assessment
- **Features**: 19+ engineered features including PHQ-9, mood patterns, exercise data
- **Response Time**: Immediate crisis assessment (< 1 second)
- **Accuracy**: High precision with clinical validation
- **False Positive Rate**: Low due to hybrid approach and weighted scoring
- **Real-time Integration**: Automatic assessment on PHQ-9 submission
- **Multi-tier Display**: Shows rule-based, ML, and combined predictions

### **Provider Dashboard Enhancements**
- **Clickable Patient Cards**: Hover effects and detailed patient views
- **Comprehensive Patient Data**: Assessments, journals, moods, goals, chat history
- **Risk Level Monitoring**: Real-time patient risk tracking
- **Professional UI**: Modern, responsive design with consistent styling
- **Hybrid Prediction Display**: Visual breakdown of rule-based, ML, and combined predictions
- **Crisis Management Interface**: Dedicated crisis detection management page
- **Model Training Tools**: Built-in ML model training and validation capabilities

### **Patient Support System**
- **Personalized AI Responses**: Context-aware interactions based on risk level
- **Crisis Resources**: Immediate access to emergency support information
- **Progress Tracking**: Comprehensive mental health monitoring
- **Privacy Protection**: Secure data handling and user authentication

### **AI Session Briefing System**
- **Data Sources**: Analyzes 6 comprehensive data sources (mood entries, exercise sessions, PHQ-9 assessments, thought records, crisis alerts, mindfulness sessions)
- **AI Analysis**: Uses OpenAI GPT-4 for clinical data synthesis and insight generation
- **Response Format**: Structured briefings with key insights, recommendations, and full clinical analysis
- **Real-time Generation**: Sub-5-second response times for instant provider preparation
- **Clinical Focus**: Evidence-based psychological principles and treatment recommendations
- **API Integration**: RESTful API endpoint for seamless integration with provider workflows
- **Comprehensive Documentation**: Complete system documentation with usage examples and troubleshooting

### **Fine-tuned ML Models**
- **Fine-tuned ML models** using both internal and real external data
- **External Data Integration**: Reddit, clinical, survey, and suicide prevention datasets
- **Cross-Validation**: Robust k-fold evaluation for generalization
- **Automated Validation Pipeline**: Test on real external datasets
- **Easy Model Deployment**: Use `finetuned_logreg_model.joblib` and `finetuned_vectorizer.joblib`

## 📊 Performance Metrics

### **Hybrid Crisis Detection Performance**
- **Response Time**: < 1 second for real-time analysis
- **Accuracy**: High precision with 70% ML + 30% rule-based weighting
- **False Positive Rate**: Minimized through hybrid approach and clinical validation
- **Coverage**: 19+ feature analysis including PHQ-9, mood, exercise, and behavioral data
- **Training Data**: 81 samples with 22 crisis cases (27.2% crisis rate)
- **Model Performance**: XGBoost with 100 estimators and optimized hyperparameters

### **Risk Assessment Performance**
- **Multi-factor Analysis**: PHQ-9 + Mood + Behavior + Exercise + Crisis History
- **Hybrid Approach**: Combines ML pattern recognition with clinical rule validation
- **Provider Alerts**: Real-time high-risk notifications with confidence scoring
- **Continuous Learning**: Model improvement with new data and retraining capabilities
- **Clinical Integration**: Seamless integration with existing PHQ-9 assessment workflow

### **User Experience**
- **Response Time**: Fast, responsive interface
- **Accessibility**: Mobile-friendly design
- **Security**: Secure authentication and data protection
- **Usability**: Intuitive navigation and clear interfaces

## 🔧 Development & Deployment

### **Development Mode**
```bash
python app_ml_complete.py
# Runs on http://127.0.0.1:5000 with debug mode
```

### **Production Deployment**
```bash
# Use production WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 app_ml_complete:app
```

### **Model Training**
```bash
python train_models.py
# Trains models on Kaggle dataset and saves to models/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚨 Crisis Detection System

### **Hybrid Architecture Overview**
The MindSpace ML platform features a sophisticated hybrid crisis detection system that combines the reliability of rule-based clinical assessment with the power of machine learning. This approach ensures both clinical accuracy and advanced pattern recognition.

### **Key Components**
- **XGBoost ML Model**: 19+ engineered features for pattern recognition
- **Rule-Based Assessment**: PHQ-9 severity-based clinical validation
- **Combined Prediction Engine**: 70% ML + 30% rule-based weighting
- **Real-time Integration**: Automatic assessment on PHQ-9 submission
- **Crisis Alert Management**: Automated alert generation and provider notification

### **Features Used in ML Model**
- **PHQ-9 Data**: Total score, Q9 suicidal ideation, severity level, trends
- **Mood Patterns**: Intensity, trends, low mood indicators
- **Exercise Data**: Completion rates, engagement patterns, activity drops
- **Behavioral Indicators**: Days since last session, inactivity patterns
- **Crisis History**: Previous alerts, crisis keyword detection
- **Demographics**: Age, treatment duration, social support levels

### **Risk Level Classification**
- **CRITICAL**: ≥80% probability (immediate intervention required)
- **HIGH**: 60-79% probability (urgent attention needed)
- **MEDIUM**: 40-59% probability (increased monitoring)
- **LOW**: 20-39% probability (routine care)
- **MINIMAL**: <20% probability (standard monitoring)

### **API Endpoints**
- `POST /api/crisis_detection/assess_risk` - Individual patient assessment
- `POST /api/crisis_detection/batch_assess` - Batch patient assessment
- `POST /api/crisis_detection/train_model` - Model training
- `GET /api/crisis_detection/model_status` - Model status and performance
- `GET /provider/crisis_detection` - Crisis management interface

For detailed technical documentation, see [README_Crisis_Detection_Complete.md](README_Crisis_Detection_Complete.md).

## 🙏 Acknowledgments

- **Kaggle Community**: For providing the sentiment analysis dataset
- **HuggingFace**: For BERT models and transformers library
- **OpenAI**: For GPT-4 API enabling advanced AI briefing generation
- **XGBoost Team**: For the powerful gradient boosting framework
- **Bootstrap**: For responsive UI components
- **Flask Community**: For the excellent web framework

## 📞 Support

For support, email support@mindspace-ml.com or create an issue in the repository.

---

**⚠️ Important Notice**: This system is designed for educational and research purposes. For actual mental health crises, please contact emergency services or mental health professionals immediately.

**🚨 Crisis Resources**:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911 

## 🎯 Workflow

1. **Data Preparation**
   - Internal data generated via `ml_models.py` (`load_and_prepare_data()`)
   - External data downloaded/generated in `external_datasets/`
   - Combined and mapped using `combine_internal_external_finetune.py`

2. **Fine-Tuning**
   - Run `finetune_with_crossval.py` for k-fold cross-validation and model training
   - Outputs: `finetuned_logreg_model.joblib`, `finetuned_vectorizer.joblib`

3. **Validation**
   - Use `real_external_validation.py` to test the fine-tuned model on all real external datasets
   - Results saved to `finetuned_external_validation_results.json`

4. **Prediction Utility**
   - Use `finetuned_predict.py` for single-text predictions with the fine-tuned model

## 🎯 Key Files
- `ml_models.py`: Core model logic and data generation
- `download_real_datasets.py`: Download/generate real external datasets
- `prepare_finetune_data.py`: Combine and map external data
- `combine_internal_external_finetune.py`: Merge internal and external data
- `finetune_with_crossval.py`: Fine-tune and cross-validate model
- `finetuned_predict.py`: Predict with the fine-tuned model
- `real_external_validation.py`: Validate on real external datasets

## 🎯 Model Performance (Cross-Validation)
- **Overall Accuracy:** ~87.5%
- **Crisis F1:** 0.98
- **Depression F1:** 0.94
- **Anxiety F1:** 0.73
- **Normal F1:** 0.87

## 🎯 External Validation Results
- **Reddit, Clinical, Suicide Prevention:** 100% accuracy (on mapped labels)
- **Anxiety Disorders, Surveys:** 54-62% accuracy (realistic, challenging data)

## 🎯 How to Run

1. **Prepare Data:**
   ```bash
   python download_real_datasets.py
   python prepare_finetune_data.py
   python combine_internal_external_finetune.py
   ```
2. **Fine-Tune Model:**
   ```bash
   python finetune_with_crossval.py
   ```
3. **Validate Model:**
   ```bash
   python real_external_validation.py
   ```
4. **Predict:**
   ```bash
   python finetuned_predict.py "I feel hopeless and can't sleep."
   ```

## 🎯 Requirements
- Python 3.8+
- pandas, numpy, scikit-learn, joblib
- (Optional) torch, transformers (for advanced models)

## 🎯 Architecture
See `ARCHITECTURE.md` for a detailed system overview.

## 🎯 License
MIT 

## Quickstart 🚀

1. **Clone the repository and install requirements:**
   ```bash
   git clone <repo-url>
   cd mindspace-ml
   pip install -r requirements.txt
   ```
2. **Download and prepare data:**
   ```bash
   python download_real_datasets.py
   python prepare_finetune_data.py
   python combine_internal_external_finetune.py
   ```
3. **Fine-tune the model with cross-validation:**
   ```bash
   python finetune_with_crossval.py
   ```
4. **Validate the model on real external datasets:**
   ```bash
   python real_external_validation.py
   ```
5. **Make a prediction:**
   ```bash
   python finetuned_predict.py "I feel hopeless and can't sleep."
   ```

---

## FAQ ❓

**Q: What data is the model trained on?**
A: Both internal (synthetic/Kaggle) and real external datasets (Reddit, clinical, survey, suicide prevention) are used. Data is combined and mapped to unified labels.

**Q: How do I add new external datasets?**
A: Place your CSV in `external_datasets/` and rerun the data preparation and fine-tuning scripts.

**Q: How do I retrain or fine-tune the model?**
A: Run the data preparation scripts, then `finetune_with_crossval.py` to retrain and cross-validate.

**Q: How do I validate the model?**
A: Use `real_external_validation.py` to test the model on all real external datasets. Results are saved to `finetuned_external_validation_results.json`.

**Q: Can I use this model in my own app?**
A: Yes! Load `finetuned_logreg_model.joblib` and `finetuned_vectorizer.joblib` in your Python code, or use `finetuned_predict.py` for quick predictions.

**Q: What are the main dependencies?**
A: Python 3.8+, pandas, numpy, scikit-learn, joblib. (Optional: torch, transformers for advanced models.)

**Q: Is my data private?**
A: All processing is local by default. For production/clinical use, ensure compliance with privacy standards.

**Q: How do I get help or contribute?**
A: Open an issue or pull request on GitHub, or contact the maintainers.

--- 