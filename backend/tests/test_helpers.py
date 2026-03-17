"""Tests for helper modules — runs without MongoDB."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set required env vars before importing modules
os.environ.setdefault('APP_NAME', 'Test')
os.environ.setdefault('APP_HOST', '0.0.0.0')
os.environ.setdefault('APP_PORT', '8000')
os.environ.setdefault('APP_ENVIRONMENT', 'test')
os.environ.setdefault('CONNECTION_STRING', 'mongodb://localhost:27017/')
os.environ.setdefault('DATABASE_NAME', 'mood_tracker_test')
os.environ.setdefault('JWT_SECRET', 'test-secret-key')
os.environ.setdefault('ENCRYPTION_KEY', 'test-encryption-key')


def test_password_hash_and_verify():
    """Password hashing should produce verifiable hashes."""
    from app.helpers.PasswordHelper import PasswordHelper

    password = "secureP@ssw0rd!"
    hashed = PasswordHelper.hash_password(password)

    assert "$" in hashed, "Hash should contain salt separator"
    assert PasswordHelper.verify_password(password, hashed) is True
    assert PasswordHelper.verify_password("wrong", hashed) is False


def test_password_unique_salts():
    """Each hash should use a unique salt."""
    from app.helpers.PasswordHelper import PasswordHelper

    h1 = PasswordHelper.hash_password("same")
    h2 = PasswordHelper.hash_password("same")
    assert h1 != h2, "Same password should produce different hashes (different salts)"


def test_jwt_create_and_verify():
    """JWT tokens should round-trip correctly."""
    from app.helpers.JWTHelper import JWTHelper

    payload = {"user_id": "abc123", "email": "test@example.com", "role": "User"}
    token = JWTHelper.create_token(payload)

    assert isinstance(token, str)
    assert token.count(".") == 2, "JWT should have 3 parts"

    decoded = JWTHelper.verify_token(token)
    assert decoded is not None
    assert decoded["user_id"] == "abc123"
    assert decoded["email"] == "test@example.com"
    assert decoded["role"] == "User"
    assert "exp" in decoded
    assert "iat" in decoded


def test_jwt_invalid_token():
    """Invalid tokens should return None."""
    from app.helpers.JWTHelper import JWTHelper

    assert JWTHelper.verify_token("invalid.token.here") is None
    assert JWTHelper.verify_token("") is None
    assert JWTHelper.verify_token("not-a-jwt") is None


def test_jwt_tampered_token():
    """Tampered tokens should fail verification."""
    from app.helpers.JWTHelper import JWTHelper

    token = JWTHelper.create_token({"user_id": "123"})
    parts = token.split(".")
    tampered = parts[0] + "." + parts[1] + ".tampered_signature"
    assert JWTHelper.verify_token(tampered) is None


def test_encryption_round_trip():
    """Encryption should round-trip correctly."""
    from app.helpers.EncryptionHelper import EncryptionHelper

    original = "Feeling great today, had a productive morning!"
    encrypted = EncryptionHelper.encrypt_field(original)

    assert encrypted != original, "Encrypted should differ from original"
    assert isinstance(encrypted, str)

    decrypted = EncryptionHelper.decrypt_field(encrypted)
    assert decrypted == original, "Decrypted should match original"


def test_encryption_none_handling():
    """Encryption should handle None gracefully."""
    from app.helpers.EncryptionHelper import EncryptionHelper

    assert EncryptionHelper.encrypt_field(None) is None
    assert EncryptionHelper.decrypt_field(None) is None
    assert EncryptionHelper.decrypt_field("") is None


def test_encryption_tamper_detection():
    """Tampered encrypted values should fail decryption."""
    from app.helpers.EncryptionHelper import EncryptionHelper

    encrypted = EncryptionHelper.encrypt_field("secret data")
    tampered = encrypted[:-4] + "XXXX"
    assert EncryptionHelper.decrypt_field(tampered) is None


def test_mask_value():
    """Masking should partially hide values."""
    from app.helpers.EncryptionHelper import EncryptionHelper

    assert EncryptionHelper.mask_value(50000) == "******"
    assert EncryptionHelper.mask_value("hello") == "h***o"
    assert EncryptionHelper.mask_value("ab") == "**"
    assert EncryptionHelper.mask_value(None) is None


def test_sentiment_analysis():
    """Sentiment analysis should classify text correctly."""
    from app.helpers.SentimentHelper import SentimentHelper

    positive = SentimentHelper.analyze("I am so happy and excited today!")
    assert positive["sentiment_label"] == "Positive"
    assert positive["sentiment_score"] > 0

    negative = SentimentHelper.analyze("I feel terrible and sad.")
    assert negative["sentiment_label"] == "Negative"
    assert negative["sentiment_score"] < 0

    neutral = SentimentHelper.analyze("I went to the store.")
    assert neutral["sentiment_label"] == "Neutral"


def test_sentiment_empty_input():
    """Sentiment should handle empty/None input."""
    from app.helpers.SentimentHelper import SentimentHelper

    result = SentimentHelper.analyze("")
    assert result["sentiment_score"] == 0.0
    assert result["sentiment_label"] == "Neutral"

    result = SentimentHelper.analyze(None)
    assert result["sentiment_score"] == 0.0


def test_pagination_helper():
    """Pagination should calculate correctly."""
    from app.helpers.PaginationHelper import PaginationHelper

    p = PaginationHelper.get_pagination(page=1, limit=10, total_count=95)
    assert p["page"] == 1
    assert p["limit"] == 10
    assert p["total_count"] == 95
    assert p["total_pages"] == 10
    assert p["has_next"] is True
    assert p["has_prev"] is False

    p = PaginationHelper.get_pagination(page=10, limit=10, total_count=95)
    assert p["has_next"] is False
    assert p["has_prev"] is True

    assert PaginationHelper.get_skip(1, 10) == 0
    assert PaginationHelper.get_skip(3, 10) == 20


def test_http_response_format():
    """HTTP responses should have consistent format."""
    from app.helpers.HttpResponse import HttpResponse

    success = HttpResponse.success(data={"key": "value"}, message="OK")
    assert success.status_code == 200

    error = HttpResponse.error(message="Not found", status_code=404)
    assert error.status_code == 404


def test_mood_model_validation():
    """Mood models should validate input correctly."""
    from app.models.MoodModel import MoodCreate, MoodUpdate, MOOD_LABELS
    from pydantic import ValidationError

    # Valid mood
    mood = MoodCreate(mood_score=4, remark="Good day")
    assert mood.mood_score == 4

    # Invalid score
    try:
        MoodCreate(mood_score=6)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass

    try:
        MoodCreate(mood_score=0)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass

    # Labels
    assert MOOD_LABELS[1] == "Terrible"
    assert MOOD_LABELS[5] == "Great"

    # Update with optional fields
    update = MoodUpdate(mood_score=3)
    assert update.mood_score == 3
    assert update.remark is None


def test_user_model_validation():
    """User models should validate input correctly."""
    from app.models.UserModel import UserCreate, UserRole
    from pydantic import ValidationError

    # Valid user
    user = UserCreate(email="test@example.com", full_name="Test User", password="securepass")
    assert user.email == "test@example.com"

    # Short password
    try:
        UserCreate(email="test@example.com", full_name="Test", password="short")
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass

    # Invalid email
    try:
        UserCreate(email="not-an-email", full_name="Test", password="securepass")
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass

    # Roles
    assert UserRole.ADMIN.value == "Admin"
    assert UserRole.USER.value == "User"
