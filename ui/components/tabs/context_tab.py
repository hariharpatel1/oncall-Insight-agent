import streamlit as st
from datetime import datetime

from contracts.incident import Incident

def display_context_tab(incident: Incident):
    """Display incident context information with enhanced visualization"""
    st.markdown("### Context Information")
    
    # Basic context metrics
    display_context_metrics(incident)
    
    # Environment details
    display_environment_details(incident)
    
    # Analysis history
    # display_analysis_history(incident)
    
    # Additional metadata
    display_metadata(incident)

def display_context_metrics(incident: Incident):
    """Display basic context metrics"""
    context = incident.context
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Application", context.application)
    with col2:
        st.metric("Environment", context.environment)
    with col3:
        st.metric("Component", context.component)

def display_environment_details(incident: Incident):
    """Display detailed environment information"""
    st.markdown("#### Environment Details")
    
    context = incident.context
    
    # Display environment details in an expandable section
    with st.expander("Environment Configuration", expanded=True):
        # Create two columns for details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Base Configuration**")
            st.markdown(f"- **Application:** {context.application}")
            st.markdown(f"- **Environment:** {context.environment}")
            st.markdown(f"- **Component:** {context.component}")
            
        with col2:
            st.markdown("**Additional Settings**")

# def display_analysis_history(incident: dict):
#     """Display analysis history if available"""
#     if 'analysis_results' in incident and incident['analysis_results']:
#         st.markdown("#### Analysis History")
        
#         with st.expander("Previous Analyses", expanded=False):
#             for analysis in incident['analysis_results']:
#                 # Create a container for each analysis
#                 with st.container():
#                     st.markdown(f"**Type:** {analysis.get('type', 'Unknown')}")
#                     st.markdown(f"**Confidence:** {analysis.get('confidence', 0) * 100:.1f}%")
#                     st.markdown(f"**Timestamp:** {analysis.get('timestamp', 'N/A')}")
                    
#                     # Display analysis results if available
#                     if 'results' in analysis:
#                         with st.expander("View Results", expanded=False):
#                             st.json(analysis['results'])
                    
#                     st.markdown("---")

def display_metadata(incident: Incident):
    """Display incident metadata"""
    if isinstance(incident, dict):
        incident = Incident(**incident)
    st.markdown("#### Metadata")
    
    # Create columns for metadata
    meta_cols = st.columns(2)
    
    with meta_cols[0]:
        # Temporal information
        st.markdown("**Temporal Information**")
        st.write("Created At:", incident.created_at)
        st.write("Last Updated:", incident.updated_at)
        
        if incident.created_at and incident.updated_at:
            duration = incident.updated_at - incident.created_at
            st.write("Age:", f"{duration.total_seconds() / 3600:.1f} hours")
    
    with meta_cols[1]:
        # Status information
        st.markdown("**Status Information**")
        st.write("Current Status:", incident.status.upper())
        st.write("Severity:", incident.severity.upper())
        
        # Calculate statistics
        if 'logs' in incident:
            st.write("Total Logs:", len(incident.logs))
        if 'metrics' in incident:
            st.write("Total Metrics:", len(incident.metrics))
