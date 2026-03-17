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
        self.db = DatabaseManager()

    def get_heatmap(self, user_id: str, year: int = None) -> list:
        """Get 12-month heatmap data."""
        if not year:
            year = date.today().year

        start = f"{year}-01-01"
        end = f"{year}-12-31"

        rows = self.db.fetchall(
            "SELECT logged_date, mood_score, mood_label FROM moods WHERE user_id = ? AND logged_date >= ? AND logged_date <= ? ORDER BY logged_date",
            (user_id, start, end)
        )

        return [{"date": r["logged_date"], "mood_score": r["mood_score"], "mood_label": r["mood_label"]} for r in rows]

    def get_sentiment_trend(self, user_id: str, days: int = 30) -> list:
        """Get sentiment scores over time."""
        start = (date.today() - timedelta(days=days)).isoformat()

        rows = self.db.fetchall(
            "SELECT logged_date, sentiment_score, sentiment_label, mood_score FROM moods WHERE user_id = ? AND logged_date >= ? ORDER BY logged_date",
            (user_id, start)
        )

        return [
            {"date": r["logged_date"], "sentiment_score": r["sentiment_score"],
             "sentiment_label": r["sentiment_label"], "mood_score": r["mood_score"]}
            for r in rows
        ]

    def get_word_cloud(self, user_id: str, days: int = 90) -> list:
        """Get word frequencies from remarks for word cloud."""
        start = (date.today() - timedelta(days=days)).isoformat()

        rows = self.db.fetchall(
            "SELECT remark FROM moods WHERE user_id = ? AND logged_date >= ? AND remark IS NOT NULL",
            (user_id, start)
        )

        word_counter = Counter()
        for row in rows:
            decrypted = EncryptionHelper.decrypt_field(row["remark"])
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

        rows = self.db.fetchall(
            "SELECT * FROM moods WHERE user_id = ? AND logged_date >= ? AND logged_date <= ? ORDER BY logged_date",
            (user_id, week_start.isoformat(), week_end.isoformat())
        )

        if not rows:
            return {
                "year": year, "week": week,
                "week_start": week_start.isoformat(), "week_end": week_end.isoformat(),
                "total_entries": 0, "average_mood": None, "average_sentiment": None,
                "most_common_mood": None, "days": []
            }

        mood_scores = [r["mood_score"] for r in rows]
        sentiment_scores = [r["sentiment_score"] or 0 for r in rows]
        mood_counter = Counter([r["mood_label"] for r in rows])

        days = []
        for r in rows:
            remark = EncryptionHelper.decrypt_field(r["remark"]) if r["remark"] else None
            days.append({
                "date": r["logged_date"],
                "mood_score": r["mood_score"],
                "mood_label": r["mood_label"],
                "sentiment_score": r["sentiment_score"] or 0,
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

        rows = self.db.fetchall(
            "SELECT mood_score, mood_label, COUNT(*) as count FROM moods WHERE user_id = ? AND logged_date >= ? GROUP BY mood_score, mood_label ORDER BY mood_score",
            (user_id, start)
        )

        return [{"mood_score": r["mood_score"], "mood_label": r["mood_label"], "count": r["count"]} for r in rows]

    def get_streak(self, user_id: str) -> dict:
        """Calculate current consecutive logging streak."""
        today = date.today()
        streak = 0
        check_date = today

        while True:
            row = self.db.fetchone(
                "SELECT id FROM moods WHERE user_id = ? AND logged_date = ?",
                (user_id, check_date.isoformat())
            )
            if row:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return {"current_streak": streak, "as_of": today.isoformat()}

    def get_admin_overview(self) -> dict:
        """Platform-wide mood averages (admin only, no PII)."""
        total_users = self.db.fetchone("SELECT COUNT(*) as cnt FROM users WHERE is_active = 1")["cnt"]
        total_entries = self.db.fetchone("SELECT COUNT(*) as cnt FROM moods")["cnt"]

        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()

        row = self.db.fetchone(
            "SELECT AVG(mood_score) as avg_mood, COUNT(*) as count FROM moods WHERE logged_date >= ?",
            (week_start,)
        )

        return {
            "total_users": total_users,
            "total_entries": total_entries,
            "this_week_avg_mood": round(row["avg_mood"], 2) if row["avg_mood"] else None,
            "this_week_entries": row["count"]
        }

    def get_active_users_stats(self) -> list:
        """User engagement stats (admin only, no remarks)."""
        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()

        rows = self.db.fetchall(
            """SELECT m.user_id, u.full_name, COUNT(*) as entries_this_week, AVG(m.mood_score) as avg_mood
               FROM moods m JOIN users u ON m.user_id = u.id
               WHERE m.logged_date >= ?
               GROUP BY m.user_id, u.full_name
               ORDER BY entries_this_week DESC""",
            (week_start,)
        )

        return [
            {"user_id": r["user_id"], "full_name": r["full_name"],
             "entries_this_week": r["entries_this_week"], "avg_mood": round(r["avg_mood"], 2)}
            for r in rows
        ]
