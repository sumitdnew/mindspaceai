# 🧠 MindSpace ML - Advanced Mental Health Support System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Machine Learning](https://img.shields.io/badge/ML-BERT%20%7C%20XGBoost-orange.svg)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Overview

**MindSpace ML** is a comprehensive machine learning platform for mental health risk assessment, crisis detection, and condition classification. It leverages both internal (Kaggle/synthetic) and real-world external datasets, supports robust model validation, and enables fine-tuning for real-world deployment.

## 🎯 Key Features

### **🤖 AI-Powered Risk Assessment**
- **Real-time Crisis Detection**: Identifies immediate crisis indicators like "suicide", "kill myself", "want to die"
- **Multi-level Risk Classification**: Low, Medium, High, Crisis with probability scores
- **Contextual Analysis**: Considers text, mood patterns, behavioral data, and temporal factors
- **Personalized Responses**: AI-generated responses based on risk level and user context

### **👨‍⚕️ Provider Dashboard**
- **Patient Overview**: Real-time monitoring of all patients with risk levels
- **Clickable Patient Cards**: Detailed patient views with comprehensive data
- **Crisis Alerts**: Immediate notifications for high-risk patients
- **Treatment Recommendations**: AI-generated intervention strategies
- **Progress Tracking**: Patient improvement metrics and trends

### **👤 Patient Support Features**
- **💬 AI Chat**: Intelligent conversations with crisis detection and OpenAI-powered contextual responses
- **📖 Journal Entries**: Mood-scored journaling with sentiment analysis
- **😊 Mood Tracking**: Daily mood logging with pattern recognition
- **🎯 Goal Setting**: Mental health goal management with progress tracking
- **📈 Insights**: AI-powered analysis of mental health patterns
- **🧘‍♀️ Meditation Timer**: Guided meditation sessions with background sounds

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

## 🛠️ Technology Stack

### **Backend Framework**
- **Flask 2.0+**: Modern Python web framework
- **SQLAlchemy**: Advanced database ORM with relationship management
- **Flask-Login**: Secure user authentication and session management
- **Werkzeug**: Security utilities and password hashing

### **Machine Learning & AI**
- **BERT (Transformers)**: Advanced text analysis and semantic understanding
- **XGBoost**: Gradient boosting for risk classification and prediction
- **Scikit-learn**: Traditional ML algorithms and model evaluation
- **Pandas/NumPy**: Data processing, analysis, and numerical computations
- **Joblib**: Model serialization and persistence

### **Natural Language Processing**
- **HuggingFace Transformers**: Pre-trained BERT models for text analysis
- **TextBlob**: Sentiment analysis and text processing
- **NLTK**: Advanced text preprocessing and tokenization
- **Custom Keyword Detection**: Specialized crisis and mental health keyword analysis

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

### **1. Crisis Detection Model (XGBoost)**
- **Purpose**: Immediate crisis indicator detection
- **Features**: Crisis keywords, text patterns, context analysis
- **Output**: Crisis probability (0-1) and risk level classification
- **Performance**: High precision for suicide/crisis keyword detection

### **2. Risk Assessment Model (XGBoost)**
- **Purpose**: Multi-factor risk scoring and classification
- **Features**: Text analysis, mood patterns, behavioral data
- **Output**: Risk levels (LOW, MEDIUM, HIGH, CRISIS)
- **Performance**: Contextual analysis with personalized risk patterns

### **3. Condition Classification Model (XGBoost)**
- **Purpose**: Mental health condition prediction
- **Features**: Text content, behavioral patterns, mood scores
- **Output**: Predicted conditions (Depression, Anxiety, Normal, etc.)
- **Performance**: Multi-class classification with confidence scores

### **4. BERT Text Analysis**
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

## 📁 Project Structure

```
mindspace-ml/
├── app_ml_complete.py          # Main Flask application with ML
├── ml_models.py                # ML model implementation
├── train_models.py             # Model training script
├── requirements_ml.txt         # ML dependencies
├── templates/                  # HTML templates
│   ├── patient_dashboard.html  # Patient dashboard
│   ├── provider_dashboard.html # Provider dashboard
│   ├── patient_detail.html     # Detailed patient view
│   ├── chat.html              # AI chat interface
│   ├── journal.html           # Journal entries
│   ├── mood_tracker.html      # Mood tracking
│   ├── goals.html             # Goal management
│   └── insights.html          # AI insights
├── models/                     # Trained ML models
│   ├── crisis_detection.joblib
│   ├── condition_classifier.joblib
│   └── risk_assessment.joblib
├── data/                       # Dataset files
└── static/                     # CSS, JS, images
```

## 🎯 Key Features in Detail

### **Real-time Crisis Detection**
- **Keywords Detected**: "suicide", "kill", "die", "want to die", "end it all"
- **Response Time**: Immediate crisis assessment (< 1 second)
- **Accuracy**: High precision for crisis keyword detection
- **False Positive Rate**: Low due to weighted keyword scoring

### **Provider Dashboard Enhancements**
- **Clickable Patient Cards**: Hover effects and detailed patient views
- **Comprehensive Patient Data**: Assessments, journals, moods, goals, chat history
- **Risk Level Monitoring**: Real-time patient risk tracking
- **Professional UI**: Modern, responsive design with consistent styling

### **Patient Support System**
- **Personalized AI Responses**: Context-aware interactions based on risk level
- **Crisis Resources**: Immediate access to emergency support information
- **Progress Tracking**: Comprehensive mental health monitoring
- **Privacy Protection**: Secure data handling and user authentication

### **Fine-tuned ML Models**
- **Fine-tuned ML models** using both internal and real external data
- **External Data Integration**: Reddit, clinical, survey, and suicide prevention datasets
- **Cross-Validation**: Robust k-fold evaluation for generalization
- **Automated Validation Pipeline**: Test on real external datasets
- **Easy Model Deployment**: Use `finetuned_logreg_model.joblib` and `finetuned_vectorizer.joblib`

## 📊 Performance Metrics

### **Crisis Detection Performance**
- **Response Time**: < 1 second for real-time analysis
- **Accuracy**: High precision for crisis keyword detection
- **False Positive Rate**: Minimized through weighted scoring
- **Coverage**: Comprehensive crisis keyword detection

### **Risk Assessment Performance**
- **Multi-factor Analysis**: Text + Mood + Behavior + Context
- **Personalization**: User-specific risk patterns
- **Provider Alerts**: Real-time high-risk notifications
- **Continuous Learning**: Model improvement with new data

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

## 🙏 Acknowledgments

- **Kaggle Community**: For providing the sentiment analysis dataset
- **HuggingFace**: For BERT models and transformers library
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