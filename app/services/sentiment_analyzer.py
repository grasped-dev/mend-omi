from openai import AsyncOpenAI
from config import settings
from app.models import SentimentType, ReflectionAnalysis
import logging
import json

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyzes meal reflections for sentiment and tone
    Uses OpenAI API for natural language understanding
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Keywords that indicate reflective intent
        self.reflection_keywords = [
            "feel", "felt", "feeling",
            "was", "were", "seemed",
            "too fast", "too slow", "rushed",
            "mindful", "aware", "noticed",
            "enjoyed", "satisfying", "satisfied",
            "stressed", "anxious", "calm"
        ]
        
    async def analyze_reflection(self, text: str) -> ReflectionAnalysis:
        """
        Analyze a meal reflection for sentiment and tone
        
        Args:
            text: User's spoken reflection text
            
        Returns:
            ReflectionAnalysis with sentiment, keywords, and tone indicators
        """
        try:
            # Check if text contains reflective intent
            is_reflective = self._is_reflective(text)
            
            if not is_reflective:
                return ReflectionAnalysis(
                    text=text,
                    sentiment=SentimentType.NEUTRAL,
                    is_reflective=False,
                    keywords=[],
                    tone_indicators={}
                )
            
            # Use OpenAI to analyze sentiment and tone
            sentiment, tone_indicators = await self._analyze_with_llm(text)
            
            # Extract keywords
            keywords = self._extract_keywords(text)
            
            return ReflectionAnalysis(
                text=text,
                sentiment=sentiment,
                is_reflective=is_reflective,
                keywords=keywords,
                tone_indicators=tone_indicators
            )
            
        except Exception as e:
            logger.error(f"Error analyzing reflection: {e}")
            return ReflectionAnalysis(
                text=text,
                sentiment=SentimentType.NEUTRAL,
                is_reflective=False,
                keywords=[],
                tone_indicators={}
            )
            
    def _is_reflective(self, text: str) -> bool:
        """Check if text contains reflective language"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.reflection_keywords)
        
    def _extract_keywords(self, text: str) -> list[str]:
        """Extract relevant keywords from reflection"""
        text_lower = text.lower()
        found_keywords = [kw for kw in self.reflection_keywords if kw in text_lower]
        return found_keywords
        
    async def _analyze_with_llm(self, text: str) -> tuple[SentimentType, dict]:
        """
        Use OpenAI to analyze sentiment and tone
        
        Returns:
            (sentiment, tone_indicators dict)
        """
        try:
            prompt = f"""Analyze this meal reflection and determine:
1. The overall sentiment (calm, stressed, neutral, rushed, or mindful)
2. Tone indicators (stressed_score, mindful_score, rushed_score from 0-1)

Reflection: "{text}"

Respond in JSON format:
{{
    "sentiment": "calm|stressed|neutral|rushed|mindful",
    "tone_indicators": {{
        "stressed_score": 0.0,
        "mindful_score": 0.0,
        "rushed_score": 0.0
    }}
}}"""

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes meal reflections for emotional tone and mindfulness."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            sentiment_str = result.get("sentiment", "neutral")
            sentiment = self._parse_sentiment(sentiment_str)
            
            tone_indicators = result.get("tone_indicators", {})
            
            return sentiment, tone_indicators
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            return SentimentType.NEUTRAL, {}
            
    def _parse_sentiment(self, sentiment_str: str) -> SentimentType:
        """Parse sentiment string to SentimentType enum"""
        sentiment_map = {
            "calm": SentimentType.CALM,
            "stressed": SentimentType.STRESSED,
            "neutral": SentimentType.NEUTRAL,
            "rushed": SentimentType.RUSHED,
            "mindful": SentimentType.MINDFUL
        }
        return sentiment_map.get(sentiment_str.lower(), SentimentType.NEUTRAL)


# Global sentiment analyzer instance
sentiment_analyzer = SentimentAnalyzer()