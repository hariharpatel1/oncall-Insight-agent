from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class DateTimeRange(BaseModel):
    start: datetime
    end: datetime

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    def __init__(self, **data):
        super().__init__(**data)
        if isinstance(self.start, str):
            self.start = datetime.fromisoformat(self.start.replace('Z', '+00:00'))
        if isinstance(self.end, str):
            self.end = datetime.fromisoformat(self.end.replace('Z', '+00:00'))

    def validate_range(self) -> bool:
        """Validate that end datetime is after start datetime"""
        return self.end > self.start
