import numpy as np
import librosa
from app.models import AudioAnalysisResult
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Processes audio chunks to detect eating sounds
    Uses acoustic features to identify eating patterns
    """
    
    def __init__(self):
        # Thresholds for eating detection
        self.eating_confidence_threshold = 0.6
        self.zcr_threshold = 0.15  # Zero crossing rate
        self.energy_threshold = 0.02
        
    def analyze_audio(self, audio_bytes: bytes, sample_rate: int = 16000) -> AudioAnalysisResult:
        """
        Analyze audio chunk for eating sounds
        
        Args:
            audio_bytes: Raw audio data (16-bit PCM)
            sample_rate: Audio sample rate (default 16kHz)
            
        Returns:
            AudioAnalysisResult with detection status and confidence
        """
        try:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
            audio_data = audio_data / 32768.0  # Normalize to [-1, 1]
            
            # Extract acoustic features
            features = self._extract_features(audio_data, sample_rate)
            
            # Detect eating patterns
            eating_detected, confidence = self._detect_eating(features)
            
            return AudioAnalysisResult(
                eating_detected=eating_detected,
                confidence=confidence,
                audio_features=features
            )
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            return AudioAnalysisResult(
                eating_detected=False,
                confidence=0.0
            )
            
    def _extract_features(self, audio: np.ndarray, sr: int) -> dict:
        """
        Extract acoustic features relevant for eating detection
        
        Features:
        - Zero Crossing Rate (ZCR): Indicates rhythmic chewing
        - RMS Energy: Overall sound level
        - Spectral Centroid: Frequency distribution (clinks, utensils)
        - Spectral Rolloff: High-frequency content
        """
        try:
            # Zero Crossing Rate - rhythmic patterns
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            zcr_mean = float(np.mean(zcr))
            zcr_std = float(np.std(zcr))
            
            # RMS Energy - sound intensity
            rms = librosa.feature.rms(y=audio)[0]
            rms_mean = float(np.mean(rms))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spectral_centroid_mean = float(np.mean(spectral_centroids))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            spectral_rolloff_mean = float(np.mean(spectral_rolloff))
            
            return {
                "zcr_mean": zcr_mean,
                "zcr_std": zcr_std,
                "rms_mean": rms_mean,
                "spectral_centroid": spectral_centroid_mean,
                "spectral_rolloff": spectral_rolloff_mean
            }
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
            
    def _detect_eating(self, features: dict) -> tuple[bool, float]:
        """
        Simple heuristic-based eating detection
        
        Eating sounds typically have:
        - Moderate ZCR (rhythmic chewing)
        - Moderate to high energy (utensil sounds, chewing)
        - Variable spectral content (clinks, rustling)
        
        Returns:
            (eating_detected, confidence_score)
        """
        if not features:
            return False, 0.0
            
        try:
            confidence_factors = []
            
            # Check Zero Crossing Rate (rhythmic patterns)
            zcr_mean = features.get("zcr_mean", 0)
            if 0.05 < zcr_mean < 0.25:  # Moderate rhythmic activity
                confidence_factors.append(0.3)
                
            # Check RMS Energy (sound intensity)
            rms_mean = features.get("rms_mean", 0)
            if rms_mean > self.energy_threshold:
                confidence_factors.append(0.3)
                
            # Check spectral content (utensil clinks have higher frequencies)
            spectral_centroid = features.get("spectral_centroid", 0)
            if spectral_centroid > 1000:  # Higher frequency content
                confidence_factors.append(0.2)
                
            # Check spectral rolloff variation
            spectral_rolloff = features.get("spectral_rolloff", 0)
            if spectral_rolloff > 2000:
                confidence_factors.append(0.2)
            
            # Calculate total confidence
            confidence = sum(confidence_factors)
            eating_detected = confidence >= self.eating_confidence_threshold
            
            return eating_detected, confidence
            
        except Exception as e:
            logger.error(f"Error in eating detection: {e}")
            return False, 0.0


# Global audio processor instance
audio_processor = AudioProcessor()