#type: ignore
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


class Metadata(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str = Field(default_factory=lambda: str(uuid4()))

class Message(BaseModel):
    user_id: str
    text: str
    metadata: Optional[Metadata] = None

class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata
    
