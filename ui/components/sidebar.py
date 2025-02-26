import streamlit as st
from datetime import datetime

def display_sidebar_header():
    """Display header information in sidebar"""
    st.sidebar.markdown("# AI Insight Agent 🤖")
    
    # Display current time
    st.sidebar.markdown(
        f"_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
    )
    
    # Add theme toggle
    with st.sidebar.expander("⚙️ Settings", expanded=False):
        # Theme toggle
        dark_mode = st.checkbox(
            "Dark Mode",
            value=st.session_state.get('dark_mode', False),
            key='dark_mode_toggle'
        )
        if dark_mode != st.session_state.get('dark_mode', False):
            st.session_state.dark_mode = dark_mode
            st.rerun()
            
        # Debug mode toggle
        st.checkbox(
            "Debug Mode",
            value=st.session_state.get('debug_mode', False),
            key='debug_mode_toggle'
        )
    
    st.sidebar.markdown("---")