import pandas as pd
import streamlit as st
import altair as alt
from typing import List
import plotly.graph_objects as go
from contracts.monitoring import Metric, MetricType

def display_metrics(metrics: List[Metric]):
    data = [metric.model_dump() for metric in metrics]
    chart = alt.Chart(data).mark_line().encode(
        x="timestamp:T",
        y="value:Q",
        color="name:N",
        tooltip=["name", "value", "timestamp"],
    ).properties(
        width=600,
        height=400,
        title="Metrics",
    )
    st.altair_chart(chart)

def display_performance_graph(metrics: List[Metric]):
    # Implement performance graph visualization using Altair or Plotly
    pass

def display_metrics_tab(incident: dict):
    """Display incident metrics with enhanced visualizations"""
    st.markdown("### Metrics Dashboard")

    # Convert metrics to proper objects if they're dictionaries
    metrics = [
        Metric(**m) if isinstance(m, dict) else m 
        for m in incident.get('metrics', [])
    ]

    if not metrics:
        st.info("No metrics available for this incident")
        return

    # Create DataFrame with proper handling of metric types
    df = pd.DataFrame([{
        'name': m.name,
        'value': m.value,
        'timestamp': m.timestamp,
        'type': m.type.value,
        'labels': str(m.labels) if m.labels else None
    } for m in metrics])

    # Metrics Overview Section
    st.markdown("#### Metrics Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Metrics", len(metrics))
    with col2:
        counter_metrics = sum(1 for m in metrics if m.type == MetricType.COUNTER)
        st.metric("Counters", counter_metrics)
    with col3:
        gauge_metrics = sum(1 for m in metrics if m.type == MetricType.GAUGE)
        st.metric("Gauges", gauge_metrics)
    with col4:
        if not df.empty:
            time_range = df['timestamp'].max() - df['timestamp'].min()
            st.metric("Time Range", f"{time_range.total_seconds()/3600:.1f}h")

    # Metric Type Filter
    metric_type = st.selectbox(
        "Filter by Metric Type",
        ["All Types", "Counter", "Gauge"],
        key="metric_type_filter"
    )

    # Filter metrics by type
    if metric_type != "All Types":
        df = df[df['type'].str.lower() == metric_type.lower()]

    # Get unique metric names after type filtering
    metric_names = sorted(df['name'].unique())

    selected_metrics = st.multiselect(
        "Select metrics to display",
        options=metric_names,
        default=metric_names[:min(3, len(metric_names))],
    )

    if not df.empty:
        # Time range selection with preservation
        if 'metrics_time_range' not in st.session_state:
            st.session_state.metrics_time_range = {
                'start': df['timestamp'].min().date(),
                'end': df['timestamp'].max().date()
            }

        time_col1, time_col2 = st.columns(2)
        with time_col1:
            start_time = st.date_input(
                "From Date",
                value=st.session_state.metrics_time_range['start'],
                min_value=df['timestamp'].min().date(),
                max_value=df['timestamp'].max().date(),
                key="metrics_start_date"
            )
        with time_col2:
            end_time = st.date_input(
                "To Date",
                value=st.session_state.metrics_time_range['end'],
                min_value=df['timestamp'].min().date(),
                max_value=df['timestamp'].max().date(),
                key="metrics_end_date"
            )

        st.session_state.metrics_time_range = {'start': start_time, 'end': end_time}

        # Filter data
        filtered_df = df[
            (df['name'].isin(selected_metrics)) &
            (df['timestamp'].dt.date >= start_time) &
            (df['timestamp'].dt.date <= end_time)
        ]

        if not filtered_df.empty:
            # Visualization tabs
            viz_tabs = st.tabs(["Time Series", "Gauges", "Statistics"])
            
            # Time Series Tab
            with viz_tabs[0]:
                fig = go.Figure()
                for metric in selected_metrics:
                    metric_data = filtered_df[filtered_df['name'] == metric]
                    if not metric_data.empty:
                        metric_type = metric_data['type'].iloc[0]
                        # Different visualizations for different metric types
                        if metric_type == MetricType.COUNTER.value:
                            # For counters, show the rate of change
                            metric_data['rate'] = metric_data['value'].diff()
                            fig.add_trace(go.Scatter(
                                x=metric_data['timestamp'],
                                y=metric_data['rate'],
                                name=f"{metric} (rate)",
                                mode='lines+markers'
                            ))
                        else:
                            fig.add_trace(go.Scatter(
                                x=metric_data['timestamp'],
                                y=metric_data['value'],
                                name=metric,
                                mode='lines+markers'
                            ))

                fig.update_layout(
                    title="Metrics Timeline",
                    xaxis_title="Time",
                    yaxis_title="Value",
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Gauges Tab
            with viz_tabs[1]:
                gauge_cols = st.columns(min(len(selected_metrics), 3))
                for idx, metric in enumerate(selected_metrics):
                    metric_data = filtered_df[filtered_df['name'] == metric]
                    if not metric_data.empty:
                        with gauge_cols[idx % 3]:
                            current_value = metric_data['value'].iloc[-1]
                            max_value = metric_data['value'].max()
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=current_value,
                                title={'text': metric},
                                gauge={'axis': {'range': [0, max_value * 1.2]}}
                            ))
                            fig.update_layout(height=200)
                            st.plotly_chart(fig, use_container_width=True)

            # Statistics Tab
            with viz_tabs[2]:
                for metric in selected_metrics:
                    metric_data = filtered_df[filtered_df['name'] == metric]
                    if not metric_data.empty:
                        with st.expander(f"📊 {metric} Statistics", expanded=True):
                            stat_cols = st.columns(4)
                            with stat_cols[0]:
                                st.metric("Current", f"{metric_data['value'].iloc[-1]:.2f}")
                            with stat_cols[1]:
                                st.metric("Average", f"{metric_data['value'].mean():.2f}")
                            with stat_cols[2]:
                                st.metric("Max", f"{metric_data['value'].max():.2f}")
                            with stat_cols[3]:
                                st.metric("Min", f"{metric_data['value'].min():.2f}")

                            # Show rate of change for counters
                            if metric_data['type'].iloc[0] == MetricType.COUNTER.value:
                                st.markdown("##### Rate of Change")
                                rate = metric_data['value'].diff()
                                rate_cols = st.columns(3)
                                with rate_cols[0]:
                                    st.metric("Avg Rate", f"{rate.mean():.2f}/s")
                                with rate_cols[1]:
                                    st.metric("Max Rate", f"{rate.max():.2f}/s")
                                with rate_cols[2]:
                                    st.metric("Min Rate", f"{rate.min():.2f}/s")

                            # Show labels if available
                            if 'labels' in metric_data.columns and not metric_data['labels'].isna().all():
                                st.markdown("##### Labels")
                                st.json(eval(metric_data['labels'].iloc[0]))