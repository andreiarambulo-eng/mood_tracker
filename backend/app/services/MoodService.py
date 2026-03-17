"""Mood entry business logic service."""
from datetime import datetime, date
from bson import ObjectId
from modules.mongodb.MongoDBManager import MongoDBManager
from app.helpers.EncryptionHelper import EncryptionHelper
from app.helpers.SentimentHelper import SentimentHelper
from app.models.MoodModel import MOOD_LABELS


class MoodService:
    """Handles mood CRUD with encryption and sentiment analysis."""

    def __init__(self):
        self.collection = MongoDBManager.get_collection('moods')

    def _serialize(self, doc: dict, decrypt: bool = True) -> dict:
        """Convert MongoDB doc to API-friendly dict."""
        doc["_id"] = str(doc["_id"])
        if decrypt and doc.get("remark"):
            doc["remark"] = EncryptionHelper.decrypt_field(doc["remark"]) or ""
        if doc.get("logged_date"):
            doc["logged_date"] = doc["logged_date"].strftime("%Y-%m-%d") if isinstance(doc["logged_date"], (date, datetime)) else doc["logged_date"]
        if doc.get("created_at"):
            doc["created_at"] = doc["created_at"].isoformat()
        if doc.get("updated_at"):
            doc["updated_at"] = doc["updated_at"].isoformat()
        return doc

    def create_mood(self, user_id: str, mood_score: int, remark: str = None) -> dict:
        """Create a mood entry for today (one per day enforced)."""
        today = date.today()
        today_dt = datetime.combine(today, datetime.min.time())

        existing = self.collection.find_one({
            "user_id": user_id,
            "logged_date": today_dt
        })
        if existing:
            return {"success": False, "message": "Mood already logged for today. Use edit instead."}

        sentiment = SentimentHelper.analyze(remark) if remark else {"sentiment_score": 0.0, "sentiment_label": "Neutral"}
        encrypted_remark = EncryptionHelper.encrypt_field(remark) if remark else None

        now = datetime.utcnow()
        mood_doc = {
            "user_id": user_id,
            "mood_score": mood_score,
            "mood_label": MOOD_LABELS.get(mood_score, "Unknown"),
            "remark": encrypted_remark,
            "sentiment_score": sentiment["sentiment_score"],
            "sentiment_label": sentiment["sentiment_label"],
            "logged_date": today_dt,
            "created_at": now,
            "updated_at": now
        }

        result = self.collection.insert_one(mood_doc)
        mood_doc["_id"] = result.inserted_id
        return {"success": True, "message": "Mood logged", "data": self._serialize(mood_doc)}

    def get_today(self, user_id: str) -> dict:
        """Get today's mood entry."""
        today = date.today()
        today_dt = datetime.combine(today, datetime.min.time())
        doc = self.collection.find_one({"user_id": user_id, "logged_date": today_dt})
        if not doc:
            return None
        return self._serialize(doc)

    def get_mood_by_id(self, mood_id: str, user_id: str) -> dict:
        """Get a single mood entry (must belong to user)."""
        doc = self.collection.find_one({"_id": ObjectId(mood_id), "user_id": user_id})
        if not doc:
            return None
        return self._serialize(doc)

    def get_moods(self, user_id: str, page: int = 1, limit: int = 10,
                  start_date: str = None, end_date: str = None) -> dict:
        """Get paginated mood entries for a user."""
        query = {"user_id": user_id}

        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                date_filter["$lte"] = datetime.fromisoformat(end_date)
            query["logged_date"] = date_filter

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.collection.find(query).sort("logged_date", -1).skip(skip).limit(limit)

        moods = [self._serialize(doc) for doc in cursor]
        return {"data": moods, "total_count": total}

    def update_mood(self, mood_id: str, user_id: str, updates: dict) -> dict:
        """Update a mood entry (must belong to user)."""
        existing = self.collection.find_one({"_id": ObjectId(mood_id), "user_id": user_id})
        if not existing:
            return {"success": False, "message": "Mood entry not found"}

        set_fields = {"updated_at": datetime.utcnow()}

        if "mood_score" in updates and updates["mood_score"] is not None:
            set_fields["mood_score"] = updates["mood_score"]
            set_fields["mood_label"] = MOOD_LABELS.get(updates["mood_score"], "Unknown")

        if "remark" in updates:
            remark = updates["remark"]
            if remark:
                set_fields["remark"] = EncryptionHelper.encrypt_field(remark)
                sentiment = SentimentHelper.analyze(remark)
                set_fields["sentiment_score"] = sentiment["sentiment_score"]
                set_fields["sentiment_label"] = sentiment["sentiment_label"]
            else:
                set_fields["remark"] = None
                set_fields["sentiment_score"] = 0.0
                set_fields["sentiment_label"] = "Neutral"

        self.collection.update_one({"_id": ObjectId(mood_id)}, {"$set": set_fields})

        updated = self.collection.find_one({"_id": ObjectId(mood_id)})
        return {"success": True, "data": self._serialize(updated)}

    def delete_mood(self, mood_id: str, user_id: str) -> dict:
        """Delete a mood entry (must belong to user)."""
        result = self.collection.delete_one({"_id": ObjectId(mood_id), "user_id": user_id})
        return {"success": result.deleted_count > 0}
