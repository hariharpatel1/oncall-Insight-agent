import streamlit as st
import asyncio
from ui.pages.analyzer import analyzer_page
from ui.pages.insights import insights_page
from ui.components.sidebar import display_sidebar_header
from ui.utils.theme import setup_custom_theme

def initialize_app_state():
    """Initialize only essential UI preferences"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False

def main():
    """Main application entry point"""
    # Configure page settings
    st.set_page_config(
        page_title="AI Insight Agent",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize minimal app state
    initialize_app_state()

    # Setup custom theme and styling
    setup_custom_theme()

    # Display sidebar header
    with st.sidebar:
        display_sidebar_header()
        selected_page = display_navigation()

    # Route to selected page
    try:
        if selected_page == "Insights Dashboard":
            asyncio.run(insights_page())
        else:
            analyzer_page()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        display_error_recovery()

def display_navigation():
    """Display navigation options in sidebar and return selected page"""
    pages = {
        "Incident Analyzer": {
            "icon": "🔍",
            "description": "Analyze and manage incidents"
        },
        "Insights Dashboard": {
            "icon": "📊",
            "description": "View analytics and insights"
        }
    }

    st.sidebar.markdown("### Navigation")

    # Create radio buttons with icons and descriptions
    selected_page = st.sidebar.radio(
        "Select a page",
        list(pages.keys()),
        format_func=lambda x: f"{pages[x]['icon']} {x}",
        help="Choose which page to view"
    )

    # Display page description
    st.sidebar.markdown(f"_{pages[selected_page]['description']}_")

    return selected_page

def display_error_recovery():
    """Display error recovery options"""
    st.markdown("### Error Recovery Options")
    
    if st.button("Reset Application"):
        # Clear only UI preferences
        if 'dark_mode' in st.session_state:
            del st.session_state.dark_mode
        if 'debug_mode' in st.session_state:
            del st.session_state.debug_mode
        initialize_app_state()
        st.rerun()
        
    if st.button("Reload Page"):
        st.rerun()

if __name__ == "__main__":
    main()