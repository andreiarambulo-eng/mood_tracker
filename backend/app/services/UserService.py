"""User business logic service."""
import uuid
from datetime import datetime
from modules.database.DatabaseManager import DatabaseManager
from app.helpers.JWTHelper import JWTHelper
from app.helpers.PasswordHelper import PasswordHelper


class UserService:
    """Handles user CRUD and authentication."""

    def __init__(self):
        self.users = DatabaseManager.get_collection("users")

    def register(self, email: str, full_name: str, password: str, role: str = "User") -> dict:
        """Register a new user."""
        existing = self.users.find_one({"email": email})
        if existing:
            return {"success": False, "message": "Email already registered"}

        password_hash = PasswordHelper.hash_password(password)
        now = datetime.utcnow().isoformat()
        user_id = str(uuid.uuid4())

        self.users.insert_one({
            "_id": user_id,
            "email": email,
            "full_name": full_name,
            "password_hash": password_hash,
            "role": role,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "last_login": None
        })

        return {
            "success": True,
            "message": "User registered successfully",
            "data": {"user_id": user_id}
        }

    def login(self, email: str, password: str) -> dict:
        """Authenticate user and return JWT token."""
        user = self.users.find_one({"email": email})

        if not user:
            return {"success": False, "message": "Invalid credentials"}

        if not user["is_active"]:
            return {"success": False, "message": "Account is deactivated"}

        if not PasswordHelper.verify_password(password, user["password_hash"]):
            return {"success": False, "message": "Invalid credentials"}

        token = JWTHelper.create_token({
            "user_id": user["_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        })

        self.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow().isoformat()}}
        )

        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "token": token,
                "user": {
                    "user_id": user["_id"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "role": user["role"]
                }
            }
        }

    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return user data.

        Stateless verification: trusts the signed JWT payload without a DB
        lookup for performance on serverless.
        """
        payload = JWTHelper.verify_token(token)
        if not payload:
            return None

        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "full_name": payload.get("full_name", ""),
            "role": payload.get("role", "User")
        }

    def get_all_users(self, page: int = 1, limit: int = 10) -> dict:
        """Get all users (admin only)."""
        skip = (page - 1) * limit
        total = self.users.count_documents({})
        cursor = self.users.find(
            {},
            {"password_hash": 0}
        ).sort("created_at", -1).skip(skip).limit(limit)

        users = []
        for u in cursor:
            users.append({
                "_id": u["_id"],
                "user_id": u["_id"],
                "email": u["email"],
                "full_name": u["full_name"],
                "role": u["role"],
                "is_active": u["is_active"],
                "created_at": u.get("created_at"),
                "updated_at": u.get("updated_at"),
                "last_login": u.get("last_login")
            })
        return {"data": users, "total_count": total}

    def get_user_by_id(self, user_id: str) -> dict:
        """Get a single user."""
        user = self.users.find_one({"_id": user_id}, {"password_hash": 0})
        if not user:
            return None
        return {
            "_id": user["_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "is_active": user["is_active"],
            "created_at": user.get("created_at"),
            "updated_at": user.get("updated_at"),
            "last_login": user.get("last_login")
        }

    def update_user(self, user_id: str, updates: dict) -> dict:
        """Update user fields."""
        updates["updated_at"] = datetime.utcnow().isoformat()
        result = self.users.update_one({"_id": user_id}, {"$set": updates})
        return {"success": result.modified_count > 0}

    def delete_user(self, user_id: str) -> dict:
        """Delete a user."""
        result = self.users.delete_one({"_id": user_id})
        return {"success": result.deleted_count > 0}

    def change_password(self, user_id: str, current_password: str, new_password: str) -> dict:
        """Change user password."""
        user = self.users.find_one({"_id": user_id})
        if not user:
            return {"success": False, "message": "User not found"}

        if not PasswordHelper.verify_password(current_password, user["password_hash"]):
            return {"success": False, "message": "Current password is incorrect"}

        new_hash = PasswordHelper.hash_password(new_password)
        self.users.update_one(
            {"_id": user_id},
            {"$set": {"password_hash": new_hash, "updated_at": datetime.utcnow().isoformat()}}
        )
        return {"success": True, "message": "Password changed successfully"}
