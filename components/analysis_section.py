import streamlit as st
import pandas as pd
import numpy as np
from utils.data_analysis import (
    calculate_basic_stats, 
    clean_data, 
    filter_data, 
    get_column_types,
    get_categorical_distribution,
    get_numeric_distribution
)

def render_analysis_section():
    """
    Render the data analysis section with various analysis options
    """
    if st.session_state.data is None:
        st.warning("No data loaded yet. Please upload a file.")
        return
    
    st.markdown('<h1 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Data Analysis</h1>', unsafe_allow_html=True)
    
    # Create tabs for different analysis features
    tab1, tab2, tab3, tab4 = st.tabs([
        "Basic Statistics", 
        "Data Cleaning", 
        "Filtering", 
        "Distribution Analysis"
    ])
    
    # Tab 1: Basic Statistics
    with tab1:
        render_basic_statistics()
    
    # Tab 2: Data Cleaning
    with tab2:
        render_data_cleaning()
    
    # Tab 3: Filtering
    with tab3:
        render_data_filtering()
    
    # Tab 4: Distribution Analysis
    with tab4:
        render_distribution_analysis()

def render_basic_statistics():
    """
    Render the basic statistics analysis section
    """
    st.markdown('<h3 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Basic Statistics</h3>', unsafe_allow_html=True)
    
    # Get column types to suggest appropriate columns
    column_types = get_column_types(st.session_state.data)
    numeric_columns = [col for col, type_ in column_types.items() if type_ in ["integer", "float"]]
    
    # Let user select columns for analysis
    selected_columns = st.multiselect(
        "Select columns for statistical analysis:",
        options=st.session_state.data.columns.tolist(),
        default=numeric_columns[:5] if len(numeric_columns) >= 5 else numeric_columns,
        help="Select numeric columns for statistical analysis"
    )
    
    if not selected_columns:
        st.info("Please select at least one column for analysis")
        return
    
    # Calculate and display statistics
    stats_df = calculate_basic_stats(st.session_state.data, selected_columns)
    
    if stats_df is not None:
        # Check if we got a message instead of actual stats
        if "Message" in stats_df.columns:
            st.warning(stats_df["Message"][0])
        else:
            st.write("Statistical summary:")
            st.dataframe(stats_df, use_container_width=True)
            
            # Store in session state for later use
            st.session_state.analysis_results["basic_stats"] = stats_df
    else:
        st.error("Could not calculate statistics for the selected columns")

def render_data_cleaning():
    """
    Render the data cleaning section
    """
    st.markdown('<h3 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Data Cleaning</h3>', unsafe_allow_html=True)
    
    # Data cleaning options
    st.write("Select data cleaning options:")
    
    # Handle missing values
    handle_missing = st.checkbox("Handle missing values", value=True)
    missing_strategy = None
    
    if handle_missing:
        missing_strategy = st.radio(
            "Choose strategy for missing values:",
            options=["drop", "fill_mean", "fill_median", "fill_mode", "fill_zero"],
            format_func=lambda x: {
                "drop": "Drop rows with missing values",
                "fill_mean": "Fill with mean (numeric columns)",
                "fill_median": "Fill with median (numeric columns)",
                "fill_mode": "Fill with mode (most frequent value)",
                "fill_zero": "Fill with zeros"
            }.get(x, x),
            help="Choose how to handle missing values in your dataset"
        )
    
    # Remove duplicates
    remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
    
    # Convert datetime columns
    datetime_conversion = st.checkbox("Convert columns to datetime format", value=False)
    datetime_columns = []
    
    if datetime_conversion:
        datetime_columns = st.multiselect(
            "Select columns to convert to datetime:",
            options=st.session_state.data.columns.tolist(),
            help="Select columns that contain date or time information"
        )
    
    # Clean data button
    if st.button("Clean Data"):
        # Create cleaning options dictionary
        cleaning_options = {
            "handle_missing": handle_missing,
            "missing_strategy": missing_strategy,
            "remove_duplicates": remove_duplicates,
            "datetime_columns": datetime_columns
        }
        
        # Perform data cleaning
        with st.spinner("Cleaning data..."):
            cleaned_data = clean_data(st.session_state.data, cleaning_options)
            
            if cleaned_data is not None:
                # Compare original and cleaned data
                original_shape = st.session_state.data.shape
                cleaned_shape = cleaned_data.shape
                
                st.success(f"Data cleaned successfully!")
                
                # Display comparison
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Original rows", original_shape[0])
                with col2:
                    st.metric(
                        "Rows after cleaning", 
                        cleaned_shape[0], 
                        delta=cleaned_shape[0] - original_shape[0]
                    )
                
                # Display preview of cleaned data
                st.subheader("Preview of Cleaned Data")
                st.dataframe(cleaned_data.head(10), use_container_width=True)
                
                # Option to replace original data
                if st.button("Replace Original Data with Cleaned Data"):
                    st.session_state.data = cleaned_data
                    st.success("Original data replaced with cleaned data")
                    st.rerun()
                
                # Store cleaned data in session state
                st.session_state.analysis_results["cleaned_data"] = cleaned_data
            else:
                st.error("Error cleaning data")

def render_data_filtering():
    """
    Render the data filtering section
    """
    st.markdown('<h3 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Data Filtering</h3>', unsafe_allow_html=True)
    
    # Initialize filters in session state if not present
    if "filters" not in st.session_state:
        st.session_state.filters = []
    
    # Add new filter interface
    st.write("Add a new filter:")
    
    # Create columns for filter inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_column = st.selectbox(
            "Select column",
            options=st.session_state.data.columns.tolist(),
            key="filter_column"
        )
    
    with col2:
        # Determine appropriate operators based on column type
        column_types = get_column_types(st.session_state.data)
        column_type = column_types.get(filter_column, "text")
        
        if column_type in ["integer", "float"]:
            operators = ["equals", "not_equals", "greater_than", "less_than", "in_range"]
        elif column_type == "datetime":
            operators = ["equals", "not_equals", "greater_than", "less_than", "in_range"]
        else:
            operators = ["equals", "not_equals", "contains", "starts_with", "ends_with"]
        
        filter_operator = st.selectbox(
            "Select operator",
            options=operators,
            format_func=lambda x: {
                "equals": "Equals (=)",
                "not_equals": "Not equals (≠)",
                "greater_than": "Greater than (>)",
                "less_than": "Less than (<)",
                "in_range": "In range",
                "contains": "Contains",
                "starts_with": "Starts with",
                "ends_with": "Ends with"
            }.get(x, x),
            key="filter_operator"
        )
    
    with col3:
        # Value input based on operator and column type
        if filter_operator == "in_range":
            # For range, we need two values
            min_val, max_val = get_min_max_values(st.session_state.data, filter_column)
            
            filter_value_min = st.number_input(
                "Minimum value",
                value=min_val,
                key="filter_value_min"
            )
            
            filter_value_max = st.number_input(
                "Maximum value",
                value=max_val,
                key="filter_value_max"
            )
            
            filter_value = [filter_value_min, filter_value_max]
        else:
            # For single value operators
            if column_type in ["integer", "float"]:
                filter_value = st.number_input(
                    "Enter value",
                    value=0,
                    key="filter_value"
                )
            elif column_type == "datetime":
                filter_value = st.date_input(
                    "Enter date",
                    key="filter_value"
                )
            elif column_type == "categorical":
                # For categorical, show a dropdown of unique values
                unique_values = st.session_state.data[filter_column].dropna().unique().tolist()
                filter_value = st.selectbox(
                    "Select value",
                    options=unique_values,
                    key="filter_value"
                )
            else:
                # For text, show a text input
                filter_value = st.text_input(
                    "Enter value",
                    key="filter_value"
                )
    
    # Add filter button
    if st.button("Add Filter"):
        # Create filter dictionary
        new_filter = {
            "column": filter_column,
            "operator": filter_operator,
            "value": filter_value
        }
        
        # Add to session state
        st.session_state.filters.append(new_filter)
        st.success(f"Filter added: {filter_column} {filter_operator} {filter_value}")
        st.rerun()
    
    # Display current filters
    if st.session_state.filters:
        st.subheader("Current Filters")
        
        for i, f in enumerate(st.session_state.filters):
            col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
            
            with col1:
                st.write(f"Column: {f['column']}")
            
            with col2:
                st.write(f"Operator: {f['operator']}")
            
            with col3:
                st.write(f"Value: {f['value']}")
            
            with col4:
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.filters.pop(i)
                    st.rerun()
        
        # Apply filters button
        if st.button("Apply Filters"):
            # Filter the data
            filtered_data = filter_data(st.session_state.data, st.session_state.filters)
            
            # Show results
            if filtered_data is not None:
                original_rows = len(st.session_state.data)
                filtered_rows = len(filtered_data)
                
                st.success(f"Filters applied: {filtered_rows} rows match the criteria (out of {original_rows})")
                
                # Display filtered data
                st.subheader("Filtered Data Preview")
                st.dataframe(filtered_data.head(10), use_container_width=True)
                
                # Store filtered data in session state
                st.session_state.analysis_results["filtered_data"] = filtered_data
                
                # Option to export filtered data
                if st.button("Replace Original Data with Filtered Data"):
                    st.session_state.data = filtered_data
                    st.success("Original data replaced with filtered data")
                    st.session_state.filters = []  # Clear filters
                    st.rerun()
            else:
                st.error("Error applying filters")
        
        # Clear all filters
        if st.button("Clear All Filters"):
            st.session_state.filters = []
            st.rerun()
    else:
        st.info("No filters added yet")

def render_distribution_analysis():
    """
    Render the distribution analysis section
    """
    st.markdown('<h3 style="color: white;">Distribution Analysis</h3>', unsafe_allow_html=True)
    
    # Get column types
    column_types = get_column_types(st.session_state.data)
    
    # Create two tabs for categorical and numerical distributions
    dist_tab1, dist_tab2 = st.tabs(["Categorical Distributions", "Numerical Distributions"])
    
    # Tab 1: Categorical distributions
    with dist_tab1:
        # Get categorical columns
        categorical_columns = [col for col, type_ in column_types.items() 
                              if type_ in ["categorical", "text"]]
        
        if not categorical_columns:
            st.info("No categorical columns detected in the dataset")
        else:
            # Let user select a categorical column
            cat_column = st.selectbox(
                "Select a categorical column:",
                options=categorical_columns,
                key="cat_distribution_column"
            )
            
            # Get and display distribution
            if st.button("Calculate Distribution", key="calc_cat_dist"):
                with st.spinner("Calculating distribution..."):
                    distribution = get_categorical_distribution(st.session_state.data, cat_column)
                    
                    if distribution is not None:
                        st.write(f"Distribution of values in '{cat_column}':")
                        st.dataframe(distribution, use_container_width=True)
                        
                        # Store in session state
                        st.session_state.analysis_results[f"distribution_{cat_column}"] = distribution
                    else:
                        st.error("Could not calculate distribution")
    
    # Tab 2: Numerical distributions
    with dist_tab2:
        # Get numerical columns
        numerical_columns = [col for col, type_ in column_types.items() 
                            if type_ in ["integer", "float"]]
        
        if not numerical_columns:
            st.info("No numerical columns detected in the dataset")
        else:
            # Let user select a numerical column
            num_column = st.selectbox(
                "Select a numerical column:",
                options=numerical_columns,
                key="num_distribution_column"
            )
            
            # Let user specify number of bins
            num_bins = st.slider(
                "Number of bins:",
                min_value=5,
                max_value=50,
                value=10,
                step=1,
                key="num_distribution_bins"
            )
            
            # Get and display distribution
            if st.button("Calculate Distribution", key="calc_num_dist"):
                with st.spinner("Calculating distribution..."):
                    bin_labels, counts = get_numeric_distribution(
                        st.session_state.data, 
                        num_column,
                        bins=num_bins
                    )
                    
                    if bin_labels is not None and counts is not None:
                        # Create dataframe for display
                        distribution_df = pd.DataFrame({
                            "Bin Range": bin_labels,
                            "Count": counts
                        })
                        
                        st.write(f"Distribution of values in '{num_column}':")
                        st.dataframe(distribution_df, use_container_width=True)
                        
                        # Store in session state
                        st.session_state.analysis_results[f"distribution_{num_column}"] = {
                            "bin_labels": bin_labels,
                            "counts": counts
                        }
                    else:
                        st.error("Could not calculate distribution")

def get_min_max_values(df, column):
    """
    Get minimum and maximum values for a column in the dataframe
    
    Parameters:
    - df: Pandas DataFrame
    - column: Column name
    
    Returns:
    - Tuple of (min_value, max_value)
    """
    try:
        min_val = float(df[column].min())
        max_val = float(df[column].max())
        return min_val, max_val
    except:
        return 0, 100  # Default range if column is not numeric
