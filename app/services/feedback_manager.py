from app.services.omi_client import omi_client
from app.database import db
from datetime import datetime, timedelta
from config import settings
import logging

logger = logging.getLogger(__name__)


class FeedbackManager:
    """
    Manages feedback notifications with rate limiting
    Ensures users aren't overwhelmed with notifications
    """
    
    def __init__(self):
        self.cooldown_seconds = settings.feedback_cooldown_seconds
        
        # Feedback message templates
        self.messages = {
            "slow_down": "Take a deep breath 🌿 Eating slowly helps digestion and mindfulness.",
            "mindful": "Great mindful eating! 🧘 Keep up the awareness.",
            "stressed": "Notice any tension? 💆 Try taking a pause between bites.",
            "rushed": "Slow down ⏸️ Enjoy each bite and savor your meal.",
        }
        
    async def send_feedback(
        self, 
        uid: str, 
        feedback_type: str,
        force: bool = False
    ) -> bool:
        """
        Send feedback notification to user with rate limiting
        
        Args:
            uid: User's Omi UID
            feedback_type: Type of feedback to send (slow_down, mindful, stressed, rushed)
            force: If True, bypass rate limiting
            
        Returns:
            True if feedback was sent
        """
        try:
            # Check rate limiting
            if not force and not await self._can_send_feedback(uid):
                logger.info(f"Feedback rate limited for user {uid}")
                return False
                
            # Get message
            message = self.messages.get(feedback_type, self.messages["slow_down"])
            
            # Send notification via Omi
            success = await omi_client.send_notification(uid, message)
            
            if success:
                logger.info(f"Feedback sent to {uid}: {feedback_type}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending feedback: {e}")
            return False
            
    async def _can_send_feedback(self, uid: str) -> bool:
        """
        Check if enough time has passed since last feedback
        
        Args:
            uid: User's Omi UID
            
        Returns:
            True if feedback can be sent
        """
        try:
            last_feedback_time = await db.get_last_feedback_time(uid)
            
            if last_feedback_time is None:
                return True
                
            time_since_last = datetime.utcnow() - last_feedback_time
            
            return time_since_last.total_seconds() >= self.cooldown_seconds
            
        except Exception as e:
            logger.error(f"Error checking feedback cooldown: {e}")
            return True  # Allow feedback on error
            
    async def should_send_rushed_feedback(
        self, 
        meal_duration: int,
        expected_duration: int = 900  # 15 minutes
    ) -> bool:
        """
        Determine if rushed eating feedback should be sent
        
        Args:
            meal_duration: Actual meal duration in seconds
            expected_duration: Expected meal duration in seconds
            
        Returns:
            True if meal was rushed
        """
        # If meal is less than 50% of expected duration
        return meal_duration < (expected_duration * 0.5)


# Global feedback manager instance
feedback_manager = FeedbackManager()