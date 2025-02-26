from typing import Dict, Optional
from datetime import datetime
from contracts.monitoring import LogMessage, Metric
from core.analyzer import IncidentAnalyzer
from memory.store import context_store
from contracts.incident import (
    CodeReference,
    Incident,
    IncidentState,
    EnvironmentContext,
    IncidentStatus
)
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class IncidentManager:
    """Manager for handling incident lifecycle and coordination"""
    def __init__(self):
        self.analyzer = IncidentAnalyzer()

    async def create_incident(self, incident_data: Incident) -> str:
        """
        Create a new incident with proper context structure
        
        Args:
            incident_data: Dictionary containing incident details
            
        Returns:
            str: Incident ID
        """
        try:
            # First create the environment context
            env_context = EnvironmentContext(
                application=incident_data.context.application,
                environment=incident_data.context.environment,
                component=incident_data.context.component
            )

            # Process any existing logs
            logs = [
                LogMessage(**log) if isinstance(log, dict) else log 
                for log in incident_data.logs
            ]

            # Process any existing metrics
            metrics = [
                Metric(**metric) if isinstance(metric, dict) else metric 
                for metric in incident_data.metrics
            ]

            # Process any existing code references
            code_refs = [
                CodeReference(**ref) if isinstance(ref, dict) else ref 
                for ref in incident_data.code_references
            ]

            # Create incident
            incident = Incident(
                id=incident_data.id,
                title=incident_data.title,
                description=incident_data.description,
                severity=incident_data.severity,
                status=incident_data.status,
                context=env_context,
                logs=logs,
                metrics=metrics,
                code_references=code_refs,
                created_at=incident_data.created_at,
                updated_at=incident_data.updated_at
            )

            logger.info(f"[Incident Manager] Creating incident state: {incident.id}")

            # Create the incident state
            state = IncidentState(
                incident_id=incident.id,
                incident=incident,
                analysis_results=None,
                conversation_history=[],
                analysis_steps=[],
                confidence_scores={},
                last_updated=datetime.utcnow(),
            )

            # Add initial system message
            state.add_conversation_message(
                role="system",
                content="Incident created",
                analysis_type="system"
            )

            logger.info(f"[Incident Manager] Saving incident state: {state}")

            # Store the state
            context_store.save_context(state)
            
            return incident.id
            
        except Exception as e:
            error_msg = f"Failed to create incident: {str(e)}"
            logger.error(f"[Incident Manager] {error_msg}")
            raise ValueError(error_msg)


    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        """
        Retrieve incident by ID
        
        Args:
            incident_id: ID of the incident to retrieve
            
        Returns:
            Optional[Dict]: Incident data if found, None otherwise
        """
        state = context_store.get_context(incident_id)
        if state:
            return state.incident
        return None

    async def update_incident(self, incident_id: str, updates: Dict) -> None:
        """
        Update incident with validation
        
        Args:
            incident_id: ID of the incident to update
            updates: Dictionary containing update data
        """
        state = context_store.get_context(incident_id)
        if not state:
            raise ValueError(f"Incident {incident_id} not found")
            
        try:
            # Update incident data
            incident_data = state.incident.model_dump()
            incident_data.update(updates)
            
            # Create new incident with updates
            updated_incident = Incident(**incident_data)
            updated_incident.updated_at = datetime.utcnow()

            # Update state
            state.incident = updated_incident
            state.last_updated = datetime.utcnow()

            # Add update message
            state.add_conversation_message(
                role="system",
                content=f"Incident updated: {', '.join(updates.keys())}",
                analysis_type="update"
            )
            
            # Save updated state
            context_store.save_context(state)
            
        except Exception as e:
            error_msg = f"Failed to update incident: {str(e)}"
            logger.error(f"[Incident Manager] {error_msg}")
            raise ValueError(error_msg)

    async def resolve_incident(self, incident_id: str) -> None:
        """
        Mark incident as resolved
        
        Args:
            incident_id: ID of the incident to resolve
        """
        try:
            await self.update_incident(
                incident_id,
                {'status': IncidentStatus.RESOLVED}
            )
            
            # Get state to add resolution message
            state = context_store.get_context(incident_id)
            if state:
                state.add_conversation_message(
                    role="system",
                    content="Incident marked as resolved",
                    analysis_type="status_change"
                )
                context_store.save_context(state)
                
        except Exception as e:
            error_msg = f"Failed to resolve incident: {str(e)}"
            logger.error(f"[Incident Manager] {error_msg}")
            raise ValueError(error_msg)

    async def analyze_incident(
        self,
        incident_id: str,
        follow_up_query: Optional[str] = None
    ) -> Dict:
        """
        Analyze incident and store results
        
        Args:
            incident_id: ID of the incident to analyze
            follow_up_query: Optional follow-up query for analysis
            
        Returns:
            Dict: Analysis results
        """

        logger.info(f"[Incident Manager] Analyzing incident: {incident_id}")
        state = context_store.get_context(incident_id)
        if not state:
            raise ValueError(f"Incident {incident_id} not found")
            
        try:
           # Prepare incident data for analysis
            incident_data = state.incident
            
            logger.info(f"[Incident Manager] Incident data for analysis: {incident_data.model_dump()}")

            # Add analysis start message
            state.add_conversation_message(
                role="system",
                content=f"Starting incident analysis{' with follow-up query' if follow_up_query else ''}",
                analysis_type="analysis_start"
            )

            # Perform analysis
            analysis_results = await self.analyzer.analyze_incident(
                incident_data
            )
            
            logger.info(f"[Incident Manager] Analysis results: {analysis_results}")
            
            state.add_analysis_step(
                step_type="full_analysis",
                input_context={"query": follow_up_query} if follow_up_query else {},
                output_result=analysis_results,
                confidence_score=0.8
            )
            
            # Analysis results are already stored by the analyzer
            # Just return them here
            return analysis_results
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(f"[Incident Manager] {error_msg}")
            
            # Add error message to state
            if state:
                state.add_conversation_message(
                    role="system",
                    content=error_msg,
                    analysis_type="error"
                )
                context_store.save_context(state)
                
            raise ValueError(error_msg)

    async def add_log(
        self,
        incident_id: str,
        level: str,
        message: str
    ) -> None:
        """Add a log entry to the incident"""
        state = context_store.get_context(incident_id)
        if not state:
            raise ValueError(f"Incident {incident_id} not found")
            
        new_log = {
            'timestamp': datetime.utcnow(),
            'level': level,
            'message': message
        }
        
        state.incident.logs.append(new_log)
        state.last_updated = datetime.utcnow()
        context_store.save_context(state)