import asyncio
import streamlit as st

from core.manager import IncidentManager
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def update_incident_data(manager, incident_id):
    """Update incident data in session state"""
    try:
        incident = asyncio.run(manager.get_incident(incident_id))
        if incident:
            st.session_state.incident_data = incident
            return True
    except Exception as e:
        logger.error(f"Error updating incident data: {str(e)}")
    return False

def display_analysis_tab(incident: dict, manager: IncidentManager):
    """Enhanced analysis tab with progress tracking"""
    st.markdown("### Analysis")

    # Analysis configuration
    with st.expander("Analysis Configuration", expanded=False):
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Full Analysis", "Root Cause Only", "Performance Only"]
        )
        
        include_metrics = st.checkbox("Include Metrics Analysis", value=True)
        include_logs = st.checkbox("Include Log Analysis", value=True)

    # Progress tracking
    if st.button("Start Analysis"):
        analysis_placeholder = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Initialize analysis
            status_text.text("Initializing analysis...")
            progress_bar.progress(10)

            # Analyze incident
            with analysis_placeholder.container():
                st.markdown("#### Analysis Progress")
                
                # Monitoring data collection
                st.markdown("📥 **Collecting Monitoring Data**")
                analysis_results = asyncio.run(
                    manager.analyze_incident(incident['id'])
                )
                progress_bar.progress(30)
                
                # Root cause analysis
                if "root_cause" in analysis_results:
                    st.markdown("🔍 **Root Cause Analysis**")
                    st.info(analysis_results["root_cause"])
                    progress_bar.progress(50)

                # Code analysis
                if "code_analysis" in analysis_results:
                    st.markdown("💻 **Code Analysis**")
                    st.info(analysis_results["code_analysis"])
                    progress_bar.progress(70)

                # Performance analysis
                if "performance_analysis" in analysis_results:
                    st.markdown("📈 **Performance Analysis**")
                    st.info(analysis_results["performance_analysis"])
                    progress_bar.progress(90)

                # Final results
                st.markdown("#### Analysis Summary")
                if "metadata" in analysis_results:
                    st.json(analysis_results["metadata"])
                
                progress_bar.progress(100)
                status_text.text("Analysis completed!")

        except Exception as e:
            progress_bar.progress(100)
            status_text.error(f"Analysis failed: {str(e)}")


def display_context_tab(incident: dict):
    """Display incident context information"""
    st.markdown("### Context Information")
    
    # Basic context
    context = incident.get('context', {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Application", context.application)
    with col2:
        st.metric("Environment", context.environment)
    with col3:
        st.metric("Component", context.component)

    # Additional metadata
    st.markdown("#### Metadata")
    meta_cols = st.columns(2)
    with meta_cols[0]:
        st.write("**Created At:**", incident.get('created_at', 'N/A'))
    with meta_cols[1]:
        st.write("**Last Updated:**", incident.get('updated_at', 'N/A'))

    # Analysis history if available
    if 'analysis_results' in incident and incident['analysis_results']:
        with st.expander("Analysis History", expanded=False):
            for analysis in incident['analysis_results']:
                st.markdown(f"**Type:** {analysis.get('type', 'Unknown')}")
                st.markdown(f"**Confidence:** {analysis.get('confidence', 0) * 100:.1f}%")
                st.markdown(f"**Timestamp:** {analysis.get('timestamp', 'N/A')}")
                st.markdown("---")

def display_logs_tab(incident: dict):
    """Display incident logs with filtering and search"""
    st.markdown("### Logs")

    # Log filtering controls
    col1, col2 = st.columns([2, 3])
    with col1:
        log_level = st.selectbox(
            "Filter by Level",
            options=["ALL", "ERROR", "WARNING", "INFO", "DEBUG"],
            key="log_level_filter"
        )
    with col2:
        search_term = st.text_input(
            "Search in logs",
            key="log_search",
            placeholder="Enter search term..."
        )

    # Time range filter
    if incident.get('logs'):
        try:
            log_times = [log['timestamp'] for log in incident['logs']]
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
    else:
        start_time = end_time = None

    # Display logs with filtering
    if incident.get('logs'):
        # Create columns for log table
        log_container = st.container()
        with log_container:
            for log in filter_logs(
                incident['logs'],
                log_level,
                search_term,
                start_time,
                end_time
            ):
                # Color coding based on log level
                level_colors = {
                    "ERROR": "🔴",
                    "WARNING": "🟡",
                    "INFO": "🔵",
                    "DEBUG": "⚪"
                }
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
    else:
        st.info("No logs available for this incident")

    # Add log statistics
    if incident.get('logs'):
        st.markdown("### Log Statistics")
        log_stats = get_log_statistics(incident['logs'])
        
        # Display statistics in columns
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("Total Logs", log_stats['total'])
        with stat_cols[1]:
            st.metric("Error Logs", log_stats['error_count'])
        with stat_cols[2]:
            st.metric("Warning Logs", log_stats['warning_count'])
        with stat_cols[3]:
            st.metric("Info Logs", log_stats['info_count'])

def filter_logs(logs, level, search_term, start_time, end_time):
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

def get_log_statistics(logs):
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
