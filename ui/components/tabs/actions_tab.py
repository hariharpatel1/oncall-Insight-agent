import streamlit as st
import asyncio
from datetime import datetime
from contracts.incident import Incident, IncidentStatus
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
import io
import pandas as pd

def display_actions_tab(incident: Incident, manager):
    """Display actions tab with state management"""
    st.markdown("### Actions")
    
    # Quick Actions
    display_quick_actions(incident, manager)
    
    # Advanced Options
   # display_advanced_options(incident, manager)
    
    # Export Options
    display_export_options(incident)

def display_quick_actions(incident: Incident, manager):
    """Display quick action buttons"""
    col1, _, col3 = st.columns(3)
    
    with col1:
        if incident.status != IncidentStatus.RESOLVED.value:
            if st.button("Mark as Resolved", key="resolve_button"):
                resolve_incident(incident, manager)
    
    # with col2:
    #     if st.button("Refresh Data", key="refresh_button"):
    #         refresh_incident_data(incident['id'], manager)
    
    with col3:
        if st.button("Export Analysis", key="export_button"):
            export_incident_analysis(incident)

# def display_advanced_options(incident: dict, manager):
#     """Display advanced options and settings"""
#     with st.expander("Advanced Options", expanded=False):
#         st.markdown("#### Analysis Settings")
        
#         # Auto-refresh settings
#         auto_refresh = st.checkbox(
#             "Auto-refresh data",
#             value=False,
#             key="auto_refresh"
#         )
        
#         if auto_refresh:
#             refresh_interval = st.slider(
#                 "Refresh interval (seconds)",
#                 min_value=30,
#                 max_value=300,
#                 value=60,
#                 key="refresh_interval"
#             )
            
#             # Check if refresh is needed
#             if 'last_update' in st.session_state:
#                 time_since_update = (
#                     datetime.utcnow() - st.session_state.last_update
#                 ).total_seconds()
                
#                 if time_since_update >= refresh_interval:
#                     refresh_incident_data(incident['id'], manager)

def display_export_options(incident: Incident):
    """Display export options"""
    st.markdown("#### Export Options")
    
    export_format = st.selectbox(
        "Export Format",
        ["JSON", "CSV", "PDF"],
        key="export_format"
    )
    
    include_sections = st.multiselect(
        "Include Sections",
        ["Analysis Results", "Metrics", "Logs", "Context", "Code References"],
        default=["Analysis Results"],
        key="export_sections"
    )
    
    if st.button("Generate Export", key="generate_export"):
        generate_export(incident, export_format, include_sections)

def resolve_incident(incident: Incident, manager):
    """Handle incident resolution"""
    try:
        asyncio.run(manager.resolve_incident(incident.id))
        st.session_state.last_update = datetime.utcnow()
        st.success("Incident marked as resolved")
        st.rerun()
    except Exception as e:
        st.error(f"Error resolving incident: {str(e)}")

# def refresh_incident_data(incident_id: str, manager):
#     """Refresh incident data"""
#     try:
#         incident = asyncio.run(manager.get_incident(incident_id))
#         if incident:
#             st.session_state.incident_data = incident
#             st.session_state.last_update = datetime.utcnow()
#             st.success("Data refreshed successfully")
#             st.rerun()
#     except Exception as e:
#         st.error(f"Error refreshing data: {str(e)}")

def export_incident_analysis(incident: Incident):
    """Export incident analysis"""
    try:
        export_data = {
            "incident": incident,
            "environment": incident.context,
            "exported_at": datetime.utcnow().isoformat()
        }
        
        st.download_button(
            "Download Analysis",
            data=str(export_data),
            file_name=f"incident_{incident.id}_analysis.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"Error exporting analysis: {str(e)}")

def generate_export(incident: Incident, export_format: str, include_sections: list):
    """Generate export in selected format"""
    if isinstance(incident, dict):
        incident = Incident(**incident)
    try:
        # Prepare export data based on selected sections
        export_data = {}
        
        if "Metrics" in include_sections:
            export_data["metrics"] = incident.metrics
        if "Logs" in include_sections:
            export_data["logs"] = incident.logs
        if "Context" in include_sections:
            export_data["context"] = incident.context
        if "Code References" in include_sections:
            export_data["code_references"] = incident.code_references
            
        # Add metadata
        export_data["metadata"] = {
            "incident_id": incident.id,
            "exported_at": datetime.utcnow().isoformat(),
            "format": export_format
        }
        
        # Generate appropriate file based on format
        if export_format == "JSON":
            file_name = f"incident_{incident.id}_export.json"
            mime = "application/json"
            data = str(export_data)
        elif export_format == "CSV":
            file_name = f"incident_{incident.id}_export.csv"
            mime = "text/csv"
            # Convert to CSV format
            data = convert_to_csv(export_data)
        else:  # PDF
            file_name = f"incident_{incident.id}_export.pdf"
            mime = "application/pdf"
            data = generate_pdf_report(export_data)
        
        # Provide download button
        st.download_button(
            "Download Export",
            data=data,
            file_name=file_name,
            mime=mime
        )
    except Exception as e:
        st.error(f"Error generating export: {str(e)}")

def convert_to_csv(export_data: dict) -> str:
    """Convert export data to CSV format"""

    # Create a buffer to store CSV data
    buffer = io.StringIO()
    
    # Convert different sections to DataFrames and save to CSV
    for section, data in export_data.items():
        if section != "metadata":
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                continue
                
            # Write section header
            buffer.write(f"=== {section.upper()} ===\n")
            df.to_csv(buffer, index=False)
            buffer.write("\n\n")
    
    return buffer.getvalue()

def generate_pdf_report(export_data: dict) -> bytes:
    """Generate PDF report from export data"""
    try:
        # Create buffer for PDF
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        title = Paragraph(
            f"Incident Report - {export_data['metadata']['incident_id']}", 
            styles['Heading1']
        )
        story.append(title)
        story.append(Spacer(1, 12))

        # Add each section
        for section, data in export_data.items():
            if section != "metadata":
                # Section header
                story.append(Paragraph(section.upper(), styles['Heading2']))
                story.append(Spacer(1, 12))

                # Convert data to table format
                if isinstance(data, list):
                    if data:
                        # Get headers from first item
                        headers = list(data[0].keys())
                        table_data = [headers]
                        # Add rows
                        for item in data:
                            table_data.append([str(item.get(h, '')) for h in headers])
                        # Create table
                        table = Table(table_data)
                        story.append(table)
                elif isinstance(data, dict):
                    # Create two-column table for dict data
                    table_data = [[k, str(v)] for k, v in data.items()]
                    table = Table(table_data)
                    story.append(table)

                story.append(Spacer(1, 12))

        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except ImportError:
        st.error("PDF generation requires reportlab package")
        return None