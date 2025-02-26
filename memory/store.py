from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

from contracts.incident import IncidentState
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class ContextStore:
    def __init__(self):
        self.store: Dict[str, IncidentState] = {}

    def save_context(self, state: IncidentState) -> None:
        """Save incident state"""
        logger.info(f"[Store] Saving incident state: {state}")
        self.store[state.incident_id] = state

    def get_context(self, incident_id: str) -> Optional[IncidentState]:
        """Get incident state by ID"""
        return self.store.get(incident_id)

    def list_incidents(self) -> List[str]:
        """Get list of all incident IDs"""
        return list(self.store.keys())

    def cleanup_old_incidents(self, max_age_days: int = 30) -> None:
        """Remove old incidents"""
        current_time = datetime.utcnow()
        to_remove = []
        
        for incident_id, state in self.store.items():
            if (current_time - state.last_updated).days > max_age_days:
                to_remove.append(incident_id)
                
        for incident_id in to_remove:
            del self.store[incident_id]

# Create singleton instance
context_store = ContextStore()