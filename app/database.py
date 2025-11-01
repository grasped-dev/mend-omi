import firebase_admin
from firebase_admin import credentials, firestore
from config import settings
from app.models import MealEvent, MealEventCreate
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """Firebase Firestore database client for Mend"""
    
    def __init__(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': settings.firebase_database_url
            })
        
        self.db = firestore.client()
        self.collection = self.db.collection('meal_events')
        
    async def create_meal_event(self, event: MealEventCreate) -> MealEvent:
        """Create a new meal event in Firestore"""
        try:
            data = {
                "uid": event.uid,
                "timestamp": datetime.utcnow(),
                "event_type": event.event_type.value,
                "duration": event.duration,
                "reflection_text": event.reflection_text,
                "sentiment": event.sentiment.value if event.sentiment else None,
                "cue_sent": False
            }
            
            doc_ref = self.collection.document()
            doc_ref.set(data)
            
            # Get the created document
            doc = doc_ref.get()
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id
            
            return MealEvent(**doc_data)
                
        except Exception as e:
            logger.error(f"Error creating meal event: {e}")
            raise
            
    async def get_user_events(
        self, 
        uid: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MealEvent]:
        """Get meal events for a user within a date range"""
        try:
            query = self.collection.where('uid', '==', uid)
            
            if start_date:
                query = query.where('timestamp', '>=', start_date)
            if end_date:
                query = query.where('timestamp', '<=', end_date)
                
            docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
            
            events = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                events.append(MealEvent(**data))
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting user events: {e}")
            return []
            
    async def get_last_feedback_time(self, uid: str) -> Optional[datetime]:
        """Get the timestamp of the last feedback sent to user"""
        try:
            docs = (
                self.collection
                .where('uid', '==', uid)
                .where('cue_sent', '==', True)
                .order_by('timestamp', direction=firestore.Query.DESCENDING)
                .limit(1)
                .stream()
            )
            
            for doc in docs:
                data = doc.to_dict()
                return data.get('timestamp')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting last feedback time: {e}")
            return None
            
    async def mark_feedback_sent(self, event_id: str) -> bool:
        """Mark that feedback was sent for an event"""
        try:
            doc_ref = self.collection.document(event_id)
            doc_ref.update({'cue_sent': True})
            return True
            
        except Exception as e:
            logger.error(f"Error marking feedback sent: {e}")
            return False
            
    async def get_weekly_stats(self, uid: str, week_start: datetime) -> dict:
        """Get statistics for a user's week"""
        try:
            week_end = week_start + timedelta(days=7)
            
            events = await self.get_user_events(uid, week_start, week_end)
            
            meals = [e for e in events if e.event_type in ["meal_start", "meal_end"]]
            reflections = [e for e in events if e.reflection_text]
            
            durations = [e.duration for e in events if e.duration]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            sentiment_counts = {}
            for event in events:
                if event.sentiment:
                    sentiment = event.sentiment.value
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            return {
                "total_meals": len(meals),
                "reflections_count": len(reflections),
                "avg_meal_duration": avg_duration,
                "sentiment_breakdown": sentiment_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly stats: {e}")
            return {}


# Global database instance
db = Database()