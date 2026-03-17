"""Encryption and data masking utilities for sensitive fields."""
import hashlib
import hmac
import base64
from typing import Any, Optional
from decouple import config


class EncryptionHelper:
    """Helper class for encrypting and masking sensitive data."""

    @staticmethod
    def _get_encryption_key() -> str:
        """Get encryption key from environment."""
        return config('ENCRYPTION_KEY', default=config('JWT_SECRET', default='your-secret-key-change-this'))

    @staticmethod
    def encrypt_field(value: Any) -> str:
        """
        Encrypt a field value using HMAC-SHA256.

        Args:
            value: Value to encrypt

        Returns:
            Encrypted value as base64 string
        """
        if value is None:
            return None

        key = EncryptionHelper._get_encryption_key()
        value_str = str(value)

        signature = hmac.new(
            key.encode(),
            value_str.encode(),
            hashlib.sha256
        ).digest()

        combined = value_str.encode() + b'::' + signature
        encrypted = base64.b64encode(combined).decode('utf-8')
        return encrypted

    @staticmethod
    def decrypt_field(encrypted_value: str) -> Optional[Any]:
        """
        Decrypt a field value.

        Args:
            encrypted_value: Encrypted base64 string

        Returns:
            Decrypted value or None if invalid
        """
        if not encrypted_value:
            return None

        try:
            key = EncryptionHelper._get_encryption_key()

            combined = base64.b64decode(encrypted_value)
            parts = combined.split(b'::')
            if len(parts) != 2:
                return None

            value_bytes, signature = parts
            value_str = value_bytes.decode('utf-8')

            expected_signature = hmac.new(
                key.encode(),
                value_str.encode(),
                hashlib.sha256
            ).digest()

            if signature != expected_signature:
                return None

            return value_str

        except Exception:
            return None

    @staticmethod
    def mask_value(value: Any, mask_char: str = '*') -> str:
        """Mask a sensitive value."""
        if value is None:
            return None

        value_str = str(value)

        if isinstance(value, (int, float)):
            return f"{mask_char * 6}"

        if len(value_str) <= 2:
            return mask_char * len(value_str)

        return value_str[0] + (mask_char * (len(value_str) - 2)) + value_str[-1]
