"""Password hashing and verification utilities."""
import hashlib
import secrets


class PasswordHelper:
    """Helper class for password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256 with salt.

        Args:
            password: Plain text password

        Returns:
            Hashed password in format: salt$hash
        """
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${pwd_hash}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            password: Plain text password to verify
            hashed_password: Stored hash in format: salt$hash

        Returns:
            True if password matches, False otherwise
        """
        try:
            salt, stored_hash = hashed_password.split('$')
            pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            return pwd_hash == stored_hash
        except (ValueError, AttributeError):
            return False
