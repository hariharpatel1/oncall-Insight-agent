import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from contracts.incident import Incident
from contracts.monitoring import MetricType

def display_metrics_tab(incident: Incident):
    """Display metrics dashboard with enhanced visualizations"""
    st.markdown("### Metrics Dashboard")

    if not incident.metrics:
        st.info("No metrics available for this incident")
        return

    # Create DataFrame for metrics
    df = pd.DataFrame([{
        'name': m['name'],
        'value': m['value'],
        'timestamp': m['timestamp'],
        'type': m['type'],
        'labels': str(m.get('labels', {}))
    } for m in incident.metrics])

    # Metrics Overview
    display_metrics_overview(df)

    # Filters and Controls
    filtered_df = apply_metrics_filters(df)

    if not filtered_df.empty:
        display_metrics_visualizations(filtered_df)

def display_metrics_overview(df: pd.DataFrame):
    """Display metrics overview statistics"""
    st.markdown("#### Metrics Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Metrics", len(df['name'].unique()))
    with col2:
        counter_metrics = len(df[df['type'] == MetricType.COUNTER.value]['name'].unique())
        st.metric("Counters", counter_metrics)
    with col3:
        gauge_metrics = len(df[df['type'] == MetricType.GAUGE.value]['name'].unique())
        st.metric("Gauges", gauge_metrics)
    with col4:
        if not df.empty:
            time_range = df['timestamp'].max() - df['timestamp'].min()
            st.metric("Time Range", f"{time_range.total_seconds()/3600:.1f}h")

def apply_metrics_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Apply user-selected filters to metrics data"""
    # Metric Type Filter
    metric_type = st.selectbox(
        "Filter by Metric Type",
        ["All Types", "Counter", "Gauge"],
        key="metric_type_filter"
    )

    if metric_type != "All Types":
        df = df[df['type'].str.lower() == metric_type.lower()]

    # Get unique metric names after type filtering
    metric_names = sorted(df['name'].unique())
    
    # Metric Selection
    selected_metrics = st.multiselect(
        "Select metrics to display",
        options=metric_names,
        default=metric_names[:3] if metric_names else [],
        key="metrics_selection"
    )

    # Time Range Selection with unique keys
    if not df.empty:
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            start_time = st.date_input(
                "From Date",
                value=df['timestamp'].min().date(),
                min_value=df['timestamp'].min().date(),
                max_value=df['timestamp'].max().date(),
                key="metrics_start_date"
            )
        with time_col2:
            end_time = st.date_input(
                "To Date",
                value=df['timestamp'].max().date(),
                min_value=df['timestamp'].min().date(),
                max_value=df['timestamp'].max().date(),
                key="metrics_end_date"
            )

        # Filter data
        df = df[
            (df['name'].isin(selected_metrics)) &
            (df['timestamp'].dt.date >= start_time) &
            (df['timestamp'].dt.date <= end_time)
        ]

    return df

def display_metrics_visualizations(df: pd.DataFrame):
    """Display enhanced metrics visualizations with tabs"""
    viz_tabs = st.tabs(["Time Series", "Gauges", "Histograms", "Statistics"])
    
    with viz_tabs[0]:
        display_time_series(df)
        
    with viz_tabs[1]:
        display_enhanced_gauges(df)
        
    with viz_tabs[2]:
        display_histograms(df)
        
    with viz_tabs[3]:
        display_statistics(df)

def display_time_series(df: pd.DataFrame):
    """Display time series visualization"""
    fig = go.Figure()
    
    for metric in df['name'].unique():
        metric_data = df[df['name'] == metric]
        if not metric_data.empty:
            metric_type = metric_data['type'].iloc[0]
            
            if metric_type == MetricType.COUNTER.value:
                # For counters, show both absolute value and rate
                # Add absolute value line
                fig.add_trace(go.Scatter(
                    x=metric_data['timestamp'],
                    y=metric_data['value'],
                    name=f"{metric} (total)",
                    mode='lines',
                    line=dict(dash='dot')
                ))
                # Add rate of change
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
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    st.plotly_chart(fig, use_container_width=True)

def display_enhanced_gauges(df: pd.DataFrame):
    """Display enhanced gauge visualizations"""
    st.markdown("#### Current Values")
    
    gauge_cols = st.columns(min(len(df['name'].unique()), 3))
    for idx, metric in enumerate(df['name'].unique()):
        metric_data = df[df['name'] == metric]
        if not metric_data.empty:
            with gauge_cols[idx % 3]:
                current_value = metric_data['value'].iloc[-1]
                min_value = metric_data['value'].min()
                max_value = metric_data['value'].max()
                avg_value = metric_data['value'].mean()
                
                # Create gauge with reference points
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=current_value,
                    title={'text': metric},
                    delta={'reference': avg_value},
                    gauge={
                        'axis': {'range': [min_value, max_value]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [min_value, avg_value], 'color': "lightgray"},
                            {'range': [avg_value, max_value], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': max_value
                        }
                    }
                ))
                fig.update_layout(height=200)
                st.plotly_chart(fig, use_container_width=True)

def display_histograms(df: pd.DataFrame):
    """Display histogram visualizations"""
    st.markdown("#### Value Distribution")
    
    for metric in df['name'].unique():
        metric_data = df[df['name'] == metric]
        if not metric_data.empty:
            fig = px.histogram(
                metric_data, 
                x='value',
                title=f"{metric} Distribution",
                nbins=30,
                histnorm='probability'
            )
            fig.update_layout(
                showlegend=False,
                xaxis_title="Value",
                yaxis_title="Frequency",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

def display_statistics(df: pd.DataFrame):
    """Display statistical analysis of metrics"""
    for metric in df['name'].unique():
        metric_data = df[df['name'] == metric]
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

                # Advanced statistics
                if metric_data['type'].iloc[0] == MetricType.COUNTER.value:
                    st.markdown("##### Rate of Change")
                    rate = metric_data['value'].diff()
                    rate_cols = st.columns(4)
                    with rate_cols[0]:
                        st.metric("Avg Rate", f"{rate.mean():.2f}/s")
                    with rate_cols[1]:
                        st.metric("Max Rate", f"{rate.max():.2f}/s")
                    with rate_cols[2]:
                        st.metric("Min Rate", f"{rate.min():.2f}/s")
                    with rate_cols[3]:
                        st.metric("Std Dev", f"{rate.std():.2f}")