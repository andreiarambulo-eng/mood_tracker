"""Analytics service for mood data aggregation."""
from datetime import datetime, date, timedelta
from collections import Counter
import re
from modules.database.DatabaseManager import DatabaseManager
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
        self.moods = DatabaseManager.get_collection("moods")
        self.users = DatabaseManager.get_collection("users")

    def get_heatmap(self, user_id: str, year: int = None) -> list:
        """Get 12-month heatmap data."""
        if not year:
            year = date.today().year

        start = f"{year}-01-01"
        end = f"{year}-12-31"

        cursor = self.moods.find(
            {"user_id": user_id, "logged_date": {"$gte": start, "$lte": end}},
            {"logged_date": 1, "mood_score": 1, "mood_label": 1}
        ).sort("logged_date", 1)

        return [{"date": d["logged_date"], "mood_score": d["mood_score"], "mood_label": d["mood_label"]} for d in cursor]

    def get_sentiment_trend(self, user_id: str, days: int = 30) -> list:
        """Get sentiment scores over time."""
        start = (date.today() - timedelta(days=days)).isoformat()

        cursor = self.moods.find(
            {"user_id": user_id, "logged_date": {"$gte": start}},
            {"logged_date": 1, "sentiment_score": 1, "sentiment_label": 1, "mood_score": 1}
        ).sort("logged_date", 1)

        return [
            {"date": d["logged_date"], "sentiment_score": d["sentiment_score"],
             "sentiment_label": d["sentiment_label"], "mood_score": d["mood_score"]}
            for d in cursor
        ]

    def get_word_cloud(self, user_id: str, days: int = 90) -> list:
        """Get word frequencies from remarks for word cloud."""
        start = (date.today() - timedelta(days=days)).isoformat()

        cursor = self.moods.find(
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

        return [{"word": word, "count": count} for word, count in word_counter.most_common(80)]

    def get_weekly_summary(self, user_id: str, year: int = None, week: int = None) -> dict:
        """Get summary for a specific ISO week."""
        if not year or not week:
            today = date.today()
            year, week, _ = today.isocalendar()

        jan4 = date(year, 1, 4)
        start_of_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
        week_start = start_of_week1 + timedelta(weeks=week - 1)
        week_end = week_start + timedelta(days=6)

        cursor = self.moods.find(
            {"user_id": user_id, "logged_date": {"$gte": week_start.isoformat(), "$lte": week_end.isoformat()}}
        ).sort("logged_date", 1)

        rows = list(cursor)

        if not rows:
            return {
                "year": year, "week": week,
                "week_start": week_start.isoformat(), "week_end": week_end.isoformat(),
                "total_entries": 0, "average_mood": None, "average_sentiment": None,
                "most_common_mood": None, "days": []
            }

        mood_scores = [r["mood_score"] for r in rows]
        sentiment_scores = [r.get("sentiment_score") or 0 for r in rows]
        mood_counter = Counter([r["mood_label"] for r in rows])

        days = []
        for r in rows:
            remark = EncryptionHelper.decrypt_field(r["remark"]) if r.get("remark") else None
            days.append({
                "date": r["logged_date"],
                "mood_score": r["mood_score"],
                "mood_label": r["mood_label"],
                "sentiment_score": r.get("sentiment_score") or 0,
                "remark_preview": (remark[:80] + "...") if remark and len(remark) > 80 else remark
            })

        return {
            "year": year, "week": week,
            "week_start": week_start.isoformat(), "week_end": week_end.isoformat(),
            "total_entries": len(rows),
            "average_mood": round(sum(mood_scores) / len(mood_scores), 2),
            "average_sentiment": round(sum(sentiment_scores) / len(sentiment_scores), 4),
            "most_common_mood": mood_counter.most_common(1)[0][0] if mood_counter else None,
            "days": days
        }

    def get_mood_distribution(self, user_id: str, days: int = 90) -> list:
        """Get mood score distribution."""
        start = (date.today() - timedelta(days=days)).isoformat()

        pipeline = [
            {"$match": {"user_id": user_id, "logged_date": {"$gte": start}}},
            {"$group": {"_id": {"mood_score": "$mood_score", "mood_label": "$mood_label"}, "count": {"$sum": 1}}},
            {"$sort": {"_id.mood_score": 1}}
        ]

        results = list(self.moods.aggregate(pipeline))
        return [{"mood_score": r["_id"]["mood_score"], "mood_label": r["_id"]["mood_label"], "count": r["count"]} for r in results]

    def get_streak(self, user_id: str) -> dict:
        """Calculate current consecutive logging streak."""
        today = date.today()
        streak = 0
        check_date = today

        while True:
            doc = self.moods.find_one({"user_id": user_id, "logged_date": check_date.isoformat()})
            if doc:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return {"current_streak": streak, "as_of": today.isoformat()}

    def get_admin_overview(self) -> dict:
        """Platform-wide mood averages (admin only, no PII)."""
        total_users = self.users.count_documents({"is_active": True})
        total_entries = self.moods.count_documents({})

        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()

        pipeline = [
            {"$match": {"logged_date": {"$gte": week_start}}},
            {"$group": {"_id": None, "avg_mood": {"$avg": "$mood_score"}, "count": {"$sum": 1}}}
        ]
        result = list(self.moods.aggregate(pipeline))

        if result:
            return {
                "total_users": total_users,
                "total_entries": total_entries,
                "this_week_avg_mood": round(result[0]["avg_mood"], 2) if result[0]["avg_mood"] else None,
                "this_week_entries": result[0]["count"]
            }

        return {
            "total_users": total_users,
            "total_entries": total_entries,
            "this_week_avg_mood": None,
            "this_week_entries": 0
        }

    def get_active_users_stats(self) -> list:
        """User engagement stats (admin only, no remarks)."""
        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()

        pipeline = [
            {"$match": {"logged_date": {"$gte": week_start}}},
            {"$group": {
                "_id": "$user_id",
                "entries_this_week": {"$sum": 1},
                "avg_mood": {"$avg": "$mood_score"}
            }},
            {"$sort": {"entries_this_week": -1}}
        ]
        mood_results = list(self.moods.aggregate(pipeline))

        # Lookup user names
        user_ids = [r["_id"] for r in mood_results]
        users_map = {}
        if user_ids:
            for u in self.users.find({"_id": {"$in": user_ids}}, {"full_name": 1}):
                users_map[u["_id"]] = u["full_name"]

        return [
            {"user_id": r["_id"], "full_name": users_map.get(r["_id"], "Unknown"),
             "entries_this_week": r["entries_this_week"], "avg_mood": round(r["avg_mood"], 2)}
            for r in mood_results
        ]
