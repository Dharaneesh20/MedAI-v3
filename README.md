# 🏥 MedAi - AI-Powered Drug Interaction Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com)
[![IBM Granite](https://img.shields.io/badge/IBM%20Granite-LLM-purple.svg)](https://huggingface.co/ibm-granite)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A sophisticated Django-based FastAPI application for **drug interaction analysis** powered by **IBM Granite LLM**. MedAi provides multiple input methods (text, OCR, speech-to-text) and delivers AI-powered medical recommendations for safer medication management.

## ✨ Highlights

### 🧠 **IBM Granite LLM Integration**
MedAi leverages the cutting-edge **IBM Granite 3.3-2B Instruct** model from HuggingFace for:
- **Advanced Drug Interaction Analysis**: Deep understanding of medication combinations
- **Personalized Dosage Recommendations**: Tailored to patient profiles and medical history  
- **Medical Context Understanding**: Natural language processing optimized for healthcare
- **Real-time Analysis**: Fast and accurate responses for critical medical decisions

> **Model**: `ibm-granite/granite-3.3-2b-instruct` - A state-of-the-art instruction-tuned language model specifically designed for complex reasoning tasks.

## � Screenshots

### 🏠 Home Page
![MedAI Home Page](screenshots/home_page.png)
*Main dashboard with quick access to all analysis features*

### 💊 Drug Analysis Interface
![Drug Analysis](screenshots/drug_analysis.png)
*Interactive interface for medication input and analysis*

### 📋 Medical History
![Medical History](screenshots/medical_history.png)
*Patient profile and conversation history management*

### 📱 OCR Processing
![OCR Processing](screenshots/ocr_processing.png)
*Image-based prescription analysis using optical character recognition*

### ⚠️ Interaction Alerts
![Interaction Alerts](screenshots/interaction_alerts.png)
*Real-time drug interaction warnings and recommendations*

> **Note**: Screenshots show the latest UI design. To add your own screenshots, place them in the `screenshots/` directory in your project root.

## �🚀 Features

- 🔤 **Text Input**: Direct medication queries and interaction checks
- 📸 **OCR Processing**: Extract medication information from prescription images
- 🎤 **Voice Recognition**: Speech-to-text for hands-free operation
- 👤 **User Authentication**: Secure login, registration, and profile management
- 📋 **Medical History**: Comprehensive patient data storage and management
- 💊 **Smart Dosage Analysis**: AI-powered personalized recommendations
- 📚 **Conversation History**: Track and review previous analyses
- ⚠️ **Interaction Alerts**: Real-time warnings for dangerous drug combinations

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | Django 4.2+ & FastAPI |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **AI/ML Engine** | HuggingFace Transformers |
| **LLM Model** | IBM Granite 3.3-2B Instruct |
| **OCR Engine** | Tesseract |
| **Speech Recognition** | SpeechRecognition Library |
| **Authentication** | Django Auth + JWT |
| **Frontend** | HTML5, CSS3, JavaScript |

## 📋 Prerequisites

- **Python 3.8+**
- **Git**
- **Virtual Environment** (recommended)
- **HuggingFace Account** (for API access)

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/medai.git
cd medai
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```bash
# .env file
SECRET_KEY=your-super-secret-django-key-here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost:5432/medai_db
```

### 5. Database Setup
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py makemigrations authentication
python manage.py makemigrations core
python manage.py makemigrations analysis
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

🎉 **Success!** Visit `http://localhost:8000` to access MedAi.

## 📱 Usage Guide

### 1. **Registration & Login**
- Navigate to `/register/` to create a new account
- Login at `/login/` with your credentials
- Complete your medical profile for personalized recommendations

### 2. **Drug Analysis Methods**

#### Text Analysis
- Go to the main dashboard
- Enter medication names or queries in the text input
- Receive instant AI-powered interaction analysis

#### Image OCR Analysis  
- Upload prescription images or medication labels
- OCR extracts text automatically
- AI analyzes extracted medication information

#### Voice Analysis
- Click the microphone icon
- Speak your medication query clearly
- Speech-to-text converts audio to analyzable text

### 3. **View Results & History**
- Review detailed interaction warnings and recommendations
- Save important analyses to your conversation history
- Access previous consultations anytime from your profile

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | User registration |
| `/api/auth/login/` | POST | User authentication |
| `/api/auth/profile/` | GET/PUT | User profile management |
| `/api/analysis/text/` | POST | Text-based drug analysis |
| `/api/analysis/image/` | POST | Image OCR and analysis |
| `/api/analysis/voice/` | POST | Voice recognition and analysis |
| `/api/history/` | GET | Conversation history |
| `/api/feedback/` | POST | Submit analysis feedback |

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test authentication
python manage.py test analysis
python manage.py test core
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'xxx'`
```bash
# Solution: Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

**Issue**: Database migration errors
```bash
# Solution: Reset migrations (development only)
python manage.py migrate --run-syncdb
```

**Issue**: HuggingFace API errors
```bash
# Solution: Verify your API key in .env file
# Check HuggingFace account quotas and permissions
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **IBM Research** for the powerful Granite LLM model
- **HuggingFace** for the transformers library and model hosting
- **Django & FastAPI** communities for excellent documentation
- **Tesseract OCR** for reliable text extraction capabilities

## 📞 Support

- 📧 **Email**: support@medai.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/medai/issues)
- 📖 **Documentation**: [Wiki](https://github.com/yourusername/medai/wiki)

---

⚠️ **Disclaimer**: MedAi is for educational and research purposes. Always consult healthcare professionals for medical decisions.
