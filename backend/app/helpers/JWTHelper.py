"""JWT token generation and validation utilities."""
import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from decouple import config


class JWTHelper:
    """Helper class for JWT token operations."""

    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        """Encode bytes to base64url string."""
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    @staticmethod
    def _base64url_decode(data: str) -> bytes:
        """Decode base64url string to bytes."""
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def create_token(
        payload: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT token.

        Args:
            payload: Token payload data
            expires_delta: Token expiration time (default: 24 hours)

        Returns:
            JWT token string
        """
        secret = config('JWT_SECRET', default='your-secret-key-change-this')

        if expires_delta is None:
            expires_delta = timedelta(hours=24)

        expire = datetime.utcnow() + expires_delta

        token_payload = payload.copy()
        token_payload.update({
            "exp": int(expire.timestamp()),
            "iat": int(datetime.utcnow().timestamp())
        })

        header = {
            "alg": "HS256",
            "typ": "JWT"
        }

        header_encoded = JWTHelper._base64url_encode(
            json.dumps(header, separators=(',', ':')).encode()
        )
        payload_encoded = JWTHelper._base64url_encode(
            json.dumps(token_payload, separators=(',', ':')).encode()
        )

        message = f"{header_encoded}.{payload_encoded}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        signature_encoded = JWTHelper._base64url_encode(signature)

        return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            secret = config('JWT_SECRET', default='your-secret-key-change-this')

            parts = token.split('.')
            if len(parts) != 3:
                return None

            header_encoded, payload_encoded, signature_encoded = parts

            message = f"{header_encoded}.{payload_encoded}"
            expected_signature = hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            expected_signature_encoded = JWTHelper._base64url_encode(
                expected_signature
            )

            if signature_encoded != expected_signature_encoded:
                return None

            payload_json = JWTHelper._base64url_decode(payload_encoded)
            payload = json.loads(payload_json)

            if 'exp' in payload:
                exp_timestamp = payload['exp']
                if datetime.utcnow().timestamp() > exp_timestamp:
                    return None

            return payload

        except Exception:
            return None

    @staticmethod
    def decode_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
        """Decode token without verification (for debugging)."""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None

            payload_json = JWTHelper._base64url_decode(parts[1])
            return json.loads(payload_json)
        except Exception:
            return None
