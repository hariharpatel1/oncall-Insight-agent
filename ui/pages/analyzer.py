import streamlit as st
import asyncio
from core.manager import IncidentManager
from contracts.base import Severity
import logging

from ui.components.incident_details import display_incident_details
from ui.components.incident_form import display_incident_form
from ui.components.incident_tabs import display_incident_tabs

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

@st.cache_resource
def get_incident_manager():
    return IncidentManager()

def analyzer_page():
    st.markdown("# Incident Analyzer")

     # Initialize the manager
    manager = IncidentManager()

    # Display incident creation form in sidebar
    display_incident_form(manager)

    # Main content area
    incident_id = st.text_input("Enter Incident ID")

    if incident_id:
        try:
            with st.spinner("Loading incident..."):
                incident = asyncio.run(manager.get_incident(incident_id))
                if incident:
                    # Display incident overview
                    display_incident_details(incident)
                    
                    # Display incident tabs
                    display_incident_tabs(incident, manager)
                else:
                    st.error("Incident not found")
        except Exception as e:
            st.error(f"Error retrieving incident: {str(e)}")


#     if incident_id:
#         try:
#             with st.spinner("Loading incident..."):
#                 incident = asyncio.run(manager.get_incident(incident_id))
#                 if incident:
#                     # Update session state
#                     st.session_state.incident_data = incident
#                     display_incident(incident, manager)
#                 else:
#                     st.error("Incident not found")
#         except Exception as e:
#             st.error(f"Error retrieving incident: {str(e)}")

# def handle_incident_creation(manager):
#     """Handle incident creation with validation"""
#     with st.sidebar:
#         with st.form("new_incident_form"):
#             st.subheader("Create New Incident")
            
#             # Basic Information
#             title = st.text_input("Title")
#             description = st.text_area("Description")
#             severity = st.selectbox(
#                 "Severity",
#                 options=[s.value for s in Severity],
#                 format_func=str.upper
#             )
            
#             # Context Information
#             st.subheader("Environment Context")
#             application = st.text_input("Application", value="default-app")
#             environment = st.text_input("Environment", value="production")
#             component = st.text_input("Component", value="api")
            
#             if st.form_submit_button("Create Incident"):
#                 create_new_incident(
#                     manager, title, description, severity,
#                     application, environment, component
#                 )

# def create_new_incident(manager, title, description, severity, 
#                        application, environment, component):
#     """Create new incident with error handling"""
#     if not (title and description):
#         st.error("Title and description are required")
#         return

#     try:
#         current_time = datetime.utcnow()
#         incident_id = current_time.strftime("%Y%m%d-%H%M%S")
        
#         incident_data = {
#             "id": incident_id,
#             "title": title,
#             "description": description,
#             "severity": severity.lower(),
#             "status": IncidentStatus.NEW.value,
#             "context": {
#                 "application": application,
#                 "environment": environment,
#                 "component": component
#             },
#             "logs": [],
#             "code_references": [],
#             "created_at": current_time,
#             "updated_at": current_time
#         }

#         created_id = asyncio.run(manager.create_incident(incident_data))
        
#         # Update session state
#         st.session_state.current_incident_id = created_id
#         st.session_state.last_update = current_time
        
#         st.success(f"Incident created: {created_id}")
#         st.rerun()
#     except Exception as e:
#         st.error(f"Error creating incident: {str(e)}")


# def display_incident(incident: dict, manager: IncidentManager):
#     """Enhanced incident display with state management"""
#     st.markdown(f"## {incident['title']}")

#     # Display dashboard metrics
#     display_dashboard(incident)

#     st.markdown("### Description")
#     st.info(incident["description"])

#     # Create tabs with state management
#     tab_titles = ["Analysis", "Metrics", "Context", "Logs", "Code", "Actions"]
#     tabs = st.tabs(tab_titles)

#     # Handle tab content with state preservation
#     with tabs[0]:
#         if st.session_state.current_tab == "Analysis":
#             display_analysis_tab(incident, manager)
#     with tabs[1]:
#         if st.session_state.current_tab == "Metrics":
#             display_metrics_tab(incident)
#     with tabs[2]:
#         if st.session_state.current_tab == "Context":
#             display_context_tab(incident)
#     with tabs[3]:
#         if st.session_state.current_tab == "Logs":
#             display_logs_tab(incident)
#     with tabs[4]:
#         if st.session_state.current_tab == "Code":
#             display_code_tab(incident)
#     with tabs[5]:
#         if st.session_state.current_tab == "Actions":
#             display_actions_tab(incident, manager)

#     # Update current tab if changed
#     for i, tab in enumerate(tabs):
#         if tab:
#             # Check if tab changed
#             new_tab = tab_titles[i]
#             if new_tab != st.session_state.current_tab:
#                 st.session_state.current_tab = new_tab
#                 st.rerun()

# def display_dashboard(incident: dict):
#     """Enhanced dashboard display"""
#     dashboard = st.container()
#     with dashboard:
#         col1, col2, col3, col4, col5 = st.columns(5)
        
#         with col1:
#             st.metric("Status", incident['status'].upper())
#         with col2:
#             st.metric("Severity", incident['severity'].upper())
#         with col3:
#             st.metric("Age", get_incident_age(incident['created_at']))
#         with col4:
#             metrics_count = len(incident.get('metrics', []))
#             st.metric("Metrics", metrics_count)
#         with col5:
#             logs_count = len(incident.get('logs', []))
#             st.metric("Logs", logs_count)

# def get_incident_age(created_at: datetime) -> str:
#     """Calculate human-readable incident age"""
#     age = datetime.utcnow() - created_at
#     if age < timedelta(hours=1):
#         return f"{int(age.total_seconds() / 60)}m"
#     elif age < timedelta(days=1):
#         return f"{int(age.total_seconds() / 3600)}h"
#     else:
#         return f"{age.days}d"


# def display_actions_tab(incident: dict, manager: IncidentManager):
#     """Enhanced actions tab with state management"""
#     st.markdown("### Actions")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         if incident['status'] != IncidentStatus.RESOLVED.value:
#             if st.button("Mark as Resolved"):
#                 resolve_incident(incident, manager)
    
#     with col2:
#         if st.button("Refresh Data"):
#             refresh_incident_data(incident['id'], manager)
    
#     with col3:
#         if st.button("Export Analysis"):
#             export_incident_analysis(incident)

#     # Display additional controls
#     with st.expander("Advanced Options", expanded=False):
#         st.markdown("#### Analysis Settings")
#         auto_refresh = st.checkbox(
#             "Auto-refresh data",
#             value=False,
#             key="auto_refresh"
#         )
#         if auto_refresh:
#             refresh_interval = st.slider(
#                 "Refresh interval (seconds)",
#                 min_value=30,
#                 max_value=300,
#                 value=60
#             )
#             if st.session_state.last_update:
#                 time_since_update = (datetime.utcnow() - st.session_state.last_update).total_seconds()
#                 if time_since_update >= refresh_interval:
#                     refresh_incident_data(incident['id'], manager)

# def resolve_incident(incident: dict, manager: IncidentManager):
#     """Handle incident resolution"""
#     try:
#         asyncio.run(manager.resolve_incident(incident['id']))
#         st.session_state.last_update = datetime.utcnow()
#         st.success("Incident marked as resolved")
#         st.rerun()
#     except Exception as e:
#         st.error(f"Error resolving incident: {str(e)}")

# def refresh_incident_data(incident_id: str, manager: IncidentManager):
#     """Refresh incident data"""
#     try:
#         incident = asyncio.run(manager.get_incident(incident_id))
#         if incident:
#             st.session_state.incident_data = incident
#             st.session_state.last_update = datetime.utcnow()
#             st.success("Data refreshed successfully")
#             st.rerun()
#     except Exception as e:
#         st.error(f"Error refreshing data: {str(e)}")

# def export_incident_analysis(incident: dict):
#     """Export incident analysis"""
#     try:
#         export_data = {
#             "incident": incident,
#             "environment": incident.get('context', {}),
#             "analysis_results": incident.get('analysis_results', {}),
#             "exported_at": datetime.utcnow().isoformat()
#         }
        
#         st.download_button(
#             "Download Analysis",
#             data=str(export_data),
#             file_name=f"incident_{incident['id']}_analysis.json",
#             mime="application/json"
#         )
#     except Exception as e:
#         st.error(f"Error exporting analysis: {str(e)}")