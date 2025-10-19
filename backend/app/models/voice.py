from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Voice model metadata
    sample_audio_path = Column(String(500), nullable=True)
    model_path = Column(String(500), nullable=True)

    # Status
    is_trained = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<VoiceProfile(id={self.id}, name={self.name})>"


class GeneratedAudio(Base):
    __tablename__ = "generated_audio"

    id = Column(Integer, primary_key=True, index=True)
    voice_profile_id = Column(Integer, nullable=True)

    # Input text
    text_input = Column(Text, nullable=False)

    # Output
    audio_path = Column(String(500), nullable=False)
    duration_seconds = Column(Integer, nullable=True)

    # Metadata
    settings = Column(Text, nullable=True)  # JSON string for generation settings

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<GeneratedAudio(id={self.id}, voice_profile_id={self.voice_profile_id})>"
