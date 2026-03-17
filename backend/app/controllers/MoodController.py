"""Mood controller — thin layer delegating to MoodService."""
from app.services.MoodService import MoodService
from app.models.MoodModel import MoodCreate, MoodUpdate
from app.helpers.HttpResponse import HttpResponse
from app.helpers.PaginationHelper import PaginationHelper
from fastapi import Depends
from app.helpers.RouteAuth import get_authenticated_user


class MoodController:
    def __init__(self):
        self.service = MoodService()

    async def create_mood(self, body: MoodCreate, current_user=Depends(get_authenticated_user)):
        result = self.service.create_mood(current_user["user_id"], body.mood_score, body.remark)
        if not result["success"]:
            return HttpResponse.error(result["message"], 409)
        return HttpResponse.success(result["data"], result["message"], 201)

    async def get_today(self, current_user=Depends(get_authenticated_user)):
        mood = self.service.get_today(current_user["user_id"])
        if not mood:
            return HttpResponse.error("No mood logged today", 404)
        return HttpResponse.success(mood)

    async def get_mood_by_id(self, mood_id: str, current_user=Depends(get_authenticated_user)):
        mood = self.service.get_mood_by_id(mood_id, current_user["user_id"])
        if not mood:
            return HttpResponse.error("Mood entry not found", 404)
        return HttpResponse.success(mood)

    async def get_moods(self, page: int = 1, limit: int = 10,
                        start_date: str = None, end_date: str = None,
                        current_user=Depends(get_authenticated_user)):
        result = self.service.get_moods(current_user["user_id"], page, limit, start_date, end_date)
        pagination = PaginationHelper.get_pagination(page, limit, result["total_count"])
        return HttpResponse.paginated(result["data"], pagination)

    async def update_mood(self, mood_id: str, body: MoodUpdate,
                          current_user=Depends(get_authenticated_user)):
        updates = body.model_dump(exclude_unset=True)
        result = self.service.update_mood(mood_id, current_user["user_id"], updates)
        if not result["success"]:
            return HttpResponse.error(result["message"], 404)
        return HttpResponse.success(result["data"], "Mood updated")

    async def delete_mood(self, mood_id: str, current_user=Depends(get_authenticated_user)):
        result = self.service.delete_mood(mood_id, current_user["user_id"])
        if not result["success"]:
            return HttpResponse.error("Mood entry not found", 404)
        return HttpResponse.success(message="Mood deleted")
