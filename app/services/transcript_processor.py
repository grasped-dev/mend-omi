from app.models import TranscriptWebhookPayload, ReflectionAnalysis
from app.services.sentiment_analyzer import sentiment_analyzer
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TranscriptProcessor:
    """
    Processes transcript segments to identify and analyze meal reflections
    """
    
    def __init__(self):
        # Trigger phrases that indicate reflection intent
        self.reflection_triggers = [
            "i feel",
            "i felt",
            "that meal",
            "that was",
            "too fast",
            "too slow",
            "i ate",
            "eating",
            "mindful",
            "rushed"
        ]
        
    async def process_transcript(
        self, 
        payload: TranscriptWebhookPayload
    ) -> Optional[ReflectionAnalysis]:
        """
        Process transcript segments to detect and analyze reflections
        
        Args:
            payload: Transcript webhook payload
            
        Returns:
            ReflectionAnalysis if reflection detected, None otherwise
        """
        try:
            # Combine all segments into full text
            full_text = " ".join([seg.text for seg in payload.segments])
            
            # Check if this is a reflection
            if not self._is_reflection(full_text):
                logger.debug(f"No reflection detected in: {full_text}")
                return None
                
            # Analyze the reflection
            analysis = await sentiment_analyzer.analyze_reflection(full_text)
            
            if analysis.is_reflective:
                logger.info(f"Reflection detected: {full_text[:50]}... | Sentiment: {analysis.sentiment}")
                return analysis
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing transcript: {e}")
            return None
            
    def _is_reflection(self, text: str) -> bool:
        """
        Check if text contains reflection triggers
        
        Args:
            text: Transcript text
            
        Returns:
            True if reflection is detected
        """
        text_lower = text.lower()
        return any(trigger in text_lower for trigger in self.reflection_triggers)


# Global transcript processor instance
transcript_processor = TranscriptProcessor()