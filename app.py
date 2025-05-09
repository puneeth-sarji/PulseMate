from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import nltk
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
import json
import os
from datetime import datetime
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # In production, use a proper secret key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize NLTK components with fallbacks
tokenizer = RegexpTokenizer(r'\w+')  # Simple word tokenizer as fallback
try:
    nltk.data.find('tokenizers/punkt')
    use_nltk_tokenizer = True
except LookupError:
    use_nltk_tokenizer = False

try:
    stop_words = set(stopwords.words('english'))
    use_stopwords = True
except LookupError:
    stop_words = set()
    use_stopwords = False

try:
    lemmatizer = WordNetLemmatizer()
    use_lemmatizer = True
except LookupError:
    use_lemmatizer = False

# Medical Disclaimer
MEDICAL_DISCLAIMER = """
This application is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. 
Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
Never disregard professional medical advice or delay in seeking it because of something you have read on this application.
"""

# Enhanced symptom-diagnosis database
SYMPTOM_DATABASE = {
    "fever": {
        "diagnoses": ["Common Cold", "Flu", "COVID-19", "Pneumonia", "Urinary Tract Infection"],
        "recommendations": ["Rest", "Stay hydrated", "Take fever reducers if needed", "Monitor temperature"],
        "severity": "moderate",
        "emergency": False
    },
    "headache": {
        "diagnoses": ["Tension Headache", "Migraine", "Sinusitis", "Cluster Headache", "Hypertension"],
        "recommendations": ["Rest in a dark room", "Stay hydrated", "Consider over-the-counter pain relievers", "Apply cold compress"],
        "severity": "mild",
        "emergency": False
    },
    "cough": {
        "diagnoses": ["Common Cold", "Bronchitis", "Allergies", "Asthma", "Pneumonia"],
        "recommendations": ["Stay hydrated", "Use a humidifier", "Consider cough suppressants", "Avoid irritants"],
        "severity": "mild",
        "emergency": False
    },
    "chest pain": {
        "diagnoses": ["Angina", "Heart Attack", "Costochondritis", "Anxiety", "GERD"],
        "recommendations": ["Seek immediate medical attention", "Call emergency services if severe", "Rest", "Monitor symptoms"],
        "severity": "severe",
        "emergency": True
    },
    "shortness of breath": {
        "diagnoses": ["Asthma", "Pneumonia", "Anxiety", "Heart Failure", "COPD"],
        "recommendations": ["Seek immediate medical attention", "Sit upright", "Try to remain calm", "Call emergency services if severe"],
        "severity": "severe",
        "emergency": True
    },
    "nausea": {
        "diagnoses": ["Gastritis", "Food Poisoning", "Migraine", "Pregnancy", "Motion Sickness"],
        "recommendations": ["Stay hydrated", "Rest", "Avoid solid foods initially", "Consider anti-nausea medication"],
        "severity": "moderate",
        "emergency": False
    },
    "dizziness": {
        "diagnoses": ["Vertigo", "Low Blood Pressure", "Anemia", "Inner Ear Problems", "Dehydration"],
        "recommendations": ["Sit or lie down", "Stay hydrated", "Avoid sudden movements", "Seek medical attention if severe"],
        "severity": "moderate",
        "emergency": False
    },
    "fatigue": {
        "diagnoses": ["Anemia", "Depression", "Thyroid Problems", "Sleep Apnea", "Chronic Fatigue Syndrome"],
        "recommendations": ["Get adequate rest", "Maintain regular sleep schedule", "Stay hydrated", "Consider medical evaluation"],
        "severity": "mild",
        "emergency": False
    }
}

# User model
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# Simple user storage (replace with database in production)
users = {}

def preprocess_text(text):
    try:
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenization
        if use_nltk_tokenizer:
            try:
                words = word_tokenize(text)
            except:
                words = tokenizer.tokenize(text)
        else:
            words = tokenizer.tokenize(text)
        
        # Remove stopwords if available
        if use_stopwords:
            words = [word for word in words if word not in stop_words]
        
        # Lemmatization if available
        if use_lemmatizer:
            try:
                words = [lemmatizer.lemmatize(word) for word in words]
            except:
                pass  # Keep words as is if lemmatization fails
        
        return words
    except Exception as e:
        app.logger.error(f"Text preprocessing failed: {str(e)}")
        return text.lower().split()  # Fallback to simple splitting

def analyze_symptoms(symptoms_text):
    try:
        tokens = preprocess_text(symptoms_text)
        diagnoses = set()
        recommendations = set()
        severity_levels = set()
        emergency = False
        
        # Match symptoms against database
        for token in tokens:
            if token in SYMPTOM_DATABASE:
                diagnoses.update(SYMPTOM_DATABASE[token]["diagnoses"])
                recommendations.update(SYMPTOM_DATABASE[token]["recommendations"])
                severity_levels.add(SYMPTOM_DATABASE[token]["severity"])
                if SYMPTOM_DATABASE[token]["emergency"]:
                    emergency = True
        
        # If no matches found, look for partial matches
        if not diagnoses:
            for token in tokens:
                for symptom in SYMPTOM_DATABASE:
                    if token in symptom or symptom in token:
                        diagnoses.update(SYMPTOM_DATABASE[symptom]["diagnoses"])
                        recommendations.update(SYMPTOM_DATABASE[symptom]["recommendations"])
                        severity_levels.add(SYMPTOM_DATABASE[symptom]["severity"])
                        if SYMPTOM_DATABASE[symptom]["emergency"]:
                            emergency = True
        
        # Determine overall severity
        severity = "mild"
        if "severe" in severity_levels:
            severity = "severe"
        elif "moderate" in severity_levels:
            severity = "moderate"
        
        return {
            "diagnoses": list(diagnoses) if diagnoses else ["No specific diagnosis found. Please consult a healthcare professional."],
            "recommendations": list(recommendations) if recommendations else ["Please consult a healthcare professional for proper evaluation."],
            "severity": severity,
            "emergency": emergency,
            "disclaimer": MEDICAL_DISCLAIMER
        }
    except Exception as e:
        app.logger.error(f"Symptom analysis failed: {str(e)}")
        return {
            "diagnoses": ["Error analyzing symptoms. Please try again."],
            "recommendations": ["If you are experiencing severe symptoms, please seek immediate medical attention."],
            "severity": "unknown",
            "emergency": False,
            "disclaimer": MEDICAL_DISCLAIMER
        }

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html', disclaimer=MEDICAL_DISCLAIMER)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        
        return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users:
            return render_template('register.html', error='Username already exists')
        
        users[username] = User(username, username, generate_password_hash(password))
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        symptoms = data.get('symptoms', '')
        if not symptoms:
            return jsonify({"error": "No symptoms provided"}), 400
        
        # Log the analysis request
        app.logger.info(f"Analysis request from user {current_user.username} at {datetime.now()}")
        
        results = analyze_symptoms(symptoms)
        return jsonify(results)
        
    except Exception as e:
        app.logger.error(f"Error during symptom analysis: {str(e)}")
        return jsonify({"error": "An error occurred during analysis"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 