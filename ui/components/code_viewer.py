import streamlit as st
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from contracts.incident import Incident

def display_code(code: str, language: str = "python"):
    lexer = get_lexer_by_name(language, stripall=True)
    formatter = HtmlFormatter(style="colorful")
    highlighted_code = highlight(code, lexer, formatter)
    st.markdown(highlighted_code, unsafe_allow_html=True)

def display_code_diff(old_code: str, new_code: str, language: str = "python"):
    st.markdown("#### Old Code")
    display_code(old_code, language)
    st.markdown("#### New Code")
    display_code(new_code, language)


def display_code_tab(incident: Incident):
    if isinstance(incident, dict):
        incident = Incident(**incident)
        
    st.markdown("### Code Analysis")
    
    if incident.code_references:
        for ref in incident.code_references:
            with st.expander(f"File: {ref.get('file_path', 'Unknown')}"):
                if 'old_code' in ref and 'new_code' in ref:
                    display_code_diff(
                        ref['old_code'],
                        ref['new_code'],
                        ref.get('language', 'python')
                    )
                elif 'code' in ref:
                    display_code(
                        ref['code'],
                        ref.get('language', 'python')
                    )
    else:
        st.info("No code references available")