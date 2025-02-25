import streamlit as st
from typing import List
from contracts.incident import CodeReference, Incident

def display_code_tab(incident: Incident):
    """Display code references with state persistence"""
    st.markdown("### Code References")

    code_references = incident.code_references
    if not code_references:
        st.info("No code references available for this incident")
        return

    # Group code references by file
    files_dict = group_references_by_file(code_references)

    # File selection
    selected_file = st.selectbox(
        "Select File",
        options=list(files_dict.keys()),
    )

    # Display selected file's references
    if selected_file:
        display_file_references(files_dict[selected_file])

def group_references_by_file(references: List[dict]) -> dict:
    """Group code references by file path"""
    files_dict = {}
    for ref in references:
        if ref['file_path'] not in files_dict:
            files_dict[ref['file_path']] = []
        files_dict[ref['file_path']].append(ref)
    
    # Sort references by line number within each file
    for file_path in files_dict:
        files_dict[file_path].sort(key=lambda x: x['line_number'])
    
    return files_dict

def display_file_references(references: List[dict]):
    """Display all references for a selected file"""
    # File statistics
    st.markdown("#### File Statistics")
    stats_col1, stats_col2 = st.columns(2)
    with stats_col1:
        st.metric("Total References", len(references))
    with stats_col2:
        functions = set(ref['function_name'] for ref in references)
        st.metric("Functions Referenced", len(functions))

    # Display each reference
    st.markdown("#### Code Sections")
    for ref in references:
        with st.expander(
            f"Line {ref['line_number']}: {ref['function_name']}",
            expanded=False
        ):
            # Display code with syntax highlighting
            if ref.get('code'):
                st.code(ref['code'], language="python")
            
            # Display metadata
            st.markdown(f"**Function:** `{ref['function_name']}`")
            st.markdown(f"**Line Number:** {ref['line_number']}")
            
            # Add copy button for the code
            if ref.get('code'):
                st.button(
                    "Copy Code",
                    key=f"copy_{ref['file_path']}_{ref['line_number']}",
                    help="Copy code to clipboard",
                    on_click=lambda: st.clipboard.copy(ref['code'])
                )

def display_code_metrics(references: List[dict]):
    """Display metrics about code references"""
    st.markdown("#### Code Metrics")
    
    # Calculate metrics
    total_lines = sum(1 for ref in references if ref.get('code'))
    unique_functions = len(set(ref['function_name'] for ref in references))
    
    # Display metrics
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    with metrics_col1:
        st.metric("Total References", len(references))
    with metrics_col2:
        st.metric("Lines of Code", total_lines)
    with metrics_col3:
        st.metric("Unique Functions", unique_functions)