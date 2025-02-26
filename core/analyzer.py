from datetime import datetime
from typing import Dict
from nlp.processor import NLPProcessor
from memory.store import context_store
from contracts.incident import Incident, IncidentState

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class IncidentAnalyzer:
    """Core incident analyzer that coordinates analysis and maintains state"""

    def __init__(self):
        self.nlp_processor = NLPProcessor()

    async def analyze_incident(self, incident: Incident):
        """
        Analyze an incident and maintain its state
        
        Args:
            incident: Dictionary containing incident details
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            incident_id = incident.id

            logger.info(f"[Core Analyzer] Analyzing incident: {incident_id}")

            # Initialize or retrieve incident state
            incident_state = self._get_or_create_incident_state(incident)
            
            # Record analysis initiation
            incident_state.add_conversation_message(
                    role="system",
                    content=f"Starting incident analysis at {datetime.utcnow().isoformat()}",
                    analysis_type="system"
            )

            # Perform NLP analysis
            try:
                logger.info(f"[Core Analyzer] Performing NLP analysis for incident: {incident_id}")
                analysis_results = await self.nlp_processor.analyze_incident(incident)
                
                # Handle successful analysis
                if "error" not in analysis_results:
                    logger.info(f"[Core Analyzer] Analysis completed successfully for incident: {incident_id}")
                    self._update_incident_state(incident_state, analysis_results)
                else:
                    logger.error(f"[Core Analyzer] Analysis failed for incident: {incident_id}")
                    incident_state.add_conversation_message(
                        role="system",
                        content=f"Analysis failed: {analysis_results['error']}",
                        analysis_type="error"
                    )

            except Exception as e:
                error_msg = f"Error during NLP analysis: {str(e)}"
                logger.error(f"[Core Analyzer] {error_msg}")
                incident_state.add_conversation_message(
                    role="system",
                    content=error_msg,
                    analysis_type="error"
                )
                analysis_results = {
                    "error": str(e),
                    "root_cause": "Analysis failed",
                    "code_analysis": "Analysis failed",
                    "performance_analysis": "Analysis failed"
                }
            
            logger.info(f"[Core Analyzer] saving incident state for incident: {incident_state.incident}")

            # Save final state
            context_store.save_context(incident_state)
            
            return analysis_results
        except Exception as e:
            error_msg = f"Critical error in incident analysis: {str(e)}"
            logger.error(f"[Core Analyzer] {error_msg}")
            return {
                "error": error_msg,
                "root_cause": "Analysis failed",
                "code_analysis": "Analysis failed",
                "performance_analysis": "Analysis failed"
            }
    
    def _get_or_create_incident_state(self, incident: Incident) -> IncidentState:
        """Get existing incident state or create new one"""
        incident_id = incident.id
        
        # Try to get existing state
        incident_state = context_store.get_context(incident_id)
        
        if not incident_state:
            logger.info(f"[Core Analyzer] Creating new state for incident: {incident_id}")
            incident_state = IncidentState(
                incident_id=incident_id,
                incident=incident,
                last_updated=datetime.utcnow()
            )
            
            # Add initial message
            incident_state.add_conversation_message(
                role="system",
                content="Incident analysis initiated",
                analysis_type="system"
            )
            
            context_store.save_context(incident_state)
        else:
            logger.info(f"[Core Analyzer] Retrieved existing state for incident: {incident_id}")
            
        return incident_state
    
    def _update_incident_state(self, incident_state: IncidentState, analysis_results: Dict):
        """Update incident state with analysis results"""
        # Update analysis results
        incident_state.analysis_results = analysis_results
        
        # Add completion message
        incident_state.add_conversation_message(
            role="system",
            content="Analysis completed successfully",
            analysis_type="system"
        )
        
        # Update metadata
        metadata = analysis_results.get("metadata", {})
        if metadata:
            incident_state.add_analysis_step(
                step_type="analysis_completion",
                input_context={},
                output_result=metadata,
                confidence_score=metadata.get("confidence_score", 0.0)
            )