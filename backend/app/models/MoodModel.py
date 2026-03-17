"""Mood entry data models."""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class MoodScore(int, Enum):
    TERRIBLE = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    GREAT = 5


MOOD_LABELS = {
    1: "Terrible",
    2: "Bad",
    3: "Neutral",
    4: "Good",
    5: "Great"
}


class MoodCreate(BaseModel):
    mood_score: int = Field(..., ge=1, le=5)
    remark: Optional[str] = Field(None, max_length=500)


class MoodUpdate(BaseModel):
    mood_score: Optional[int] = Field(None, ge=1, le=5)
    remark: Optional[str] = Field(None, max_length=500)
