"""Health check controller."""
from modules.database.DatabaseManager import DatabaseManager
from app.helpers.HttpResponse import HttpResponse


class HealthController:
    async def healthz(self):
        is_healthy = DatabaseManager.ping()
        if is_healthy:
            return HttpResponse.success(message="Healthy")
        return HttpResponse.error("Database unreachable", 503)
