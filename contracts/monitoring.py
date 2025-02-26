from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict
from enum import Enum

from .base import DateTimeRange

class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class Metric(BaseModel):
    name: str
    value: float
    timestamp: datetime
    type: MetricType
    labels: Optional[Dict[str, str]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    def __init__(self, **data):
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        super().__init__(**data)

class LogMessage(BaseModel):
    timestamp: datetime
    level: str  
    message: str
    attributes: Optional[Dict[str, str]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    def __init__(self, **data):
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        super().__init__(**data)

class MonitoringQuery(BaseModel):
    metric_name: Optional[str] = None 
    log_level: Optional[str] = None
    date_range: DateTimeRange

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )


class MonitoringData(BaseModel):
    metrics: List[Metric]
    logs: List[LogMessage]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    def get_metrics_in_timeframe(self, start: datetime, end: datetime) -> List[Metric]:
        """Filter metrics within a specific timeframe"""
        return [
            metric for metric in self.metrics 
            if start <= metric.timestamp <= end
        ]

    def get_logs_in_timeframe(self, start: datetime, end: datetime) -> List[LogMessage]:
        """Filter logs within a specific timeframe"""
        return [
            log for log in self.logs 
            if start <= log.timestamp <= end
        ]

    def get_logs_by_level(self, level: str) -> List[LogMessage]:
        """Filter logs by level"""
        return [
            log for log in self.logs 
            if log.level.upper() == level.upper()
        ]