import streamlit as st
from datetime import datetime

def initialize_app_state():
    """Initialize only UI preference related state"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False

def needs_refresh(refresh_interval: int) -> bool:
    """Check if data needs to be refreshed based on interval"""
    if 'last_update' not in st.session_state:
        return True
        
    time_since_update = (
        datetime.utcnow() - st.session_state.last_update
    ).total_seconds()
    
    return time_since_update >= refresh_interval