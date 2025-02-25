import streamlit as st
from datetime import datetime

from contracts.incident import IncidentState

def display_history_tab(incident_state: IncidentState):
    """Display incident history and analysis steps"""
    st.markdown("### Incident History")
    
    # Display analysis steps
    if incident_state.analysis_steps:
        st.markdown("#### Analysis Steps")
        for step in incident_state.analysis_steps:
            with st.expander(
                f"📋 {step['step_type']} - {step['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                expanded=False
            ):
                # Display step details
                st.markdown(f"**Type:** {step['step_type']}")
                st.markdown(f"**Confidence Score:** {step['confidence_score']:.2f}")
                
                # Input context
                st.markdown("**Input Context:**")
                st.json(step['input_context'])
                
                # Output results
                st.markdown("**Results:**")
                st.json(step['output_result'])

    # Display conversation history
    if incident_state.conversation_history:
        st.markdown("#### Event Timeline")
        for message in incident_state.conversation_history:
            with st.expander(
                f"💬 {message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {message['role']}",
                expanded=False
            ):
                st.markdown(f"**Type:** {message.get('analysis_type', 'message')}")
                st.markdown(message['content'])

    # Display state changes
    st.markdown("#### State Changes")
    changes = [
        {'timestamp': incident_state.incident.created_at, 'event': 'Incident Created'},
        {'timestamp': incident_state.incident.updated_at, 'event': 'Last Updated'}
    ]
    
    # Sort all changes by timestamp
    changes.sort(key=lambda x: x['timestamp'])
    
    # Display changes in a timeline
    for change in changes:
        st.markdown(
            f"🕒 **{change['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}** - {change['event']}"
        )