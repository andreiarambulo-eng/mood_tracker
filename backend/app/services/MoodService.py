"""Mood entry business logic service."""
import uuid
from datetime import datetime, date
from modules.database.DatabaseManager import DatabaseManager
from app.helpers.EncryptionHelper import EncryptionHelper
from app.helpers.SentimentHelper import SentimentHelper
from app.models.MoodModel import MOOD_LABELS


class MoodService:
    """Handles mood CRUD with encryption and sentiment analysis."""

    def __init__(self):
        self.moods = DatabaseManager.get_collection("moods")

    def _serialize(self, doc: dict, decrypt: bool = True) -> dict:
        """Convert MongoDB doc to API-friendly dict."""
        result = {
            "_id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "mood_score": doc["mood_score"],
            "mood_label": doc["mood_label"],
            "remark": doc.get("remark"),
            "sentiment_score": doc.get("sentiment_score", 0.0),
            "sentiment_label": doc.get("sentiment_label", "Neutral"),
            "logged_date": doc["logged_date"],
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }
        if decrypt and result["remark"]:
            result["remark"] = EncryptionHelper.decrypt_field(result["remark"]) or ""
        return result

    def create_mood(self, user_id: str, mood_score: int, remark: str = None) -> dict:
        """Create a mood entry for today (one per day enforced)."""
        today_str = date.today().isoformat()

        existing = self.moods.find_one({"user_id": user_id, "logged_date": today_str})
        if existing:
            return {"success": False, "message": "Mood already logged for today. Use edit instead."}

        sentiment = SentimentHelper.analyze(remark) if remark else {"sentiment_score": 0.0, "sentiment_label": "Neutral"}
        encrypted_remark = EncryptionHelper.encrypt_field(remark) if remark else None

        now = datetime.utcnow().isoformat()
        mood_id = str(uuid.uuid4())

        doc = {
            "_id": mood_id,
            "user_id": user_id,
            "mood_score": mood_score,
            "mood_label": MOOD_LABELS.get(mood_score, "Unknown"),
            "remark": encrypted_remark,
            "sentiment_score": sentiment["sentiment_score"],
            "sentiment_label": sentiment["sentiment_label"],
            "logged_date": today_str,
            "created_at": now,
            "updated_at": now
        }
        self.moods.insert_one(doc)

        return {"success": True, "message": "Mood logged", "data": self._serialize(doc)}

    def get_today(self, user_id: str) -> dict:
        """Get today's mood entry."""
        today_str = date.today().isoformat()
        doc = self.moods.find_one({"user_id": user_id, "logged_date": today_str})
        if not doc:
            return None
        return self._serialize(doc)

    def get_mood_by_id(self, mood_id: str, user_id: str) -> dict:
        """Get a single mood entry (must belong to user)."""
        doc = self.moods.find_one({"_id": mood_id, "user_id": user_id})
        if not doc:
            return None
        return self._serialize(doc)

    def get_moods(self, user_id: str, page: int = 1, limit: int = 10,
                  start_date: str = None, end_date: str = None) -> dict:
        """Get paginated mood entries for a user."""
        query = {"user_id": user_id}
        if start_date:
            query.setdefault("logged_date", {})["$gte"] = start_date
        if end_date:
            query.setdefault("logged_date", {})["$lte"] = end_date

        total = self.moods.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.moods.find(query).sort("logged_date", -1).skip(skip).limit(limit)

        moods = [self._serialize(doc) for doc in cursor]
        return {"data": moods, "total_count": total}

    def update_mood(self, mood_id: str, user_id: str, updates: dict) -> dict:
        """Update a mood entry (must belong to user)."""
        existing = self.moods.find_one({"_id": mood_id, "user_id": user_id})
        if not existing:
            return {"success": False, "message": "Mood entry not found"}

        set_fields = {"updated_at": datetime.utcnow().isoformat()}

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

        self.moods.update_one({"_id": mood_id}, {"$set": set_fields})

        updated = self.moods.find_one({"_id": mood_id})
        return {"success": True, "data": self._serialize(updated)}

    def delete_mood(self, mood_id: str, user_id: str) -> dict:
        """Delete a mood entry (must belong to user)."""
        result = self.moods.delete_one({"_id": mood_id, "user_id": user_id})
        return {"success": result.deleted_count > 0}
