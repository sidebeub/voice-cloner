from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VoiceProfileBase(BaseModel):
    name: str
    description: Optional[str] = None


class VoiceProfileCreate(VoiceProfileBase):
    pass


class VoiceProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class VoiceProfileResponse(VoiceProfileBase):
    id: int
    sample_audio_path: Optional[str] = None
    model_path: Optional[str] = None
    is_trained: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        protected_namespaces = ()


class GenerateAudioRequest(BaseModel):
    text: str
    voice_profile_id: Optional[int] = None
    settings: Optional[dict] = None


class GeneratedAudioResponse(BaseModel):
    id: int
    voice_profile_id: Optional[int] = None
    text_input: str
    audio_path: str
    duration_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
