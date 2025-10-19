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
    """Generate audio from text (placeholder - implement with actual voice cloning service)"""
    # Validate voice profile if provided
    if request.voice_profile_id:
        voice = db.query(VoiceProfile).filter(VoiceProfile.id == request.voice_profile_id).first()
        if not voice:
            raise HTTPException(status_code=404, detail="Voice profile not found")

    # Create output directory
    output_dir = os.path.join(settings.UPLOAD_DIR, "generated")
    os.makedirs(output_dir, exist_ok=True)

    # Placeholder for actual voice generation
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"generated_{timestamp}.wav"
    audio_path = os.path.join(output_dir, audio_filename)

    # TODO: Implement actual voice cloning here
    # For now, just create a placeholder file
    with open(audio_path, "wb") as f:
        f.write(b"")

    # Save to database
    generated = GeneratedAudio(
        voice_profile_id=request.voice_profile_id,
        text_input=request.text,
        audio_path=audio_path,
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
