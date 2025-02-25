import streamlit as st
from contracts.incident import Incident
from ui.components.tabs.analysis_tab import display_analysis_tab
from ui.components.tabs.metrics_tab import display_metrics_tab
from ui.components.tabs.context_tab import display_context_tab
from ui.components.tabs.logs_tab import display_logs_tab
from ui.components.tabs.code_tab import display_code_tab
from ui.components.tabs.history_tab import display_history_tab
from ui.components.tabs.actions_tab import display_actions_tab
from memory.store import context_store
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def display_incident_tabs(incident: Incident, manager):
    """Display all incident tabs with state management"""
    if isinstance(incident, dict):
        incident = Incident(**incident)

    # Get the latest incident state from context store
    incident_state = context_store.get_context(incident.id)

    if not incident_state:
        st.error("No incident state found")
        return
    
    # Use incident data from the state
    current_incident = incident_state.incident

    # logger.info(f"Current incident data: {current_incident}")

    # Create tabs
    tab_titles = ["Analysis", "Metrics", "Context", "Logs", "Code", "History", "Actions"]
    tabs = st.tabs(tab_titles)

    # Handle tab content based on current state
    with tabs[0]:
            display_analysis_tab(incident_state, manager)
    with tabs[1]:
            display_metrics_tab(current_incident)
    with tabs[2]:
            display_context_tab(current_incident)
    with tabs[3]:
            display_logs_tab(current_incident)
    with tabs[4]:
            display_code_tab(current_incident)
    with tabs[5]:
            display_history_tab(incident_state)
    with tabs[6]:
            display_actions_tab(current_incident, manager)