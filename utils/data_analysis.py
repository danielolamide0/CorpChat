import pandas as pd
import numpy as np
import streamlit as st

def calculate_basic_stats(df, columns=None):
    """
    Calculate basic statistics for selected columns
    
    Parameters:
    - df: Pandas DataFrame
    - columns: List of columns to analyze (None for all numeric columns)
    
    Returns:
    - DataFrame with basic statistics
    """
    if df is None or df.empty:
        return None
    
    # If no columns specified, use all numeric columns
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Filter to only include numeric columns from the selection
    numeric_columns = [col for col in columns if pd.api.types.is_numeric_dtype(df[col])]
    
    if not numeric_columns:
        return pd.DataFrame({
            "Message": ["No numeric columns selected for analysis"]
        })
    
    # Calculate statistics
    stats = {}
    for col in numeric_columns:
        col_stats = {
            "Mean": df[col].mean(),
            "Median": df[col].median(),
            "Std Dev": df[col].std(),
            "Min": df[col].min(),
            "Max": df[col].max(),
            "25%": df[col].quantile(0.25),
            "75%": df[col].quantile(0.75),
            "Count": df[col].count(),
            "Missing": df[col].isna().sum()
        }
        stats[col] = col_stats
    
    return pd.DataFrame(stats)

def get_column_types(df):
    """
    Get the data types of columns in a DataFrame
    
    Parameters:
    - df: Pandas DataFrame
    
    Returns:
    - Dictionary mapping column names to their general types
    """
    if df is None or df.empty:
        return {}
    
    types = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].dropna().apply(lambda x: x == int(x)).all():
                types[col] = "integer"
            else:
                types[col] = "float"
        elif pd.api.types.is_datetime64_dtype(df[col]):
            types[col] = "datetime"
        elif df[col].nunique() < 10:
            types[col] = "categorical"
        else:
            types[col] = "text"
    
    return types

def clean_data(df, options):
    """
    Clean data based on selected options
    
    Parameters:
    - df: Pandas DataFrame
    - options: Dictionary of cleaning options
    
    Returns:
    - Cleaned DataFrame
    """
    if df is None or df.empty:
        return None
    
    # Create a copy to avoid modifying the original
    cleaned_df = df.copy()
    
    # Handle missing values
    if options.get('handle_missing'):
        missing_strategy = options.get('missing_strategy', 'drop')
        
        if missing_strategy == 'drop':
            cleaned_df = cleaned_df.dropna()
        elif missing_strategy == 'fill_mean':
            for col in cleaned_df.select_dtypes(include=[np.number]).columns:
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
        elif missing_strategy == 'fill_median':
            for col in cleaned_df.select_dtypes(include=[np.number]).columns:
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
        elif missing_strategy == 'fill_mode':
            for col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else None)
        elif missing_strategy == 'fill_zero':
            cleaned_df = cleaned_df.fillna(0)
    
    # Remove duplicates
    if options.get('remove_duplicates'):
        cleaned_df = cleaned_df.drop_duplicates()
    
    # Convert columns to datetime
    if options.get('datetime_columns'):
        for col in options['datetime_columns']:
            try:
                cleaned_df[col] = pd.to_datetime(cleaned_df[col])
            except:
                pass
    
    return cleaned_df

def filter_data(df, filters):
    """
    Filter data based on specified conditions
    
    Parameters:
    - df: Pandas DataFrame
    - filters: List of dictionaries with filter conditions
    
    Returns:
    - Filtered DataFrame
    """
    if df is None or df.empty or not filters:
        return df
    
    filtered_df = df.copy()
    
    for filter_item in filters:
        column = filter_item.get('column')
        operator = filter_item.get('operator')
        value = filter_item.get('value')
        
        if not column or not operator or value is None:
            continue
        
        # Apply filter based on operator
        if operator == 'equals':
            filtered_df = filtered_df[filtered_df[column] == value]
        elif operator == 'not_equals':
            filtered_df = filtered_df[filtered_df[column] != value]
        elif operator == 'greater_than':
            filtered_df = filtered_df[filtered_df[column] > value]
        elif operator == 'less_than':
            filtered_df = filtered_df[filtered_df[column] < value]
        elif operator == 'contains':
            filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(value), na=False)]
        elif operator == 'starts_with':
            filtered_df = filtered_df[filtered_df[column].astype(str).str.startswith(str(value), na=False)]
        elif operator == 'ends_with':
            filtered_df = filtered_df[filtered_df[column].astype(str).str.endswith(str(value), na=False)]
        elif operator == 'in_range':
            if isinstance(value, (list, tuple)) and len(value) == 2:
                filtered_df = filtered_df[(filtered_df[column] >= value[0]) & (filtered_df[column] <= value[1])]
    
    return filtered_df

def get_categorical_distribution(df, column):
    """
    Get the distribution of values in a categorical column
    
    Parameters:
    - df: Pandas DataFrame
    - column: Column name
    
    Returns:
    - DataFrame with value counts
    """
    if df is None or df.empty or column not in df.columns:
        return None
    
    # Get value counts and convert to DataFrame
    distribution = df[column].value_counts().reset_index()
    distribution.columns = [column, 'Count']
    
    # Calculate percentage
    distribution['Percentage'] = (distribution['Count'] / distribution['Count'].sum() * 100).round(2)
    
    return distribution

def get_numeric_distribution(df, column, bins=10):
    """
    Get the distribution of values in a numeric column
    
    Parameters:
    - df: Pandas DataFrame
    - column: Column name
    - bins: Number of bins for histogram
    
    Returns:
    - Tuple of (bin_edges, counts)
    """
    if df is None or df.empty or column not in df.columns:
        return None, None
    
    if not pd.api.types.is_numeric_dtype(df[column]):
        return None, None
    
    counts, bin_edges = np.histogram(df[column].dropna(), bins=bins)
    
    # Create bin labels
    bin_labels = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)]
    
    return bin_labels, counts
