"""Main API route registration."""
from fastapi import FastAPI, APIRouter, Depends
from app.controllers.HealthController import HealthController
from app.controllers.UserController import UserController
from app.controllers.MoodController import MoodController
from app.controllers.AnalyticsController import AnalyticsController
from app.helpers.RouteAuth import get_authenticated_user, get_admin_user
from config.app import APP_NAME


class API:
    """
    Main API class with route-based authentication.

    Three levels:
    1. unauth - Public endpoints
    2. user_auth - Any authenticated user (own data)
    3. admin_auth - Admin only
    """

    def __init__(self):
        self.app = FastAPI(
            title="Mood Tracker API",
            description="Daily mood tracking with sentiment analysis",
            version="1.0.0"
        )
        self.setup_routes()

    def setup_routes(self):
        health = HealthController()
        user = UserController()
        mood = MoodController()
        analytics = AnalyticsController()

        # ========== UNAUTH (Public) ==========
        self.app.get('/healthz')(health.healthz)
        self.app.get('/v1')(self.api_version)

        unauth = APIRouter()
        unauth.post('/auth/login')(user.login)
        unauth.post('/auth/register')(user.register)

        # ========== USER AUTH (Any Authenticated User) ==========
        user_router = APIRouter(dependencies=[Depends(get_authenticated_user)])

        # Auth
        user_router.post('/auth/logout')(user.logout)
        user_router.get('/auth/me')(user.get_current_user_info)
        user_router.post('/auth/change-password')(user.change_password)

        # Mood CRUD (own data only — enforced in service layer)
        user_router.get('/moods/get')(mood.get_moods)
        user_router.get('/moods/today')(mood.get_today)
        user_router.get('/moods/get/{mood_id}')(mood.get_mood_by_id)
        user_router.post('/moods/create')(mood.create_mood)
        user_router.patch('/moods/edit/{mood_id}')(mood.update_mood)
        user_router.delete('/moods/{mood_id}')(mood.delete_mood)

        # Analytics (own data only)
        user_router.get('/analytics/heatmap')(analytics.get_heatmap)
        user_router.get('/analytics/sentiment-trend')(analytics.get_sentiment_trend)
        user_router.get('/analytics/word-cloud')(analytics.get_word_cloud)
        user_router.get('/analytics/weekly-summary')(analytics.get_weekly_summary)
        user_router.get('/analytics/weekly-summary/{year}/{week}')(analytics.get_weekly_summary_by_week)
        user_router.get('/analytics/mood-distribution')(analytics.get_mood_distribution)
        user_router.get('/analytics/streak')(analytics.get_streak)

        # ========== ADMIN AUTH (Admin Only) ==========
        admin_router = APIRouter(dependencies=[Depends(get_admin_user)])

        admin_router.get('/users/get')(user.get_all_users)
        admin_router.get('/users/get/{user_id}')(user.get_user_by_id)
        admin_router.patch('/users/edit')(user.update_user)
        admin_router.delete('/users/{user_id}')(user.delete_user)
        admin_router.get('/admin/analytics/overview')(analytics.get_admin_overview)
        admin_router.get('/admin/analytics/active-users')(analytics.get_active_users)

        # Include routers
        self.app.include_router(unauth)
        self.app.include_router(user_router)
        self.app.include_router(admin_router)

    async def api_version(self):
        return {
            "application": APP_NAME,
            "version": "1.0.0",
            "status": "active"
        }
