from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Types of events tracked by Mend"""
    MEAL_START = "meal_start"
    MEAL_END = "meal_end"
    REFLECTION = "reflection"


class SentimentType(str, Enum):
    """Sentiment analysis results"""
    CALM = "calm"
    STRESSED = "stressed"
    NEUTRAL = "neutral"
    RUSHED = "rushed"
    MINDFUL = "mindful"


class AudioWebhookPayload(BaseModel):
    """Payload received from Omi realtime audio webhook"""
    uid: str
    audio_bytes: bytes
    timestamp: datetime
    sample_rate: int = 16000
    

class TranscriptSegment(BaseModel):
    """A segment of transcript text"""
    text: str
    timestamp: datetime
    speaker: Optional[str] = None


class TranscriptWebhookPayload(BaseModel):
    """Payload received from Omi realtime transcript webhook"""
    uid: str
    segments: list[TranscriptSegment]
    timestamp: datetime


class MealEvent(BaseModel):
    """A meal-related event"""
    id: Optional[str] = None  # Firestore document ID
    uid: str
    timestamp: datetime
    event_type: EventType
    duration: Optional[int] = None  # Duration in seconds
    reflection_text: Optional[str] = None
    sentiment: Optional[SentimentType] = None
    cue_sent: bool = False
    

class MealEventCreate(BaseModel):
    """Model for creating a new meal event"""
    uid: str
    event_type: EventType
    duration: Optional[int] = None
    reflection_text: Optional[str] = None
    sentiment: Optional[SentimentType] = None
    

class FeedbackNotification(BaseModel):
    """Notification to send to user"""
    message: str
    uid: str


class WeeklyInsights(BaseModel):
    """Weekly summary insights for a user"""
    uid: str
    week_start: datetime
    week_end: datetime
    avg_meal_duration: float
    total_meals: int
    reflections_count: int
    most_mindful_time: Optional[str] = None
    sentiment_breakdown: dict[str, int]


class AudioAnalysisResult(BaseModel):
    """Result from audio analysis"""
    eating_detected: bool
    confidence: float
    audio_features: Optional[dict] = None
    

class ReflectionAnalysis(BaseModel):
    """Analysis of a meal reflection"""
    text: str
    sentiment: SentimentType
    is_reflective: bool
    keywords: list[str]
    tone_indicators: dict[str, float]