"""Health check controller."""
from modules.mongodb.MongoDBManager import MongoDBManager
from app.helpers.HttpResponse import HttpResponse


class HealthController:
    async def healthz(self):
        is_healthy = MongoDBManager.ping()
        if is_healthy:
            return HttpResponse.success(message="Healthy")
        return HttpResponse.error("MongoDB unreachable", 503)
