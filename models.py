from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class MessageRecord(BaseModel):
    id: Optional[int] = None
    from_number: str
    to_number: str
    body: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CallRecord(BaseModel):
    id: Optional[int] = None
    from_number: str
    to_number: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
