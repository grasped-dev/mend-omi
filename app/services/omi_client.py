import httpx
from config import settings
from app.models import FeedbackNotification
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class OmiClient:
    """Client for interacting with Omi API"""
    
    def __init__(self):
        self.base_url = settings.omi_api_base_url
        self.app_id = settings.omi_app_id
        self.app_secret = settings.omi_app_secret
        
    def _get_headers(self) -> dict:
        """Get authorization headers for Omi API"""
        return {
            "Authorization": f"Bearer {self.app_secret}",
            "Content-Type": "application/json"
        }
        
    async def send_notification(self, uid: str, message: str) -> bool:
        """
        Send a notification to the user via Omi
        
        Args:
            uid: User's Omi UID
            message: Notification message
            
        Returns:
            True if notification was sent successfully
        """
        try:
            url = f"{self.base_url}/v2/integrations/{self.app_id}/notification"
            params = {
                "uid": uid,
                "message": message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=10.0
                )
                
            if response.status_code == 200:
                logger.info(f"Notification sent to {uid}: {message}")
                return True
            else:
                logger.error(f"Failed to send notification: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
            
    async def create_memory(
        self, 
        uid: str, 
        title: str, 
        content: str,
        structured_data: Optional[dict] = None
    ) -> bool:
        """
        Create a memory entry in the user's Omi timeline
        
        Args:
            uid: User's Omi UID
            title: Memory title
            content: Memory content/description
            structured_data: Optional structured data
            
        Returns:
            True if memory was created successfully
        """
        try:
            url = f"{self.base_url}/v1/memories"
            
            payload = {
                "uid": uid,
                "title": title,
                "content": content,
            }
            
            if structured_data:
                payload["structured"] = structured_data
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=10.0
                )
                
            if response.status_code in [200, 201]:
                logger.info(f"Memory created for {uid}: {title}")
                return True
            else:
                logger.error(f"Failed to create memory: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating memory: {e}")
            return False


# Global Omi client instance
omi_client = OmiClient()