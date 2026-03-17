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
        self.db = DatabaseManager()

    def _serialize(self, row: dict, decrypt: bool = True) -> dict:
        """Convert DB row to API-friendly dict."""
        doc = dict(row)
        doc["_id"] = doc.pop("id")
        if decrypt and doc.get("remark"):
            doc["remark"] = EncryptionHelper.decrypt_field(doc["remark"]) or ""
        return doc

    def create_mood(self, user_id: str, mood_score: int, remark: str = None) -> dict:
        """Create a mood entry for today (one per day enforced)."""
        today_str = date.today().isoformat()

        existing = self.db.fetchone(
            "SELECT id FROM moods WHERE user_id = ? AND logged_date = ?",
            (user_id, today_str)
        )
        if existing:
            return {"success": False, "message": "Mood already logged for today. Use edit instead."}

        sentiment = SentimentHelper.analyze(remark) if remark else {"sentiment_score": 0.0, "sentiment_label": "Neutral"}
        encrypted_remark = EncryptionHelper.encrypt_field(remark) if remark else None

        now = datetime.utcnow().isoformat()
        mood_id = str(uuid.uuid4())

        self.db.execute_and_commit(
            """INSERT INTO moods (id, user_id, mood_score, mood_label, remark, sentiment_score, sentiment_label, logged_date, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (mood_id, user_id, mood_score, MOOD_LABELS.get(mood_score, "Unknown"),
             encrypted_remark, sentiment["sentiment_score"], sentiment["sentiment_label"],
             today_str, now, now)
        )

        row = self.db.fetchone("SELECT * FROM moods WHERE id = ?", (mood_id,))
        return {"success": True, "message": "Mood logged", "data": self._serialize(row)}

    def get_today(self, user_id: str) -> dict:
        """Get today's mood entry."""
        today_str = date.today().isoformat()
        row = self.db.fetchone(
            "SELECT * FROM moods WHERE user_id = ? AND logged_date = ?",
            (user_id, today_str)
        )
        if not row:
            return None
        return self._serialize(row)

    def get_mood_by_id(self, mood_id: str, user_id: str) -> dict:
        """Get a single mood entry (must belong to user)."""
        row = self.db.fetchone(
            "SELECT * FROM moods WHERE id = ? AND user_id = ?",
            (mood_id, user_id)
        )
        if not row:
            return None
        return self._serialize(row)

    def get_moods(self, user_id: str, page: int = 1, limit: int = 10,
                  start_date: str = None, end_date: str = None) -> dict:
        """Get paginated mood entries for a user."""
        conditions = ["user_id = ?"]
        params = [user_id]

        if start_date:
            conditions.append("logged_date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("logged_date <= ?")
            params.append(end_date)

        where = " AND ".join(conditions)
        total = self.db.fetchone(f"SELECT COUNT(*) as cnt FROM moods WHERE {where}", tuple(params))["cnt"]

        skip = (page - 1) * limit
        rows = self.db.fetchall(
            f"SELECT * FROM moods WHERE {where} ORDER BY logged_date DESC LIMIT ? OFFSET ?",
            tuple(params + [limit, skip])
        )

        moods = [self._serialize(row) for row in rows]
        return {"data": moods, "total_count": total}

    def update_mood(self, mood_id: str, user_id: str, updates: dict) -> dict:
        """Update a mood entry (must belong to user)."""
        existing = self.db.fetchone(
            "SELECT * FROM moods WHERE id = ? AND user_id = ?",
            (mood_id, user_id)
        )
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

        set_clauses = ", ".join(f"{k} = ?" for k in set_fields)
        values = list(set_fields.values()) + [mood_id]
        self.db.execute_and_commit(f"UPDATE moods SET {set_clauses} WHERE id = ?", tuple(values))

        updated = self.db.fetchone("SELECT * FROM moods WHERE id = ?", (mood_id,))
        return {"success": True, "data": self._serialize(updated)}

    def delete_mood(self, mood_id: str, user_id: str) -> dict:
        """Delete a mood entry (must belong to user)."""
        cursor = self.db.execute_and_commit(
            "DELETE FROM moods WHERE id = ? AND user_id = ?",
            (mood_id, user_id)
        )
        return {"success": cursor.rowcount > 0}
