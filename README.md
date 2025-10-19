# Voice Cloner Application

A full-stack voice cloning application built with FastAPI, React, and PostgreSQL, ready to deploy on Railway.

## Features

- Create and manage voice profiles
- Upload audio samples for voice training
- Generate speech from text
- Modern, responsive web interface
- REST API for programmatic access
- PostgreSQL database for data persistence

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database
- **Alembic** - Database migrations
- **Uvicorn** - ASGI server

### Frontend
- **React** - UI library
- **Vite** - Build tool and dev server
- **Axios** - HTTP client

## Project Structure

```
voice cloner/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration and database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI application
│   ├── alembic/          # Database migrations
│   └── alembic.ini       # Alembic configuration
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main React component
│   │   ├── main.jsx      # Entry point
│   │   └── index.css     # Styles
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── uploads/              # Audio file storage
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

### Local Development

1. **Clone the repository**
   ```bash
   cd "voice cloner"
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and configure:
   - `DATABASE_URL` - Your PostgreSQL connection string
   - `SECRET_KEY` - A random secret key for the application
   - `ALLOWED_ORIGINS` - Frontend URL (default: http://localhost:3000)

3. **Backend Setup**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # Run database migrations
   cd backend
   alembic upgrade head

   # Start the backend server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at http://localhost:8000
   API documentation at http://localhost:8000/docs

4. **Frontend Setup**
   ```bash
   # In a new terminal
   cd frontend

   # Install dependencies
   npm install

   # Start the development server
   npm run dev
   ```

   The frontend will be available at http://localhost:3000

## Railway Deployment

### 1. Set up Railway Project

1. Go to [Railway](https://railway.app) and create a new project
2. Add a PostgreSQL database to your project
3. Deploy your application from GitHub

### 2. Configure Environment Variables

In Railway, set the following environment variables:

- `DATABASE_URL` - Automatically provided by Railway PostgreSQL
- `SECRET_KEY` - Generate a secure random string
- `ALLOWED_ORIGINS` - Your Railway frontend URL
- `DEBUG` - Set to `False` for production
- `PORT` - Automatically provided by Railway

### 3. Deploy

Railway will automatically:
- Detect your Python application
- Install dependencies from requirements.txt
- Run database migrations
- Start the application using the Procfile

## API Endpoints

### Voice Profiles

- `POST /api/v1/voices/` - Create a new voice profile
- `GET /api/v1/voices/` - List all voice profiles
- `GET /api/v1/voices/{voice_id}` - Get a specific voice profile
- `PUT /api/v1/voices/{voice_id}` - Update a voice profile
- `DELETE /api/v1/voices/{voice_id}` - Delete a voice profile
- `POST /api/v1/voices/{voice_id}/upload-sample` - Upload audio sample

### Audio Generation

- `POST /api/v1/voices/generate` - Generate audio from text
- `GET /api/v1/voices/generated/history` - Get generation history

### Health Check

- `GET /health` - Check API health status

## Database Models

### VoiceProfile
- `id` - Primary key
- `name` - Voice profile name
- `description` - Optional description
- `sample_audio_path` - Path to audio sample
- `model_path` - Path to trained model
- `is_trained` - Training status
- `is_active` - Active status
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### GeneratedAudio
- `id` - Primary key
- `voice_profile_id` - Foreign key to VoiceProfile
- `text_input` - Input text
- `audio_path` - Path to generated audio
- `duration_seconds` - Audio duration
- `settings` - Generation settings (JSON)
- `created_at` - Creation timestamp

## Adding Voice Cloning API Integration

The application is structured to easily integrate with voice cloning services. To add API integration:

1. Update `requirements.txt` with your chosen API client (e.g., `elevenlabs==1.10.0`)
2. Add API credentials to `.env`:
   ```
   ELEVENLABS_API_KEY=your_api_key_here
   ```
3. Create a service in `backend/app/services/voice_service.py`
4. Update the generate endpoint in `backend/app/api/voices.py` to use the service

Example service structure:
```python
from elevenlabs import ElevenLabs

class VoiceService:
    def __init__(self, api_key: str):
        self.client = ElevenLabs(api_key=api_key)

    def generate_speech(self, text: str, voice_id: str):
        # Implementation here
        pass
```

## Development

### Create Database Migration

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

### Run Tests

```bash
# Backend tests (add pytest configuration)
pytest

# Frontend tests (add after configuring testing library)
cd frontend
npm test
```

## Production Considerations

1. **Security**
   - Use strong SECRET_KEY
   - Enable HTTPS
   - Implement rate limiting
   - Add authentication/authorization

2. **Storage**
   - Consider using object storage (S3, etc.) for audio files
   - Implement file size limits
   - Add file cleanup jobs

3. **Performance**
   - Add caching layer (Redis)
   - Implement background job queue for audio generation
   - Optimize database queries

4. **Monitoring**
   - Add logging
   - Set up error tracking (Sentry)
   - Monitor API performance

## License

MIT License - feel free to use this project for your own purposes.

## Support

For issues and questions, please open an issue on the GitHub repository.
