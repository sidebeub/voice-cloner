"""
Voice Cloning Service using Coqui TTS XTTS-v2
Handles text-to-speech generation with voice cloning capabilities
"""
import os
import torch
from TTS.api import TTS
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class VoiceCloningService:
    """Service for generating speech with voice cloning"""

    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        """
        Initialize the voice cloning service

        Args:
            model_name: Name of the TTS model to use
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = None
        logger.info(f"Voice cloning service initialized with device: {self.device}")

    def load_model(self):
        """Load the TTS model (lazy loading to save memory)"""
        if self.tts is None:
            logger.info(f"Loading TTS model: {self.model_name}")
            self.tts = TTS(self.model_name).to(self.device)
            logger.info("TTS model loaded successfully")

    def generate_speech(
        self,
        text: str,
        output_path: str,
        speaker_wav: Optional[str] = None,
        language: str = "en",
        **kwargs
    ) -> str:
        """
        Generate speech from text

        Args:
            text: Text to convert to speech
            output_path: Path where the audio file will be saved
            speaker_wav: Path to reference audio file for voice cloning (optional)
            language: Language code (default: "en")
            **kwargs: Additional parameters for generation

        Returns:
            Path to the generated audio file
        """
        # Load model if not loaded
        self.load_model()

        logger.info(f"Generating speech for text length: {len(text)} characters")

        try:
            if speaker_wav and os.path.exists(speaker_wav):
                # Voice cloning mode with reference audio
                logger.info(f"Using voice cloning with reference: {speaker_wav}")
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=speaker_wav,
                    language=language
                )
            else:
                # Default voice mode
                logger.info("Using default voice (no reference audio)")
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language=language
                )

            logger.info(f"Speech generated successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise

    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        if self.tts is None:
            self.load_model()

        # XTTS-v2 supports multiple languages
        return ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"]

    def unload_model(self):
        """Unload the model to free up memory"""
        if self.tts is not None:
            del self.tts
            self.tts = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("TTS model unloaded")


# Global instance (singleton pattern)
_voice_service = None


def get_voice_service() -> VoiceCloningService:
    """Get the global voice cloning service instance"""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceCloningService()
    return _voice_service
