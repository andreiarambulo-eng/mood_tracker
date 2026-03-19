"""User business logic service."""
import uuid
from datetime import datetime
from modules.database.DatabaseManager import DatabaseManager
from app.helpers.JWTHelper import JWTHelper
from app.helpers.PasswordHelper import PasswordHelper


class UserService:
    """Handles user CRUD and authentication."""

    def __init__(self):
        self.db = DatabaseManager()

    def register(self, email: str, full_name: str, password: str, role: str = "User") -> dict:
        """Register a new user."""
        existing = self.db.fetchone("SELECT id FROM users WHERE email = ?", (email,))
        if existing:
            return {"success": False, "message": "Email already registered"}

        password_hash = PasswordHelper.hash_password(password)
        now = datetime.utcnow().isoformat()
        user_id = str(uuid.uuid4())

        self.db.execute_and_commit(
            "INSERT INTO users (id, email, full_name, password_hash, role, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 1, ?, ?)",
            (user_id, email, full_name, password_hash, role, now, now)
        )

        return {
            "success": True,
            "message": "User registered successfully",
            "data": {"user_id": user_id}
        }

    def login(self, email: str, password: str) -> dict:
        """Authenticate user and return JWT token."""
        user = self.db.fetchone("SELECT * FROM users WHERE email = ?", (email,))

        if not user:
            return {"success": False, "message": "Invalid credentials"}

        if not user["is_active"]:
            return {"success": False, "message": "Account is deactivated"}

        if not PasswordHelper.verify_password(password, user["password_hash"]):
            return {"success": False, "message": "Invalid credentials"}

        token = JWTHelper.create_token({
            "user_id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        })

        self.db.execute_and_commit(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), user["id"])
        )

        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "token": token,
                "user": {
                    "user_id": user["id"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "role": user["role"]
                }
            }
        }

    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return user data.

        Stateless verification: trusts the signed JWT payload without a DB
        lookup. This is required for Vercel serverless where each function
        invocation may have a fresh ephemeral SQLite DB in /tmp.
        """
        payload = JWTHelper.verify_token(token)
        if not payload:
            return None

        # Return user info directly from the JWT payload (stateless)
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "full_name": payload.get("full_name", ""),
            "role": payload.get("role", "User")
        }

    def get_all_users(self, page: int = 1, limit: int = 10) -> dict:
        """Get all users (admin only)."""
        skip = (page - 1) * limit
        total = self.db.fetchone("SELECT COUNT(*) as cnt FROM users")["cnt"]
        rows = self.db.fetchall(
            "SELECT id, email, full_name, role, is_active, created_at, updated_at, last_login FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, skip)
        )

        users = [{"_id": r["id"], **{k: r[k] for k in r.keys() if k != "id"}} for r in rows]
        return {"data": users, "total_count": total}

    def get_user_by_id(self, user_id: str) -> dict:
        """Get a single user."""
        user = self.db.fetchone(
            "SELECT id, email, full_name, role, is_active, created_at, updated_at, last_login FROM users WHERE id = ?",
            (user_id,)
        )
        if not user:
            return None
        return {"_id": user["id"], **{k: user[k] for k in user.keys() if k != "id"}}

    def update_user(self, user_id: str, updates: dict) -> dict:
        """Update user fields."""
        updates["updated_at"] = datetime.utcnow().isoformat()
        set_clauses = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [user_id]
        cursor = self.db.execute_and_commit(
            f"UPDATE users SET {set_clauses} WHERE id = ?", tuple(values)
        )
        return {"success": cursor.rowcount > 0}

    def delete_user(self, user_id: str) -> dict:
        """Delete a user."""
        cursor = self.db.execute_and_commit("DELETE FROM users WHERE id = ?", (user_id,))
        return {"success": cursor.rowcount > 0}

    def change_password(self, user_id: str, current_password: str, new_password: str) -> dict:
        """Change user password."""
        user = self.db.fetchone("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        if not user:
            return {"success": False, "message": "User not found"}

        if not PasswordHelper.verify_password(current_password, user["password_hash"]):
            return {"success": False, "message": "Current password is incorrect"}

        new_hash = PasswordHelper.hash_password(new_password)
        self.db.execute_and_commit(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (new_hash, datetime.utcnow().isoformat(), user_id)
        )
        return {"success": True, "message": "Password changed successfully"}
