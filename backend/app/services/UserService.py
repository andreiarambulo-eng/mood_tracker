"""User business logic service."""
from datetime import datetime
from bson import ObjectId
from modules.mongodb.MongoDBManager import MongoDBManager
from app.helpers.JWTHelper import JWTHelper
from app.helpers.PasswordHelper import PasswordHelper


class UserService:
    """Handles user CRUD and authentication."""

    def __init__(self):
        self.collection = MongoDBManager.get_collection('users')

    def register(self, email: str, full_name: str, password: str, role: str = "User") -> dict:
        """Register a new user."""
        if self.collection.find_one({"email": email}):
            return {"success": False, "message": "Email already registered"}

        password_hash = PasswordHelper.hash_password(password)
        now = datetime.utcnow()

        user_doc = {
            "email": email,
            "full_name": full_name,
            "password_hash": password_hash,
            "role": role,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "last_login": None
        }

        result = self.collection.insert_one(user_doc)
        return {
            "success": True,
            "message": "User registered successfully",
            "data": {"user_id": str(result.inserted_id)}
        }

    def login(self, email: str, password: str) -> dict:
        """Authenticate user and return JWT token."""
        user = self.collection.find_one({"email": email})

        if not user:
            return {"success": False, "message": "Invalid credentials"}

        if not user.get("is_active", True):
            return {"success": False, "message": "Account is deactivated"}

        if not PasswordHelper.verify_password(password, user["password_hash"]):
            return {"success": False, "message": "Invalid credentials"}

        token = JWTHelper.create_token({
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"]
        })

        self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "token": token,
                "user": {
                    "user_id": str(user["_id"]),
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "role": user["role"]
                }
            }
        }

    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return user data."""
        payload = JWTHelper.verify_token(token)
        if not payload:
            return None

        user = self.collection.find_one({"_id": ObjectId(payload["user_id"])})
        if not user or not user.get("is_active", True):
            return None

        return {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }

    def get_all_users(self, page: int = 1, limit: int = 10) -> dict:
        """Get all users (admin only)."""
        skip = (page - 1) * limit
        total = self.collection.count_documents({})
        cursor = self.collection.find({}, {"password_hash": 0}).skip(skip).limit(limit).sort("created_at", -1)

        users = []
        for u in cursor:
            u["_id"] = str(u["_id"])
            if u.get("created_at"):
                u["created_at"] = u["created_at"].isoformat()
            if u.get("updated_at"):
                u["updated_at"] = u["updated_at"].isoformat()
            if u.get("last_login"):
                u["last_login"] = u["last_login"].isoformat()
            users.append(u)

        return {"data": users, "total_count": total}

    def get_user_by_id(self, user_id: str) -> dict:
        """Get a single user."""
        user = self.collection.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
        if not user:
            return None
        user["_id"] = str(user["_id"])
        if user.get("created_at"):
            user["created_at"] = user["created_at"].isoformat()
        if user.get("updated_at"):
            user["updated_at"] = user["updated_at"].isoformat()
        if user.get("last_login"):
            user["last_login"] = user["last_login"].isoformat()
        return user

    def update_user(self, user_id: str, updates: dict) -> dict:
        """Update user fields."""
        updates["updated_at"] = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updates}
        )
        return {"success": result.modified_count > 0}

    def delete_user(self, user_id: str) -> dict:
        """Delete a user."""
        result = self.collection.delete_one({"_id": ObjectId(user_id)})
        return {"success": result.deleted_count > 0}

    def change_password(self, user_id: str, current_password: str, new_password: str) -> dict:
        """Change user password."""
        user = self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"success": False, "message": "User not found"}

        if not PasswordHelper.verify_password(current_password, user["password_hash"]):
            return {"success": False, "message": "Current password is incorrect"}

        new_hash = PasswordHelper.hash_password(new_password)
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": new_hash, "updated_at": datetime.utcnow()}}
        )
        return {"success": True, "message": "Password changed successfully"}
