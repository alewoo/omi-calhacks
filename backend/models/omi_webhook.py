"""Pydantic models for Omi webhook payloads"""
from pydantic import BaseModel, Field
from typing import List, Optional


class TranscriptSegment(BaseModel):
    """Individual segment of conversation transcript"""
    text: str
    speaker: str
    speaker_id: int
    is_user: bool
    start: float  # timestamp in seconds
    end: float


class RealtimeWebhook(BaseModel):
    """Real-time transcript webhook from Omi device"""
    session_id: str
    segments: List[TranscriptSegment]

    def get_user_text(self) -> str:
        """Extract all user speech as single string"""
        return " ".join([s.text for s in self.segments if s.is_user])


class Memory(BaseModel):
    """Memory structure from Omi"""
    id: str
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    transcript: str = ""
    transcript_segments: List[TranscriptSegment] = []
    photos: List[str] = []
    structured: dict = {}


class MemoryCreated(BaseModel):
    """Memory creation webhook from Omi"""
    uid: str  # user ID
    memory: Memory
