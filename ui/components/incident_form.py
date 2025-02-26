import streamlit as st
import asyncio
from datetime import datetime
from contracts.base import Severity
from contracts.incident import IncidentStatus, Incident, EnvironmentContext


def display_incident_form(manager):
    """Display incident creation form in sidebar"""
    with st.sidebar:
        with st.form("new_incident_form"):
            st.subheader("Create New Incident")
            
            # Basic Information
            title = st.text_input("Title")
            description = st.text_area("Description")
            severity = st.selectbox(
                "Severity",
                options=[s.value for s in Severity],
                format_func=str.upper
            )
            
            # Context Information
            st.subheader("Environment Context")
            application = st.text_input("Application", value="default-app")
            environment = st.text_input("Environment", value="production")
            component = st.text_input("Component", value="api")
            
            if st.form_submit_button("Create Incident"):
                create_new_incident(
                    manager, title, description, severity,
                    application, environment, component
                )

def create_new_incident(manager, title, description, severity, 
                       application, environment, component):
    """Create new incident with error handling"""
    if not (title and description):
        st.error("Title and description are required")
        return

    try:
        current_time = datetime.utcnow()
        incident_id = current_time.strftime("%Y%m%d-%H%M%S")

        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            severity=severity.lower(),
            status=IncidentStatus.NEW.value,
            context=EnvironmentContext(
                application=application,
                environment=environment,
                component=component
            ),
            logs=[],
            code_references=[],
            metrics=[],
            created_at=current_time,
            updated_at=current_time
        )

        created_id = asyncio.run(manager.create_incident(incident))
        st.success(f"Incident created: {created_id}")
        
    except Exception as e:
        st.error(f"Error creating incident: {str(e)}")