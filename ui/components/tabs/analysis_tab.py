import streamlit as st
import asyncio
from contracts.incident import IncidentState, Incident
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def display_analysis_tab(incident_state: IncidentState, manager):
    """Display analysis tab with state persistence"""
    st.markdown("### Analysis")

    # Use existing analysis results if available
    if incident_state.analysis_results:
        display_existing_analysis(incident_state.analysis_results)

        # Show a button to re-run analysis if needed
        if st.button("Run New Analysis"):
            perform_analysis(incident_state, manager)
    else:
       # If no previous analysis exists, show a prominent analysis button
        st.info("No analysis has been performed on this incident yet.")

        # Center the button in the middle column
        if st.button("Start Initial Analysis", use_container_width=True):
            # handle async call properly
            perform_analysis(incident_state, manager)
        
        # Show some helpful context about what the analysis will do
        with st.expander("ℹ️ About the Analysis", expanded=True):
            st.markdown("""
            The analysis will:
            - Collect and analyze incident metrics
            - Process incident logs
            - Identify potential root causes
            - Analyze related code references
            - Generate performance insights
            """)

    
    
    # # Analysis configuration
    # with st.expander("Analysis Configuration", expanded=False):
    #     analysis_type = st.selectbox(
    #         "Analysis Type",
    #         ["Full Analysis", "Root Cause Only", "Performance Only"]
    #     )
        
    #     include_metrics = st.checkbox("Include Metrics Analysis", value=True)
    #     include_logs = st.checkbox("Include Log Analysis", value=True)

    # Progress tracking
    # if st.button("Start Analysis"):
    #     perform_analysis(incident_state.incident, manager)

def display_existing_analysis(analysis_results: dict):
    """Display existing analysis results"""
    # Create columns for metadata and timestamps
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("#### Previous Analysis Results")
    with col2:
        if "metadata" in analysis_results and "analyzed_at" in analysis_results["metadata"]:
            st.markdown(f"*Last analyzed: {analysis_results['metadata']['analyzed_at']}*")
    
    # Root cause analysis
    if "root_cause" in analysis_results:
        with st.expander("🔍 Root Cause Analysis", expanded=True):
            st.info(analysis_results["root_cause"])

    # Code analysis
    if "code_analysis" in analysis_results:
        with st.expander("💻 Code Analysis", expanded=True):
            st.info(analysis_results["code_analysis"])

    # Performance analysis
    if "performance_analysis" in analysis_results:
        with st.expander("📈 Performance Analysis", expanded=True):
            st.info(analysis_results["performance_analysis"])
    
     # Analysis metadata
    if "metadata" in analysis_results:
        with st.expander("ℹ️ Analysis Metadata", expanded=False):
            st.json(analysis_results["metadata"])


def perform_analysis(incident_state: IncidentState, manager):
    """Perform incident analysis and update state"""

    logger.info("Performing analysis...")

    logger.info(f"Analyzing incident: {incident_state}")

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
            
            # Phase 1: Data Collection
            st.markdown("📥 **Phase 1: Collecting Data**")
            st.markdown("- Gathering incident metrics")
            st.markdown("- Processing incident logs")
            st.markdown("- Analyzing code references")
            analysis_results = asyncio.run(
                manager.analyze_incident(incident_state.incident_id)
            )
            progress_bar.progress(30)
            
            st.markdown("🔍 **Phase 2: Analysis**")
            # Display and store results
            display_analysis_results(analysis_results, progress_bar)
            
            # Phase 3: Completion
            progress_bar.progress(100)
            status_text.success("✅ Analysis completed successfully!")

    except Exception as e:
        progress_bar.progress(100)
        status_text.error(f"Analysis failed: {str(e)}")

def display_analysis_results(results: dict, progress_bar):
    """Display analysis results with progress updates"""
    if "root_cause" in results:
        st.markdown("🔍 **Root Cause Analysis**")
        st.info(results["root_cause"])
        progress_bar.progress(50)

    if "code_analysis" in results:
        st.markdown("💻 **Code Analysis**")
        st.info(results["code_analysis"])
        progress_bar.progress(70)

    if "performance_analysis" in results:
        st.markdown("📈 **Performance Analysis**")
        st.info(results["performance_analysis"])
        progress_bar.progress(90)

    if "metadata" in results:
        st.markdown("#### Analysis Summary")
        st.json(results["metadata"])
