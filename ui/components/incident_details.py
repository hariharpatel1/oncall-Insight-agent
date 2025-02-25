import streamlit as st
from datetime import datetime, timedelta

from contracts.incident import Incident
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def display_incident_details(incident: Incident):

    if isinstance(incident, dict):
        incident = Incident(**incident)
    
    st.markdown(f"## {incident.title}")

    # Display dashboard metrics
    display_dashboard(incident)

    st.markdown("### Description")
    st.info(incident.description)

def display_dashboard(incident: Incident):
    """Enhanced dashboard display with metrics"""
    dashboard = st.container()
    with dashboard:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Status", incident.status.upper())
        with col2:
            st.metric("Severity", incident.severity.upper())
        with col3:
            st.metric("Age", get_incident_age(incident.created_at))
        with col4:
            metrics_count = len(incident.metrics)
            st.metric("Metrics", metrics_count)
        with col5:
            logs_count = len(incident.logs)
            st.metric("Logs", logs_count)

def get_incident_age(created_at: datetime) -> str:
    """Calculate human-readable incident age"""
    age = datetime.utcnow() - created_at
    if age < timedelta(hours=1):
        return f"{int(age.total_seconds() / 60)}m"
    elif age < timedelta(days=1):
        return f"{int(age.total_seconds() / 3600)}h"
    else:
        return f"{age.days}d"

def get_incident_status_class(status: str) -> str:
    """Get CSS class for incident status"""
    status_classes = {
        'new': 'status-new',
        'in_progress': 'status-in-progress',
        'resolved': 'status-resolved',
        'closed': 'status-closed'
    }
    return status_classes.get(status.lower(), 'status-default')

def get_severity_class(severity: str) -> str:
    """Get CSS class for incident severity"""
    severity_classes = {
        'critical': 'severity-critical',
        'high': 'severity-high',
        'medium': 'severity-medium',
        'low': 'severity-low'
    }
    return severity_classes.get(severity.lower(), 'severity-default')