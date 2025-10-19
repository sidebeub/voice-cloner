from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from ..core import get_db, settings
from ..models import VoiceProfile, GeneratedAudio
from ..schemas import (
    VoiceProfileCreate,
    VoiceProfileUpdate,
    VoiceProfileResponse,
    GenerateAudioRequest,
    GeneratedAudioResponse,
)
from ..services import get_voice_service

router = APIRouter(prefix="/voices", tags=["voices"])


@router.post("/", response_model=VoiceProfileResponse, status_code=201)
def create_voice_profile(
    voice: VoiceProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new voice profile"""
    db_voice = VoiceProfile(**voice.dict())
    db.add(db_voice)
    db.commit()
    db.refresh(db_voice)
    return db_voice


@router.get("/", response_model=List[VoiceProfileResponse])
def list_voice_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all voice profiles"""
    voices = db.query(VoiceProfile).filter(VoiceProfile.is_active == True).offset(skip).limit(limit).all()
    return voices


@router.get("/{voice_id}", response_model=VoiceProfileResponse)
def get_voice_profile(voice_id: int, db: Session = Depends(get_db)):
    """Get a specific voice profile"""
    voice = db.query(VoiceProfile).filter(VoiceProfile.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice profile not found")
    return voice


@router.put("/{voice_id}", response_model=VoiceProfileResponse)
def update_voice_profile(
    voice_id: int,
    voice_update: VoiceProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update a voice profile"""
    voice = db.query(VoiceProfile).filter(VoiceProfile.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    update_data = voice_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voice, field, value)

    db.commit()
    db.refresh(voice)
    return voice


@router.delete("/{voice_id}", status_code=204)
def delete_voice_profile(voice_id: int, db: Session = Depends(get_db)):
    """Soft delete a voice profile"""
    voice = db.query(VoiceProfile).filter(VoiceProfile.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    voice.is_active = False
    db.commit()
    return None


@router.post("/{voice_id}/upload-sample")
async def upload_voice_sample(
    voice_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an audio sample for a voice profile"""
    voice = db.query(VoiceProfile).filter(VoiceProfile.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    # Validate file type
    allowed_extensions = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.UPLOAD_DIR, "samples", str(voice_id))
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}{file_ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update voice profile
    voice.sample_audio_path = file_path
    db.commit()
    db.refresh(voice)

    return {"message": "Sample uploaded successfully", "file_path": file_path}


@router.post("/generate", response_model=GeneratedAudioResponse)
async def generate_audio(
    request: GenerateAudioRequest,
    db: Session = Depends(get_db)
):
    """Generate audio from text using voice cloning"""
    # Validate voice profile if provided
    speaker_wav_path = None
    if request.voice_profile_id:
        voice = db.query(VoiceProfile).filter(VoiceProfile.id == request.voice_profile_id).first()
        if not voice:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        speaker_wav_path = voice.sample_audio_path

    # Create output directory
    output_dir = os.path.join(settings.UPLOAD_DIR, "generated")
    os.makedirs(output_dir, exist_ok=True)

    # Generate audio file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"generated_{timestamp}.wav"
    audio_path = os.path.join(output_dir, audio_filename)

    duration = None

    if settings.ENABLE_VOICE_CLONING:
        try:
            # Get voice cloning service
            voice_service = get_voice_service()

            # Generate speech with voice cloning
            voice_service.generate_speech(
                text=request.text,
                output_path=audio_path,
                speaker_wav=speaker_wav_path,
                language=request.settings.get("language", "en") if request.settings else "en"
            )

            # Get audio duration
            import wave
            try:
                with wave.open(audio_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    duration = int(frames / float(rate))
            except:
                duration = None

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")
    else:
        # Voice cloning disabled - create placeholder file
        with open(audio_path, "wb") as f:
            f.write(b"")

    # Generate URL path for the audio file (relative to /audio mount)
    audio_url_path = f"/audio/generated/{audio_filename}"
    full_audio_url = f"{settings.BASE_URL}{audio_url_path}"

    # Save to database (store the full URL)
    generated = GeneratedAudio(
        voice_profile_id=request.voice_profile_id,
        text_input=request.text,
        audio_path=full_audio_url,
        duration_seconds=duration,
        settings=str(request.settings) if request.settings else None
    )
    db.add(generated)
    db.commit()
    db.refresh(generated)

    return generated


@router.get("/generated/history", response_model=List[GeneratedAudioResponse])
def get_generated_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get history of generated audio"""
    generated = db.query(GeneratedAudio).order_by(GeneratedAudio.created_at.desc()).offset(skip).limit(limit).all()
    return generated
