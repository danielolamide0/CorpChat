import streamlit as st
import pandas as pd
import numpy as np
from utils.data_visualization import (
    create_bar_chart,
    create_line_chart,
    create_scatter_plot,
    create_histogram,
    create_pie_chart,
    create_heatmap,
    create_box_plot,
    create_correlation_heatmap
)
from utils.data_analysis import get_column_types

def render_visualization_section():
    """
    Render the data visualization section with various chart options
    """
    if st.session_state.data is None:
        st.warning("No data loaded yet. Please upload a file.")
        return
    
    st.markdown('<h1 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Data Visualization</h1>', unsafe_allow_html=True)
    
    # Get column types for better column selection suggestions
    column_types = get_column_types(st.session_state.data)
    
    # Initialize visualization list in session state if not present
    if "visualizations" not in st.session_state:
        st.session_state.visualizations = []
    
    # Visualization type selection
    viz_type = st.selectbox(
        "Select visualization type:",
        options=[
            "Bar Chart",
            "Line Chart",
            "Scatter Plot",
            "Histogram",
            "Pie Chart",
            "Heatmap",
            "Box Plot",
            "Correlation Matrix"
        ]
    )
    
    # Create visualization based on type
    with st.expander('<span style="color: white;">Visualization Configuration</span>', expanded=True):
        if viz_type == "Bar Chart":
            render_bar_chart_config(column_types)
        elif viz_type == "Line Chart":
            render_line_chart_config(column_types)
        elif viz_type == "Scatter Plot":
            render_scatter_plot_config(column_types)
        elif viz_type == "Histogram":
            render_histogram_config(column_types)
        elif viz_type == "Pie Chart":
            render_pie_chart_config(column_types)
        elif viz_type == "Heatmap":
            render_heatmap_config(column_types)
        elif viz_type == "Box Plot":
            render_box_plot_config(column_types)
        elif viz_type == "Correlation Matrix":
            render_correlation_matrix_config(column_types)
    
    # Display saved visualizations
    if st.session_state.visualizations:
        st.markdown('<h3 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Your Visualizations</h3>', unsafe_allow_html=True)
        
        for i, viz in enumerate(st.session_state.visualizations):
            with st.expander(f"Visualization {i+1}: {viz['title']}", expanded=i == 0):
                st.plotly_chart(viz['figure'], use_container_width=True, key=f"viz_{i}")
                
                # Button to remove visualization
                if st.button(f"Remove this visualization", key=f"remove_viz_{i}"):
                    st.session_state.visualizations.pop(i)
                    st.rerun()
    else:
        st.info("No visualizations created yet. Configure a visualization and click 'Create Visualization' to add one.")

def render_bar_chart_config(column_types):
    """
    Render configuration options for a bar chart
    
    Parameters:
    - column_types: Dictionary mapping column names to their types
    """
    st.markdown('<h3 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Bar Chart Configuration</h3>', unsafe_allow_html=True)
    
    # Get categorical columns for x-axis suggestions
    categorical_columns = [col for col, type_ in column_types.items() 
                          if type_ in ["categorical", "text"]]
    
    # Get numerical columns for y-axis suggestions
    numerical_columns = [col for col, type_ in column_types.items() 
                        if type_ in ["integer", "float"]]
    
    # X-axis selection
    x_column = st.selectbox(
        "X-axis (categories):",
        options=st.session_state.data.columns.tolist(),
        index=categorical_columns.index(categorical_columns[0]) if categorical_columns else 0
    )
    
    # Y-axis selection
    y_column = st.selectbox(
        "Y-axis (values):",
        options=st.session_state.data.columns.tolist(),
        index=numerical_columns.index(numerical_columns[0]) if numerical_columns else 0
    )
    
    # Color column selection (optional)
    color_column = st.selectbox(
        "Color by (optional):",
        options=["None"] + categorical_columns,
        index=0
    )
    
    # Convert "None" to None
    color_column = None if color_column == "None" else color_column
    
    # Chart orientation
    orientation = st.radio(
        "Bar orientation:",
        options=["vertical", "horizontal"],
        format_func=lambda x: "Vertical" if x == "vertical" else "Horizontal"
    )
    
    # Chart title
    chart_title = st.text_input(
        "Chart title:",
        value=f"Bar Chart: {y_column} by {x_column}"
    )
    
    # Create visualization button
    if st.button("Create Bar Chart"):
        with st.spinner("Creating visualization..."):
            # Create bar chart
            fig = create_bar_chart(
                st.session_state.data,
                x_column,
                y_column,
                color=color_column,
                title=chart_title,
                orientation="h" if orientation == "horizontal" else "v"
            )
            
            if fig is not None:
                # Store visualization in session state
                st.session_state.visualizations.append({
                    "type": "bar",
                    "title": chart_title,
                    "figure": fig
                })
                
                st.success("Bar chart created successfully!")
                st.rerun()
            else:
                st.error("Could not create bar chart with the selected columns")

def render_line_chart_config(column_types):
    """
    Render configuration options for a line chart
    
    Parameters:
    - column_types: Dictionary mapping column names to their types
    """
    st.markdown('<h3 style="color: white;">Line Chart Configuration</h3>', unsafe_allow_html=True)
    
    # Suggest datetime or numeric columns for x-axis
    x_axis_suggestions = [col for col, type_ in column_types.items() 
                         if type_ in ["datetime", "integer", "float"]]
    
    # X-axis selection
    x_column = st.selectbox(
        "X-axis (typically time or ordered variable):",
        options=st.session_state.data.columns.tolist(),
        index=st.session_state.data.columns.tolist().index(x_axis_suggestions[0]) if x_axis_suggestions else 0
    )
    
    # Get numerical columns for y-axis suggestions
    numerical_columns = [col for col, type_ in column_types.items() 
                        if type_ in ["integer", "float"]]
    
    # Y-axis selection (multiple)
    y_columns = st.multiselect(
        "Y-axis values (select one or more):",
        options=numerical_columns,
        default=[numerical_columns[0]] if numerical_columns else []
    )
    
    # Chart title
    chart_title = st.text_input(
        "Chart title:",
        value=f"Line Chart: {', '.join(y_columns)} over {x_column}" if y_columns else "Line Chart"
    )
    
    # Create visualization button
    if st.button("Create Line Chart"):
        # Validate selection
        if not y_columns:
            st.warning("Please select at least one Y-axis column")
            return
        
        with st.spinner("Creating visualization..."):
            # Create line chart
            fig = create_line_chart(
                st.session_state.data,
                x_column,
                y_columns,
                title=chart_title
            )
            
            if fig is not None:
                # Store visualization in session state
                st.session_state.visualizations.append({
                    "type": "line",
                    "title": chart_title,
                    "figure": fig
                })
                
                st.success("Line chart created successfully!")
                st.rerun()
            else:
                st.error("Could not create line chart with the selected columns")

def render_scatter_plot_config(column_types):
    """
    Render configuration options for a scatter plot
    
    Parameters:
    - column_types: Dictionary mapping column names to their types
    """
    st.subheader("Scatter Plot Configuration")
    
    # Get numerical columns for axis suggestions
    numerical_columns = [col for col, type_ in column_types.items() 
                        if type_ in ["integer", "float"]]
    
    # X-axis selection
    x_column = st.selectbox(
        "X-axis:",
        options=numerical_columns,
        index=0 if numerical_columns else 0
    )
    
    # Y-axis selection
    y_column = st.selectbox(
        "Y-axis:",
        options=numerical_columns,
        index=min(1, len(numerical_columns)-1) if len(numerical_columns) > 1 else 0
    )
    
    # Get categorical columns for color suggestions
    categorical_columns = [col for col, type_ in column_types.items() 
                          if type_ in ["categorical", "text"]]
    
    # Color column selection (optional)
    color_column = st.selectbox(
        "Color by (optional):",
        options=["None"] + categorical_columns,
        index=0
    )
    
    # Size column selection (optional)
    size_column = st.selectbox(
        "Size by (optional):",
        options=["None"] + numerical_columns,
        index=0
    )
    
    # Convert "None" to None
    color_column = None if color_column == "None" else color_column
    size_column = None if size_column == "None" else size_column
    
    # Chart title
    chart_title = st.text_input(
        "Chart title:",
        value=f"Scatter Plot: {y_column} vs {x_column}"
    )
    
    # Create visualization button
    if st.button("Create Scatter Plot"):
        with st.spinner("Creating visualization..."):
            # Create scatter plot
            fig = create_scatter_plot(
                st.session_state.data,
                x_column,
                y_column,
                color=color_column,
                size=size_column,
                title=chart_title
            )
            
            if fig is not None:
                # Store visualization in session state
                st.session_state.visualizations.append({
                    "type": "scatter",
                    "title": chart_title,
                    "figure": fig
                })
                
                st.success("Scatter plot created successfully!")
                st.rerun()
            else:
                st.error("Could not create scatter plot with the selected columns")

def render_histogram_config(column_types):
    """
    Render configuration options for a histogram
    
    Parameters:
    - column_types: Dictionary mapping column names to their types
    """
    st.subheader("Histogram Configuration")
    
    # Get numerical columns for histogram
    numerical_columns = [col for col, type_ in column_types.items() 
                        if type_ in ["integer", "float"]]
    
    if not numerical_columns:
        st.warning("No numerical columns found in the data")
        return
    
    # Column selection
    column = st.selectbox(
        "Select column:",
        options=numerical_columns,
        index=0
    )
    
    # Number of bins
    bins = st.slider(
        "Number of bins:",
        min_value=5,
        max_value=100,
        value=20,
        step=5
    )
    
    # Get categorical columns for color suggestions
    categorical_columns = [col for col, type_ in column_types.items() 
                          if type_ in ["categorical", "text"]]
    
    # Color column selection (optional)
    color_column = st.selectbox(
        "Color by (optional):",
        options=["None"] + categorical_columns,
        index=0
    )
    
    # Convert "None" to None
    color_column = None if color_column == "None" else color_column
    
    # Chart title
    chart_title = st.text_input(
        "Chart title:",
        value=f"Histogram: Distribution of {column}"
    )
    
    # Create visualization button
    if st.button("Create Histogram"):
        with st.spinner("Creating visualization..."):
            # Create histogram
            fig = create_histogram(
                st.session_state.data,
                column,
                bins=bins,
                title=chart_title,
                color=color_column
            )
            
            if fig is not None:
                # Store visualization in session state
                st.session_state.visualizations.append({
                    "type": "histogram",
                    "title": chart_title,
                    "figure": fig
                })
                
                st.success("Histogram created successfully!")
                st.rerun()
            else:
                st.error("Could not create histogram with the selected column")

def render_pie_chart_config(column_types):
    """
    Render configuration options for a pie chart
    
    Parameters:
    - column_types: Dictionary mapping column names to their types
    """
    st.subheader("Pie Chart Configuration")
    
    # Get categorical columns for segments
    categorical_columns = [col for col, type_ in column_types.items() 
                          if type_ in ["categorical", "text"]]
    
    # Names column selection
    names_column = st.selectbox(
        "Segments (categories):",
        options=categorical_columns,
        index=0 if categorical_columns else 0
    )
    
    # Get numerical columns for values
    numerical_columns = [col for col, type_ in column_types.items() 
                        if type_ in ["integer", "float"]]
    
    # Values column selection
    values_column = st.selectbox(
        "Values:",
        options=numerical_columns,
        index=0 if numerical_columns else 0
    )
    
    # Chart title
    chart_title = st.text_input(
        "Chart title:",
        value=f"Pie Chart: {values_column} by {names_column}"
    )
    
    # Create visualization button
    if st.button("Create Pie Chart"):
        with st.spinner("Creating visualization..."):
            # Create pie chart
            fig = create_pie_chart(
                st.session_state.data,
                names_column,
                values_column,
                title=chart_title
            )
            
            if fig is not None:
                # Store visualization in session state
                st.session_state.visualizations.append({
                    "type": "pie",
                    "title": chart_title,
                    "figure": fig
                })
                
                st.success("Pie chart created successfully!")
                st.rerun()
            else:
                st.error("Could not create pie chart with the selected columns")

def render_heatmap_config(column_types):
    """
    Render configuration options for a heatmap
    
    Parameters:
    - column_types: Dictionary mapping column names to their types
    """
    st.subheader("Heatmap Configuration")
    
    # Get categorical columns for x and y axes
    categorical_columns = [col for col, type_ in column_types.items() 
                          if type_ in ["categorical", "text"]]
    
    # X-axis selection
    x_column = st.selectbox(
        "X-axis (categories):",
        options=categorical_columns,
        index=0 if categorical_columns else 0
    )
    
    # Y-axis selection
    y_column = st.selectbox(
        "Y-axis (categories):",
        options=categorical_columns,
        index=min(1, len(categorical_columns)-1) if len(categorical_columns) > 1 else 0
    )
    
    # Get numerical columns for values
    numerical_columns = [col for col, type_ in column_types.items() 
                        if type_ in ["integer", "float"]]
    
    # Value column selection
    value_column = st.selectbox(
        "Values:",
        options=numerical_columns,
        index=0 if numerical_columns else 0
    )
    
    # Chart title
    chart_title = st.text_input(
        "Chart title:",
        value=f"Heatmap: {value_column} by {x_column} and {y_column}"
    )
    
    # Create visualization button
    if st.button("Create Heatmap"):
        # Validate selections
        if x_column == y_column:
            st.warning("Please select different columns for X and Y axes")
            return
        
        with st.spinner("Creating visualization..."):
            # Create heatmap
            fig = create_heatmap(
                st.session_state.data,
                x_column,
                y_column,
                value_column,
                title=chart_title
            )
            
            if fig is not None:
                # Store visualization in session state
                st.session_state.visualizations.append({
                    "type": "heatmap",
                    "title": chart_title,
                    "figure": fig
                })
                
                st.success("Heatmap created successfully!")
                st.rerun()
            else:
                st.error("Could not create heatmap with the selected columns")

def render_box_plot_config(column_types):
    """
    Render configuration options for a box plot
    
    Parameters:
    - column_types: Dictionary mapping column names to their types
    """
    st.subheader("Box Plot Configuration")
    
    # Get categorical columns for x-axis
    categorical_columns = [col for col, type_ in column_types.items() 
                          if type_ in ["categorical", "text"]]
    
    # X-axis selection
    x_column = st.selectbox(
        "X-axis (categories):",
        options=categorical_columns,
        index=0 if categorical_columns else 0
    )
    
    # Get numerical columns for y-axis
    numerical_columns = [col for col, type_ in column_types.items() 
                        if type_ in ["integer", "float"]]
    
    # Y-axis selection
    y_column = st.selectbox(
        "Y-axis (values):",
        options=numerical_columns,
        index=0 if numerical_columns else 0
    )
    
    # Color column selection (optional)
    color_column = st.selectbox(
        "Color by (optional):",
        options=["None"] + categorical_columns,
        index=0
    )
    
    # Convert "None" to None
    color_column = None if color_column == "None" else color_column
    
    # Chart title
    chart_title = st.text_input(
        "Chart title:",
        value=f"Box Plot: {y_column} by {x_column}"
    )
    
    # Create visualization button
    if st.button("Create Box Plot"):
        with st.spinner("Creating visualization..."):
            # Create box plot
            fig = create_box_plot(
                st.session_state.data,
                x_column,
                y_column,
                color=color_column,
                title=chart_title
            )
            
            if fig is not None:
                # Store visualization in session state
                st.session_state.visualizations.append({
                    "type": "box",
                    "title": chart_title,
                    "figure": fig
                })
                
                st.success("Box plot created successfully!")
                st.rerun()
            else:
                st.error("Could not create box plot with the selected columns")

def render_correlation_matrix_config(column_types):
    """
    Render configuration options for a correlation matrix
    
    Parameters:
    - column_types: Dictionary mapping column names to their types
    """
    st.subheader("Correlation Matrix Configuration")
    
    # Get numerical columns for correlation
    numerical_columns = [col for col, type_ in column_types.items() 
                        if type_ in ["integer", "float"]]
    
    if len(numerical_columns) < 2:
        st.warning("Need at least 2 numerical columns to create a correlation matrix")
        return
    
    # Column selection (multiple)
    selected_columns = st.multiselect(
        "Select columns to include:",
        options=numerical_columns,
        default=numerical_columns[:5] if len(numerical_columns) > 5 else numerical_columns
    )
    
    # Chart title
    chart_title = st.text_input(
        "Chart title:",
        value="Correlation Matrix"
    )
    
    # Create visualization button
    if st.button("Create Correlation Matrix"):
        # Validate selection
        if len(selected_columns) < 2:
            st.warning("Please select at least 2 columns")
            return
        
        with st.spinner("Creating visualization..."):
            # Create correlation matrix
            fig = create_correlation_heatmap(
                st.session_state.data,
                columns=selected_columns,
                title=chart_title
            )
            
            if fig is not None:
                # Store visualization in session state
                st.session_state.visualizations.append({
                    "type": "correlation",
                    "title": chart_title,
                    "figure": fig
                })
                
                st.success("Correlation matrix created successfully!")
                st.rerun()
            else:
                st.error("Could not create correlation matrix with the selected columns")
