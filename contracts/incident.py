from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional
from datetime import datetime

from contracts.monitoring import Metric

from .base import Severity, IncidentStatus


class DebugLog(BaseModel):
    timestamp: datetime
    level: str
    message: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    def __init__(self, **data):
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        super().__init__(**data)

class CodeReference(BaseModel):
    file_path: str
    line_number: int
    function_name: str
    code: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )

class EnvironmentContext(BaseModel):
    """Environment-specific context"""
    application: str
    environment: str
    component: str

    model_config = ConfigDict(from_attributes=True)

class Incident(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity
    status: IncidentStatus
    context: EnvironmentContext
    logs: List[DebugLog]
    code_references: List[CodeReference]
    metrics: List[Metric]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    def __init__(self, **data):
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        super().__init__(**data)

    def add_log(self, level: str, message: str):
        """Add a new debug log entry"""
        log = DebugLog(
            timestamp=datetime.now(),
            level=level,
            message=message
        )
        self.logs.append(log)
        self.updated_at = datetime.now()

    def add_code_reference(self, file_path: str, line_number: int, function_name: str, code: Optional[str] = None):
        """Add a new code reference"""
        ref = CodeReference(
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            code=code
        )
        self.code_references.append(ref)
        self.updated_at = datetime.now()

class RootCauseAnalysis(BaseModel):
    incident_id: str
    probable_cause: str
    contributing_factors: List[str]
    confidence_score: float

    model_config = ConfigDict(
        from_attributes=True
    )

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence_score >= 0.8

class PerformanceAnalysis(BaseModel):
    incident_id: str
    bottlenecks: List[str]
    optimization_suggestions: List[str]

    model_config = ConfigDict(
        from_attributes=True
    )

    def get_prioritized_suggestions(self) -> List[str]:
        """Return optimization suggestions in priority order"""
        # In a real implementation, this would use some logic to prioritize
        return sorted(self.optimization_suggestions, 
                     key=lambda x: len(x),  # Simple example ordering
                     reverse=True)

class IncidentState(BaseModel):
    """Incident state and analysis information"""
    incident_id: str
    incident: Incident
    analysis_results: Optional[Dict] = None
    conversation_history: List[Dict] = []
    analysis_steps: List[Dict] = []
    confidence_scores: Dict[str, float] = {}
    last_updated: datetime = datetime.utcnow()

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    def add_conversation_message(self, role: str, content: str, 
                               analysis_type: Optional[str] = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
            "analysis_type": analysis_type
        }
        self.conversation_history.append(message)
        self.last_updated = datetime.utcnow()

    def add_analysis_step(self, step_type: str, input_context: Dict, 
                         output_result: Dict, confidence_score: float):
        step = {
            "step_type": step_type,
            "timestamp": datetime.utcnow(),
            "input_context": input_context,
            "output_result": output_result,
            "confidence_score": confidence_score
        }
        self.analysis_steps.append(step)
        self.last_updated = datetime.utcnow()
