"""Standardized HTTP response helpers."""
from fastapi.responses import JSONResponse


class HttpResponse:
    """Helper for consistent API responses."""

    @staticmethod
    def success(data=None, message="Success", status_code=200):
        return JSONResponse(
            status_code=status_code,
            content={"success": True, "message": message, "data": data}
        )

    @staticmethod
    def error(message="Error", status_code=400):
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": message}
        )

    @staticmethod
    def paginated(data, pagination, message="Success"):
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": message,
                "data": {"data": data, "pagination": pagination}
            }
        )
