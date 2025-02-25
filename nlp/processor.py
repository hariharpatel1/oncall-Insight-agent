from datetime import datetime, timedelta
from typing import Dict, List
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from contracts.base import DateTimeRange
from contracts.incident import CodeReference, IncidentState, Incident
from nlp.azure.client import azure_openai_client
from nlp.prompts.root_cause import root_cause_prompt
from nlp.prompts.code import code_analysis_prompt
from nlp.prompts.perf import performance_analysis_prompt
from monitoring.system import MonitoringSystem
from contracts.monitoring import LogMessage, Metric, MonitoringQuery, MonitoringData
from memory.store import context_store
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Natural Language Processor for incident analysis"""

    def __init__(self):
        self.monitoring_system = MonitoringSystem()
        self._init_chains()

    def _init_chains(self):
        """Initialize analysis chains with modern LangChain syntax"""
        # Root cause analysis chain
        self.root_cause_chain = (
            root_cause_prompt | 
            azure_openai_client.llm | 
            StrOutputParser()
        )

        # Code analysis chain
        self.code_analysis_chain = (
            code_analysis_prompt | 
            azure_openai_client.llm | 
            StrOutputParser()
        )

        # Performance analysis chain
        self.performance_analysis_chain = (
            performance_analysis_prompt | 
            azure_openai_client.llm | 
            StrOutputParser()
        )

    async def analyze_incident(self, incident: Incident) -> Dict:
        """
        Analyze incident using multiple specialized chains
        
        Args:
            incident: Dictionary containing incident details
            
        Returns:
            Dictionary containing analysis results and metadata
        """
        try:
            logger.info(f"[NLP Processor] Analyzing incident: {incident.id}")

            logger.info(f"[NLP Processor] Retrieving monitoring data for incident: {incident.id}")
            
            # Retrieve monitoring data
            monitoring_data = await self._get_monitoring_data(incident)

            incident_state = context_store.get_context(incident.id)
            if not incident_state:
                logger.info(f"[NLP Processor] Creating new context for incident: {incident.id}")
                incident_state = IncidentState(
                    incident_id=incident.id,
                    incident=incident,
                    analysis_results=None,
                    conversation_history=[],
                    analysis_steps=[],
                    confidence_scores={},
                    last_updated=datetime.utcnow(),
                )
                context_store.save_context(incident_state)

            if not monitoring_data:
                logger.warning(f"[NLP Processor] No monitoring data retrieved for incident: {incident.id}")
            else:
                logger.info(
                    f"[NLP Processor] Retrieved {len(monitoring_data.metrics)} metrics and "
                    f"{len(monitoring_data.logs)} logs for incident: {incident.id}"
                )
            
            # Update incident with monitoring data
            updated_incident = self._update_incident_with_monitoring(incident, monitoring_data)

            logger.info(f"[NLP Processor] Updated incident with monitoring data")
            # Prepare analysis inputs
            analysis_inputs = self._prepare_analysis_inputs(updated_incident, monitoring_data)

            logger.info(f"[NLP Processor] setting updated incident in incident state")
            incident_state.incident = updated_incident
            context_store.save_context(incident_state)
            logger.info(f"[NLP Processor] updated incident in incident state")
            # Run analyses concurrently
            try:
                root_cause_result = await self.root_cause_chain.ainvoke({
                    "incident_details": analysis_inputs["incident_details"],
                    "logs": analysis_inputs["logs"],
                    "code_references": analysis_inputs["code_references"]
                })

                incident_state.add_analysis_step(
                    step_type="root_cause_analysis",
                    input_context={
                        "incident_details": analysis_inputs["incident_details"],
                        "logs_count": len(monitoring_data.logs),
                        "code_refs_count": len(incident.code_references)
                    },
                    output_result={"analysis": root_cause_result},
                    confidence_score=0.8  # You might want to calculate this based on the result
                )

                code_analysis_result = await self.code_analysis_chain.ainvoke({
                    "code_references": analysis_inputs["code_references"]
                })

                incident_state.add_analysis_step(
                    step_type="code_analysis",
                    input_context={
                        "code_refs_count": len(incident.code_references)
                    },
                    output_result={"analysis": code_analysis_result},
                    confidence_score=0.8
                )

                performance_analysis_result = await self.performance_analysis_chain.ainvoke({
                    "incident_details": analysis_inputs["incident_details"],
                    "metrics": analysis_inputs["metrics"],
                    "logs": analysis_inputs["logs"]
                })

                incident_state.add_analysis_step(
                    step_type="performance_analysis",
                    input_context={
                        "metrics_count": len(monitoring_data.metrics),
                        "logs_count": len(monitoring_data.logs)
                    },
                    output_result={"analysis": performance_analysis_result},
                    confidence_score=0.8
                )
                
                # Save updated incident state
                context_store.save_context(incident_state)

                # Store final analysis results
                analysis_results = {
                    "root_cause": root_cause_result,
                    "code_analysis": code_analysis_result,
                    "performance_analysis": performance_analysis_result,
                    "metadata": {
                        "analyzed_at": datetime.now().isoformat(),
                        "monitoring_data_included": bool(monitoring_data.logs or monitoring_data.metrics),
                        "analysis_coverage": self._calculate_analysis_coverage(monitoring_data)
                    }
                }
                
                incident_state.analysis_results = analysis_results
                
                # Add a summary message to conversation history
                incident_state.add_conversation_message(
                    role="system",
                    content="Analysis completed successfully",
                    analysis_type="summary"
                )

                # Save incident state
                context_store.save_context(incident_state)

                return analysis_results

            except Exception as e:
                error_msg = f"[NLP Processor] Error during analysis chains: {str(e)}"
                logger.error(error_msg)

                # Record error in incident state
                incident_state.add_conversation_message(
                    role="system",
                    content=error_msg,
                    analysis_type="error"
                )
                
                failed_results = {
                    "error": str(e),
                    "root_cause": "Analysis failed",
                    "code_analysis": "Analysis failed",
                    "performance_analysis": "Analysis failed"
                }
                
                incident_state.analysis_results = failed_results
                return failed_results
                raise

        except Exception as e:
            error_msg = f"[NLP Processor] Error during incident analysis: {str(e)}"
            logger.error(error_msg)
            
            # Create incident state with error
            incident_state = IncidentState(
                incident_id=incident.id,
                incident=incident
            )
            
            incident_state.add_conversation_message(
                role="system",
                content=error_msg,
                analysis_type="error"
            )
            
            failed_results = {
                "error": str(e),
                "root_cause": "Analysis failed",
                "code_analysis": "Analysis failed",
                "performance_analysis": "Analysis failed"
            }
            
            incident_state.analysis_results = failed_results
            return failed_results


    async def _get_monitoring_data(self, incident: Incident) -> MonitoringData:
        """
        Retrieve monitoring data for the incident
        
        Args:
            incident: Dictionary containing incident details
            
        Returns:
            MonitoringData object containing metrics and logs
        """
        try:
            logger.info(f"[NLP Processor] Getting monitoring data for incident: {incident.id}")

            # Create a time window from incident creation time
            # Default to 1 hour before incident creation
            incident_time = incident.created_at
            if isinstance(incident_time, str):
                incident_time = datetime.fromisoformat(incident_time.replace('Z', '+00:00'))
            
            start_time = incident_time - timedelta(hours=1)
            end_time = incident_time + timedelta(hours=1)
            
            query = MonitoringQuery(
                metric_name="*",
                log_level="error",
                date_range=DateTimeRange(
                    start=start_time,
                    end=end_time
                )
            )

            logger.info(f"[NLP Processor] Monitoring query: {query}")
            return await self.monitoring_system.query_monitoring_data(query)
        except Exception as e:
            logger.error(f"[NLP Processor] Error retrieving monitoring data: {str(e)}")
            return MonitoringData(metrics=[], logs=[])

    def _format_logs(self, logs: List) -> str:
        """Format logs for analysis"""
        return "\n".join(log.message for log in logs) if logs else "No logs available"

    def _format_code_references(self, refs: List) -> str:
        """Format code references for analysis"""
        return "\n".join(ref for ref in refs) if refs else "No code references available"

    def _format_metrics(self, metrics: List) -> str:
        """Format metrics for analysis"""
        return "\n".join(
            f"{metric.name}: {metric.value}" 
            for metric in metrics
        ) if metrics else "No metrics available"
    def _update_incident_with_monitoring(
        self, 
        incident: Incident, 
        monitoring_data: MonitoringData
    ) -> Dict:
        """Update incident dictionary with monitoring data"""
        incident.logs = [
            log.model_dump() for log in monitoring_data.logs
        ] if monitoring_data.logs else []
        incident.metrics = [
            metric.model_dump() for metric in monitoring_data.metrics
        ] if monitoring_data.metrics else []
        return incident

    def _prepare_analysis_inputs(
        self, 
        incident: Incident,
        monitoring_data: MonitoringData
    ) -> Dict:
        """Prepare inputs for analysis chains"""
        return {
            "incident_details": incident.description,
            "logs": self._format_logs(monitoring_data.logs),
            "code_references": self._format_code_references(incident.code_references),
            "metrics": self._format_metrics(monitoring_data.metrics)
        }

    def _format_logs(self, logs: List[LogMessage]) -> str:
        """Format logs for analysis"""
        if not logs:
            return "No logs available"
            
        return "\n".join(
            f"[{log.timestamp}] {log.level}: {log.message}" +
            (f" | {log.attributes}" if log.attributes else "")
            for log in logs
        )

    def _format_code_references(self, refs: List[CodeReference]) -> str:
        """Format code references for analysis"""
        if not refs:
            return "No code references available"
            
        return "\n".join(
            f"File: {ref.file_path}:{ref.line_number} | Function: {ref.function_name}\n" +
            (f"Code:\n{ref.code}\n" if ref.code else "")
            for ref in refs
        )

    def _format_metrics(self, metrics: List[Metric]) -> str:
        """Format metrics for analysis"""
        if not metrics:
            return "No metrics available"
            
        return "\n".join(
            f"{metric.name} = {metric.value}" +
            (f" | Labels: {metric.labels}" if metric.labels else "")
            for metric in metrics
        )

    def _calculate_analysis_coverage(self, monitoring_data: MonitoringData) -> Dict:
        """Calculate coverage metrics for the analysis"""
        return {
            "logs_analyzed": len(monitoring_data.logs),
            "metrics_analyzed": len(monitoring_data.metrics),
            "has_error_logs": any(
                log.level.upper() == "ERROR" 
                for log in monitoring_data.logs
            )
        }