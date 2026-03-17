"""Analytics controller."""
from app.services.AnalyticsService import AnalyticsService
from app.helpers.HttpResponse import HttpResponse
from fastapi import Depends
from app.helpers.RouteAuth import get_authenticated_user


class AnalyticsController:
    def __init__(self):
        self.service = AnalyticsService()

    async def get_heatmap(self, year: int = None, current_user=Depends(get_authenticated_user)):
        data = self.service.get_heatmap(current_user["user_id"], year)
        return HttpResponse.success(data)

    async def get_sentiment_trend(self, days: int = 30, current_user=Depends(get_authenticated_user)):
        data = self.service.get_sentiment_trend(current_user["user_id"], days)
        return HttpResponse.success(data)

    async def get_word_cloud(self, days: int = 90, current_user=Depends(get_authenticated_user)):
        data = self.service.get_word_cloud(current_user["user_id"], days)
        return HttpResponse.success(data)

    async def get_weekly_summary(self, current_user=Depends(get_authenticated_user)):
        data = self.service.get_weekly_summary(current_user["user_id"])
        return HttpResponse.success(data)

    async def get_weekly_summary_by_week(self, year: int, week: int,
                                          current_user=Depends(get_authenticated_user)):
        data = self.service.get_weekly_summary(current_user["user_id"], year, week)
        return HttpResponse.success(data)

    async def get_mood_distribution(self, days: int = 90, current_user=Depends(get_authenticated_user)):
        data = self.service.get_mood_distribution(current_user["user_id"], days)
        return HttpResponse.success(data)

    async def get_streak(self, current_user=Depends(get_authenticated_user)):
        data = self.service.get_streak(current_user["user_id"])
        return HttpResponse.success(data)

    async def get_admin_overview(self):
        data = self.service.get_admin_overview()
        return HttpResponse.success(data)

    async def get_active_users(self):
        data = self.service.get_active_users_stats()
        return HttpResponse.success(data)
