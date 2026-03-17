"""Analytics service for mood data aggregation."""
from datetime import datetime, date, timedelta
from collections import Counter
import re
from bson import ObjectId
from modules.mongodb.MongoDBManager import MongoDBManager
from app.helpers.EncryptionHelper import EncryptionHelper


class AnalyticsService:
    """Computes mood analytics and aggregations."""

    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why",
        "how", "all", "each", "every", "both", "few", "more", "most",
        "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "just", "because", "but", "and", "or",
        "if", "while", "about", "up", "it", "i", "me", "my", "myself",
        "we", "our", "you", "your", "he", "him", "she", "her", "they",
        "them", "what", "which", "who", "this", "that", "these", "those",
        "am", "its", "let", "got", "get", "go", "going", "went", "really",
        "feel", "feeling", "felt", "today", "day", "much", "like", "also",
        "still", "even", "well", "back", "thing", "things", "lot", "bit"
    }

    def __init__(self):
        self.collection = MongoDBManager.get_collection('moods')

    def get_heatmap(self, user_id: str, year: int = None) -> list:
        """Get 12-month heatmap data."""
        if not year:
            year = date.today().year

        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31, 23, 59, 59)

        cursor = self.collection.find(
            {"user_id": user_id, "logged_date": {"$gte": start, "$lte": end}},
            {"logged_date": 1, "mood_score": 1, "mood_label": 1}
        ).sort("logged_date", 1)

        return [
            {
                "date": doc["logged_date"].strftime("%Y-%m-%d"),
                "mood_score": doc["mood_score"],
                "mood_label": doc.get("mood_label", "")
            }
            for doc in cursor
        ]

    def get_sentiment_trend(self, user_id: str, days: int = 30) -> list:
        """Get sentiment scores over time."""
        start = datetime.combine(date.today() - timedelta(days=days), datetime.min.time())

        cursor = self.collection.find(
            {"user_id": user_id, "logged_date": {"$gte": start}},
            {"logged_date": 1, "sentiment_score": 1, "sentiment_label": 1, "mood_score": 1}
        ).sort("logged_date", 1)

        return [
            {
                "date": doc["logged_date"].strftime("%Y-%m-%d"),
                "sentiment_score": doc.get("sentiment_score", 0),
                "sentiment_label": doc.get("sentiment_label", "Neutral"),
                "mood_score": doc["mood_score"]
            }
            for doc in cursor
        ]

    def get_word_cloud(self, user_id: str, days: int = 90) -> list:
        """Get word frequencies from remarks for word cloud."""
        start = datetime.combine(date.today() - timedelta(days=days), datetime.min.time())

        cursor = self.collection.find(
            {"user_id": user_id, "logged_date": {"$gte": start}, "remark": {"$ne": None}},
            {"remark": 1}
        )

        word_counter = Counter()
        for doc in cursor:
            decrypted = EncryptionHelper.decrypt_field(doc["remark"])
            if decrypted:
                words = re.findall(r'[a-zA-Z]{3,}', decrypted.lower())
                filtered = [w for w in words if w not in self.STOP_WORDS]
                word_counter.update(filtered)

        return [
            {"word": word, "count": count}
            for word, count in word_counter.most_common(80)
        ]

    def get_weekly_summary(self, user_id: str, year: int = None, week: int = None) -> dict:
        """Get summary for a specific ISO week."""
        if not year or not week:
            today = date.today()
            year, week, _ = today.isocalendar()

        jan4 = date(year, 1, 4)
        start_of_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
        week_start = start_of_week1 + timedelta(weeks=week - 1)
        week_end = week_start + timedelta(days=6)

        start_dt = datetime.combine(week_start, datetime.min.time())
        end_dt = datetime.combine(week_end, datetime.max.time())

        cursor = self.collection.find(
            {"user_id": user_id, "logged_date": {"$gte": start_dt, "$lte": end_dt}}
        ).sort("logged_date", 1)

        entries = list(cursor)

        if not entries:
            return {
                "year": year, "week": week,
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "total_entries": 0,
                "average_mood": None,
                "average_sentiment": None,
                "most_common_mood": None,
                "days": []
            }

        mood_scores = [e["mood_score"] for e in entries]
        sentiment_scores = [e.get("sentiment_score", 0) for e in entries]
        mood_counter = Counter([e.get("mood_label", "") for e in entries])

        days = []
        for e in entries:
            remark = EncryptionHelper.decrypt_field(e.get("remark")) if e.get("remark") else None
            days.append({
                "date": e["logged_date"].strftime("%Y-%m-%d"),
                "mood_score": e["mood_score"],
                "mood_label": e.get("mood_label", ""),
                "sentiment_score": e.get("sentiment_score", 0),
                "remark_preview": (remark[:80] + "...") if remark and len(remark) > 80 else remark
            })

        return {
            "year": year,
            "week": week,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "total_entries": len(entries),
            "average_mood": round(sum(mood_scores) / len(mood_scores), 2),
            "average_sentiment": round(sum(sentiment_scores) / len(sentiment_scores), 4),
            "most_common_mood": mood_counter.most_common(1)[0][0] if mood_counter else None,
            "days": days
        }

    def get_mood_distribution(self, user_id: str, days: int = 90) -> list:
        """Get mood score distribution."""
        start = datetime.combine(date.today() - timedelta(days=days), datetime.min.time())

        pipeline = [
            {"$match": {"user_id": user_id, "logged_date": {"$gte": start}}},
            {"$group": {"_id": "$mood_score", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]

        results = list(self.collection.aggregate(pipeline))

        from app.models.MoodModel import MOOD_LABELS
        return [
            {
                "mood_score": r["_id"],
                "mood_label": MOOD_LABELS.get(r["_id"], "Unknown"),
                "count": r["count"]
            }
            for r in results
        ]

    def get_streak(self, user_id: str) -> dict:
        """Calculate current consecutive logging streak."""
        today = date.today()
        streak = 0
        check_date = today

        while True:
            check_dt = datetime.combine(check_date, datetime.min.time())
            exists = self.collection.find_one({"user_id": user_id, "logged_date": check_dt})
            if exists:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return {"current_streak": streak, "as_of": today.isoformat()}

    def get_admin_overview(self) -> dict:
        """Platform-wide mood averages (admin only, no PII)."""
        users_col = MongoDBManager.get_collection('users')
        total_users = users_col.count_documents({"is_active": True})
        total_entries = self.collection.count_documents({})

        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())

        pipeline = [
            {"$match": {"logged_date": {"$gte": week_start_dt}}},
            {"$group": {"_id": None, "avg_mood": {"$avg": "$mood_score"}, "count": {"$sum": 1}}}
        ]
        result = list(self.collection.aggregate(pipeline))

        return {
            "total_users": total_users,
            "total_entries": total_entries,
            "this_week_avg_mood": round(result[0]["avg_mood"], 2) if result else None,
            "this_week_entries": result[0]["count"] if result else 0
        }

    def get_active_users_stats(self) -> list:
        """User engagement stats (admin only, no remarks)."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())

        pipeline = [
            {"$match": {"logged_date": {"$gte": week_start_dt}}},
            {"$group": {
                "_id": "$user_id",
                "entries_this_week": {"$sum": 1},
                "avg_mood": {"$avg": "$mood_score"}
            }},
            {"$sort": {"entries_this_week": -1}}
        ]

        results = list(self.collection.aggregate(pipeline))

        users_col = MongoDBManager.get_collection('users')
        output = []
        for r in results:
            user = users_col.find_one({"_id": ObjectId(r["_id"])}, {"full_name": 1, "email": 1})
            output.append({
                "user_id": r["_id"],
                "full_name": user["full_name"] if user else "Unknown",
                "entries_this_week": r["entries_this_week"],
                "avg_mood": round(r["avg_mood"], 2)
            })

        return output
