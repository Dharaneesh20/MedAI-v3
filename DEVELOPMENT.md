# MedAi Development Setup Guide

## Quick Start

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create a Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

## Prerequisites

### Required Software
- **Python 3.8+** - Programming language
- **Tesseract OCR** - For image text extraction
  - Download from: https://github.com/UB-Mannheim/tesseract/wiki
  - Install to: `C:\Program Files\Tesseract-OCR\` (Windows)

### Optional Software
- **Redis** - For caching and background tasks (Celery)
- **PostgreSQL** - For production database

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/profile/` - Get user profile
- `POST /api/auth/logout/` - User logout

### Analysis Endpoints
- `POST /api/analysis/text/` - Text-based drug analysis
- `POST /api/analysis/image/` - Image OCR and analysis
- `POST /api/analysis/voice/` - Voice recognition and analysis

### History Endpoints
- `GET /api/history/` - Get conversation history
- `POST /api/history/feedback/` - Submit feedback

## Development Features

### Input Methods
1. **Text Input** - Direct medication name entry
2. **Image OCR** - Upload prescription/medication photos
3. **Voice Recognition** - Audio file processing

### AI Analysis
- **HuggingFace Integration** - Using `ibm-granite/granite-3.3-2b-instruct`
- **Drug Interaction Detection** - Major, moderate, and minor interactions
- **Safety Scoring** - 0-100 safety assessment
- **Personalized Recommendations** - Based on user medical history

### User Management
- **Custom User Model** - Extended with medical information
- **JWT Authentication** - Secure API access
- **Medical Profile** - Store allergies, conditions, current medications
- **Conversation History** - Track all analysis sessions

## Production Considerations

### Security
- Change `SECRET_KEY` in production
- Set `DEBUG=False`
- Use HTTPS for all connections
- Implement rate limiting

### Database
- Use PostgreSQL instead of SQLite
- Set up database backups
- Configure connection pooling

### Performance
- Set up Redis for caching
- Use Celery for background tasks
- Implement CDN for static files

### AI/ML
- Consider GPU acceleration for faster inference
- Implement model caching
- Set up monitoring for API usage

## Troubleshooting

### Common Issues

1. **JWT Import Error**
   ```bash
   pip install PyJWT
   ```

2. **Tesseract Not Found**
   - Install Tesseract OCR
   - Update `TESSERACT_CMD` path in settings

3. **Audio Processing Issues**
   - Install PyAudio dependencies
   - Check microphone permissions

4. **HuggingFace API Issues**
   - Verify API key is correct
   - Check internet connection
   - Monitor API usage limits

### Development Tips
- Use virtual environment for isolation
- Run migrations after model changes
- Check Django admin for data inspection
- Use Django shell for testing: `python manage.py shell`

## Testing

Run tests with:
```bash
pytest
```

For Django-specific tests:
```bash
python manage.py test
```

## Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Manual Deployment
1. Set up production server (Ubuntu/CentOS)
2. Install Python, PostgreSQL, Redis, Nginx
3. Configure environment variables
4. Set up systemd services
5. Configure reverse proxy

## Support

For issues and questions:
1. Check this documentation
2. Review Django and FastAPI documentation
3. Check HuggingFace Transformers documentation
4. Create GitHub issues for bugs

## License

MIT License - see LICENSE file for details.
