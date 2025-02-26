import streamlit as st
from contracts.monitoring import MonitoringQuery
from monitoring.system import MonitoringSystem
from ui.components.metrics_view import display_metrics, display_performance_graph

async def insights_page():
    st.markdown("# Insights Dashboard")

    # Fetch metrics data
    monitoring_system = MonitoringSystem()
    query = MonitoringQuery(metric_name="*")
    metrics = await monitoring_system.query_monitoring_data(query)

    st.markdown("## Key Metrics")
    display_metrics(metrics["metrics"])

    st.markdown("## Performance Trends")
    display_performance_graph(metrics["metrics"])