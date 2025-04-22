import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

def create_bar_chart(df, x_column, y_column, color=None, title=None, orientation='v'):
    """
    Create a bar chart
    
    Parameters:
    - df: Pandas DataFrame
    - x_column: Column for x-axis
    - y_column: Column for y-axis
    - color: Optional column for coloring
    - title: Optional chart title
    - orientation: 'v' for vertical, 'h' for horizontal
    
    Returns:
    - Plotly figure
    """
    if df is None or df.empty:
        return None
    
    if not title:
        title = f"Bar Chart: {y_column} by {x_column}"
    
    if orientation == 'h':
        fig = px.bar(
            df, 
            y=x_column, 
            x=y_column, 
            color=color,
            title=title,
            labels={y_column: y_column, x_column: x_column},
            orientation='h'
        )
    else:
        fig = px.bar(
            df, 
            x=x_column, 
            y=y_column, 
            color=color,
            title=title,
            labels={y_column: y_column, x_column: x_column}
        )
    
    fig.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column,
        legend_title=color if color else "",
        plot_bgcolor='white',
        height=500
    )
    
    return fig

def create_line_chart(df, x_column, y_columns, title=None):
    """
    Create a line chart
    
    Parameters:
    - df: Pandas DataFrame
    - x_column: Column for x-axis
    - y_columns: List of columns for y-axis
    - title: Optional chart title
    
    Returns:
    - Plotly figure
    """
    if df is None or df.empty:
        return None
    
    if not title:
        title = f"Line Chart: {', '.join(y_columns)} over {x_column}"
    
    fig = go.Figure()
    
    for y_col in y_columns:
        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df[y_col],
                mode='lines+markers',
                name=y_col
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title=x_column,
        yaxis_title="Value",
        legend_title="Variables",
        plot_bgcolor='white',
        height=500
    )
    
    return fig

def create_scatter_plot(df, x_column, y_column, color=None, size=None, title=None):
    """
    Create a scatter plot
    
    Parameters:
    - df: Pandas DataFrame
    - x_column: Column for x-axis
    - y_column: Column for y-axis
    - color: Optional column for coloring points
    - size: Optional column for point sizes
    - title: Optional chart title
    
    Returns:
    - Plotly figure
    """
    if df is None or df.empty:
        return None
    
    if not title:
        title = f"Scatter Plot: {y_column} vs {x_column}"
    
    fig = px.scatter(
        df,
        x=x_column,
        y=y_column,
        color=color,
        size=size,
        title=title,
        labels={
            x_column: x_column,
            y_column: y_column,
            color: color if color else "",
            size: size if size else ""
        }
    )
    
    fig.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column,
        legend_title=color if color else "",
        plot_bgcolor='white',
        height=500
    )
    
    return fig

def create_histogram(df, column, bins=None, title=None, color=None):
    """
    Create a histogram
    
    Parameters:
    - df: Pandas DataFrame
    - column: Column to visualize
    - bins: Number of bins
    - title: Optional chart title
    - color: Optional column for coloring
    
    Returns:
    - Plotly figure
    """
    if df is None or df.empty:
        return None
    
    if not title:
        title = f"Histogram: Distribution of {column}"
    
    fig = px.histogram(
        df,
        x=column,
        color=color,
        nbins=bins,
        title=title,
        labels={column: column}
    )
    
    fig.update_layout(
        xaxis_title=column,
        yaxis_title="Count",
        bargap=0.1,
        plot_bgcolor='white',
        height=500
    )
    
    return fig

def create_pie_chart(df, names_column, values_column, title=None):
    """
    Create a pie chart
    
    Parameters:
    - df: Pandas DataFrame
    - names_column: Column for slice names
    - values_column: Column for slice values
    - title: Optional chart title
    
    Returns:
    - Plotly figure
    """
    if df is None or df.empty:
        return None
    
    if not title:
        title = f"Pie Chart: {values_column} by {names_column}"
    
    # Aggregate data if there are multiple entries per category
    pie_data = df.groupby(names_column)[values_column].sum().reset_index()
    
    fig = px.pie(
        pie_data,
        names=names_column,
        values=values_column,
        title=title
    )
    
    fig.update_layout(
        height=500
    )
    
    return fig

def create_heatmap(df, x_column, y_column, value_column, title=None):
    """
    Create a heatmap
    
    Parameters:
    - df: Pandas DataFrame
    - x_column: Column for x-axis
    - y_column: Column for y-axis
    - value_column: Column for cell values
    - title: Optional chart title
    
    Returns:
    - Plotly figure
    """
    if df is None or df.empty:
        return None
    
    if not title:
        title = f"Heatmap: {value_column} by {x_column} and {y_column}"
    
    # Create pivot table for heatmap
    pivot_data = df.pivot_table(
        index=y_column, 
        columns=x_column, 
        values=value_column,
        aggfunc='mean'
    )
    
    fig = px.imshow(
        pivot_data,
        labels=dict(x=x_column, y=y_column, color=value_column),
        x=pivot_data.columns,
        y=pivot_data.index,
        title=title,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        height=500
    )
    
    return fig

def create_box_plot(df, x_column, y_column, color=None, title=None):
    """
    Create a box plot
    
    Parameters:
    - df: Pandas DataFrame
    - x_column: Column for x-axis (categories)
    - y_column: Column for y-axis (values)
    - color: Optional column for coloring
    - title: Optional chart title
    
    Returns:
    - Plotly figure
    """
    if df is None or df.empty:
        return None
    
    if not title:
        title = f"Box Plot: {y_column} by {x_column}"
    
    fig = px.box(
        df,
        x=x_column,
        y=y_column,
        color=color,
        title=title,
        labels={
            x_column: x_column,
            y_column: y_column
        }
    )
    
    fig.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column,
        plot_bgcolor='white',
        height=500
    )
    
    return fig

def create_correlation_heatmap(df, columns=None, title=None):
    """
    Create a correlation heatmap
    
    Parameters:
    - df: Pandas DataFrame
    - columns: List of columns to include (None for all numeric)
    - title: Optional chart title
    
    Returns:
    - Plotly figure
    """
    if df is None or df.empty:
        return None
    
    # Select only numeric columns if not specified
    if columns is None:
        numeric_df = df.select_dtypes(include=[np.number])
    else:
        numeric_df = df[columns].select_dtypes(include=[np.number])
    
    if numeric_df.shape[1] < 2:
        return None
    
    # Calculate correlation matrix
    corr_matrix = numeric_df.corr()
    
    # Create heatmap
    if not title:
        title = "Correlation Heatmap"
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title=title
    )
    
    fig.update_layout(
        height=600,
        width=800
    )
    
    return fig
