"""User controller — thin layer delegating to UserService."""
from app.services.UserService import UserService
from app.models.UserModel import UserCreate, UserLogin, UserUpdate, ChangePassword
from app.helpers.HttpResponse import HttpResponse
from app.helpers.PaginationHelper import PaginationHelper
from fastapi import Depends
from app.helpers.RouteAuth import get_authenticated_user


class UserController:
    def __init__(self):
        self.service = UserService()

    async def register(self, body: UserCreate):
        result = self.service.register(body.email, body.full_name, body.password)
        if not result["success"]:
            return HttpResponse.error(result["message"], 409)
        return HttpResponse.success(result["data"], result["message"], 201)

    async def login(self, body: UserLogin):
        result = self.service.login(body.email, body.password)
        if not result["success"]:
            return HttpResponse.error(result["message"], 401)
        return HttpResponse.success(result["data"], result["message"])

    async def logout(self):
        return HttpResponse.success(message="Logged out successfully")

    async def get_current_user_info(self, current_user=Depends(get_authenticated_user)):
        return HttpResponse.success(current_user)

    async def change_password(self, body: ChangePassword, current_user=Depends(get_authenticated_user)):
        result = self.service.change_password(
            current_user["user_id"], body.current_password, body.new_password
        )
        if not result["success"]:
            return HttpResponse.error(result["message"])
        return HttpResponse.success(message=result["message"])

    async def get_all_users(self, page: int = 1, limit: int = 10):
        result = self.service.get_all_users(page, limit)
        pagination = PaginationHelper.get_pagination(page, limit, result["total_count"])
        return HttpResponse.paginated(result["data"], pagination)

    async def get_user_by_id(self, user_id: str):
        user = self.service.get_user_by_id(user_id)
        if not user:
            return HttpResponse.error("User not found", 404)
        return HttpResponse.success(user)

    async def update_user(self, body: UserUpdate):
        updates = body.model_dump(exclude_unset=True, exclude={"user_id"})
        result = self.service.update_user(body.user_id, updates)
        if not result["success"]:
            return HttpResponse.error("Update failed")
        return HttpResponse.success(message="User updated")

    async def delete_user(self, user_id: str):
        result = self.service.delete_user(user_id)
        if not result["success"]:
            return HttpResponse.error("Delete failed", 404)
        return HttpResponse.success(message="User deleted")
