import streamlit as st

def setup_custom_theme():
    """Setup custom theme and styling"""
    # Custom theme configuration
    custom_theme = {
        'light': {
            'primaryColor': '#007bff',
            'backgroundColor': '#ffffff',
            'secondaryBackgroundColor': '#f8f9fa',
            'textColor': '#212529',
            'font': 'sans-serif'
        },
        'dark': {
            'primaryColor': '#0d6efd',
            'backgroundColor': '#212529',
            'secondaryBackgroundColor': '#343a40',
            'textColor': '#f8f9fa',
            'font': 'sans-serif'
        }
    }

    # Apply theme based on mode
    theme = custom_theme['dark'] if st.session_state.get('dark_mode', False) else custom_theme['light']
    
    # Apply custom CSS
    custom_css = f"""
        <style>
            .stApp {{
                background-color: {theme['backgroundColor']};
                color: {theme['textColor']};
                font-family: {theme['font']};
            }}
            
            .stSidebar {{
                background-color: {theme['secondaryBackgroundColor']};
            }}
            
            /* Status badges */
            .status-badge {{
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
            }}
            
            .status-new {{
                background-color: #17a2b8;
                color: white;
            }}
            
            .status-in-progress {{
                background-color: #ffc107;
                color: black;
            }}
            
            .status-resolved {{
                background-color: #28a745;
                color: white;
            }}
            
            .status-closed {{
                background-color: #6c757d;
                color: white;
            }}
            
            /* Severity indicators */
            .severity-critical {{
                color: #dc3545;
            }}
            
            .severity-high {{
                color: #fd7e14;
            }}
            
            .severity-medium {{
                color: #ffc107;
            }}
            
            .severity-low {{
                color: #28a745;
            }}
            
            /* Custom containers */
            .metric-container {{
                border: 1px solid {theme['primaryColor']};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }}
            
            .analysis-container {{
                border-left: 4px solid {theme['primaryColor']};
                padding-left: 16px;
                margin: 16px 0;
            }}
        </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)

def apply_theme_to_plotly(fig):
    """Apply current theme to Plotly figures"""
    is_dark = st.session_state.get('dark_mode', False)
    
    fig.update_layout(
        template='plotly_dark' if is_dark else 'plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f8f9fa' if is_dark else '#212529'
    )
    
    return fig

def get_color_scheme(num_colors: int = 10):
    """Get color scheme based on current theme"""
    is_dark = st.session_state.get('dark_mode', False)
    
    # Color schemes for light and dark modes
    schemes = {
        'light': [
            '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
            '#6610f2', '#fd7e14', '#20c997', '#e83e8c', '#6c757d'
        ],
        'dark': [
            '#0d6efd', '#198754', '#dc3545', '#ffc107', '#0dcaf0',
            '#6610f2', '#fd7e14', '#20c997', '#e83e8c', '#6c757d'
        ]
    }
    
    colors = schemes['dark'] if is_dark else schemes['light']
    return colors[:num_colors]