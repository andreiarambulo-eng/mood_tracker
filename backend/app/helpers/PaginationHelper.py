"""Pagination calculation helper."""
import math


class PaginationHelper:
    """Helper for pagination calculations."""

    @staticmethod
    def get_pagination(page: int, limit: int, total_count: int) -> dict:
        total_pages = math.ceil(total_count / limit) if limit > 0 else 0
        return {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

    @staticmethod
    def get_skip(page: int, limit: int) -> int:
        return (page - 1) * limit
