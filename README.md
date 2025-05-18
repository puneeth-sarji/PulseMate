# PulseMate - Smart Health Analysis Platform

PulseMate is an intelligent health analysis platform that uses natural language processing to analyze symptoms and provide preliminary health insights. The platform combines modern web technologies with advanced NLP to deliver a user-friendly health assessment tool.

## 🌟 Features

- **Smart Symptom Analysis**: Advanced NLP-based symptom analysis
- **User Authentication**: Secure login and registration system
- **Real-time Analysis**: Instant health insights and recommendations
- **Emergency Alerts**: Immediate notification for critical conditions
- **Responsive Design**: Beautiful UI that works on all devices
- **Medical Disclaimer**: Clear health information guidelines

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pulsemate.git
cd pulsemate
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Download required NLTK data:
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5002`

## 💻 Usage

1. **Register/Login**: Create an account or login to access the platform
2. **Enter Symptoms**: Describe your symptoms in natural language
3. **Get Analysis**: Receive instant health insights and recommendations
4. **Review Results**: Check diagnoses and follow recommendations

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **NLP**: NLTK (Natural Language Toolkit)
- **Database**: SQLite (for user management)
- **Authentication**: Flask-Login

## 🔒 Security Features

- Secure password hashing
- Session management
- Protected routes
- Input validation
- Error handling

## ⚠️ Medical Disclaimer

PulseMate is designed to provide preliminary health insights and should not be used as a substitute for professional medical advice. Always consult with healthcare professionals for proper diagnosis and treatment.


## 👥 Authors

- Puneeth Sarji

## 🙏 Acknowledgments

- NLTK team for the natural language processing tools
- Flask team for the web framework
- Tailwind CSS for the styling framework


Made with ❤️ by the PulseMate Team 
