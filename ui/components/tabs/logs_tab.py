import streamlit as st
from datetime import datetime

from contracts.incident import Incident

def display_logs_tab(incident: Incident):
    """Display logs with component state instead of session state"""
    st.markdown("### Logs")

    if not incident.logs:
        st.info("No logs available for this incident")
        return

    # Filtering controls using component state
    col1, col2 = st.columns([2, 3])
    with col1:
        log_level = st.selectbox(
            "Filter by Level",
            options=["ALL", "ERROR", "WARNING", "INFO", "DEBUG"]
        )
    with col2:
        search_term = st.text_input(
            "Search in logs",
            placeholder="Enter search term..."
        )

    # Time range filter
    try:
        log_times = [log['timestamp'] for log in incident.logs]
        min_time = min(log_times)
        max_time = max(log_times)
        
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            start_time = st.date_input(
                "From Date",
                value=min_time.date(),
                min_value=min_time.date(),
                max_value=max_time.date()
            )
        with time_col2:
            end_time = st.date_input(
                "To Date",
                value=max_time.date(),
                min_value=min_time.date(),
                max_value=max_time.date()
            )
    except (AttributeError, TypeError):
        st.warning("Invalid timestamp data in logs")
        start_time = end_time = None

    # Apply filters
    filtered_logs = filter_logs(incident.logs, log_level, search_term, start_time, end_time)
    display_filtered_logs(filtered_logs)
    display_log_statistics(incident.logs)

def apply_log_filters(logs: list) -> list:
    """Apply filters to logs with state persistence"""
    # Log Level Filter
    col1, col2 = st.columns([2, 3])
    with col1:
        log_level = st.selectbox(
            "Filter by Level",
            options=["ALL", "ERROR", "WARNING", "INFO", "DEBUG"],
            key="log_level_filter",
            index=["ALL", "ERROR", "WARNING", "INFO", "DEBUG"].index(
                st.session_state.log_filter_state['level']
            )
        )
    with col2:
        search_term = st.text_input(
            "Search in logs",
            value=st.session_state.log_filter_state['search_term'],
            key="log_search",
            placeholder="Enter search term..."
        )

    # Time Range Filter
    try:
        log_times = [log['timestamp'] for log in logs]
        min_time = min(log_times)
        max_time = max(log_times)
        
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            start_time = st.date_input(
                "From Date",
                value=min_time.date(),
                min_value=min_time.date(),
                max_value=max_time.date()
            )
        with time_col2:
            end_time = st.date_input(
                "To Date",
                value=max_time.date(),
                min_value=min_time.date(),
                max_value=max_time.date()
            )
    except (AttributeError, TypeError):
        st.warning("Invalid timestamp data in logs")
        start_time = end_time = None

    # Update filter state
    st.session_state.log_filter_state = {
        'level': log_level,
        'search_term': search_term,
        'time_range': {'start': start_time, 'end': end_time} if start_time and end_time else None
    }

    # Apply filters
    filtered_logs = filter_logs(logs, log_level, search_term, start_time, end_time)
    return filtered_logs

def filter_logs(logs: list, level: str, search_term: str, start_time, end_time) -> list:
    """Filter logs based on criteria"""
    filtered_logs = []
    for log in logs:
        # Level filter
        if level != "ALL" and log['level'] != level:
            continue
            
        # Search term filter
        if search_term and search_term.lower() not in log['message'].lower():
            continue
            
        # Time range filter
        if start_time and end_time:
            try:
                log_date = log['timestamp'].date()
                if not (start_time <= log_date <= end_time):
                    continue
            except (AttributeError, TypeError):
                continue
                
        filtered_logs.append(log)
    
    return filtered_logs

def display_filtered_logs(logs: list):
    """Display filtered logs with formatting"""
    log_container = st.container()
    with log_container:
        # Color coding for log levels
        level_colors = {
            "ERROR": "🔴",
            "WARNING": "🟡",
            "INFO": "🔵",
            "DEBUG": "⚪"
        }
        
        for log in logs:
            level_icon = level_colors.get(log['level'], "⚫")
            
            with st.expander(
                f"{level_icon} [{log['timestamp']}] {log['level']}: {log['message'][:100]}...",
                expanded=False
            ):
                st.code(f"""Timestamp: {log['timestamp']}
Level: {log['level']}
Message: {log['message']}""")
                
                if 'attributes' in log and log['attributes']:
                    st.markdown("**Additional Attributes:**")
                    st.json(log['attributes'])

def display_log_statistics(logs: list):
    """Display log statistics summary"""
    st.markdown("### Log Statistics")
    
    # Calculate statistics
    stats = get_log_statistics(logs)
    
    # Display statistics in columns
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.metric("Total Logs", stats['total'])
    with stat_cols[1]:
        st.metric("Error Logs", stats['error_count'])
    with stat_cols[2]:
        st.metric("Warning Logs", stats['warning_count'])
    with stat_cols[3]:
        st.metric("Info Logs", stats['info_count'])

def get_log_statistics(logs: list) -> dict:
    """Calculate log statistics"""
    stats = {
        'total': len(logs),
        'error_count': 0,
        'warning_count': 0,
        'info_count': 0,
        'debug_count': 0
    }
    
    for log in logs:
        level = log.get('level', '').upper()
        if level == 'ERROR':
            stats['error_count'] += 1
        elif level == 'WARNING':
            stats['warning_count'] += 1
        elif level == 'INFO':
            stats['info_count'] += 1
        elif level == 'DEBUG':
            stats['debug_count'] += 1
            
    return stats