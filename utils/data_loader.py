import streamlit as st
import pandas as pd
import numpy as np
import io

def load_file(uploaded_file, sample_size=None):
    """
    Load data from an uploaded file (CSV or Excel)
    
    Parameters:
    - uploaded_file: The uploaded file object
    - sample_size: Optional number of rows to sample
    
    Returns:
    - DataFrame with the loaded data
    """
    file_name = uploaded_file.name
    file_extension = file_name.split('.')[-1].lower()
    
    try:
        # Process based on file extension
        if file_extension == 'csv':
            data = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            data = pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file format: {file_extension}. Please upload a CSV or Excel file.")
            return None
        
        # Sample data if specified
        if sample_size and sample_size < len(data):
            data = data.sample(n=sample_size, random_state=42)
        
        return data
    
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def load_sample_data():
    """
    Create an empty DataFrame as a placeholder
    
    Returns:
    - Empty DataFrame with sample columns
    """
    # Empty dataframe with typical columns
    df = pd.DataFrame(columns=['ID', 'Date', 'Category', 'Value', 'Region'])
    return df

def get_data_summary(df):
    """
    Get a basic summary of the dataframe
    
    Parameters:
    - df: Pandas DataFrame
    
    Returns:
    - Dictionary with summary information
    """
    if df is None or df.empty:
        return None
    
    summary = {
        'rows': len(df),
        'columns': len(df.columns),
        'column_types': df.dtypes.value_counts().to_dict(),
        'missing_values': df.isna().sum().sum(),
        'memory_usage': df.memory_usage(deep=True).sum() / (1024 * 1024),  # in MB
    }
    
    return summary

def validate_dataframe(df):
    """
    Validate that the dataframe is properly formatted
    
    Parameters:
    - df: Pandas DataFrame
    
    Returns:
    - Boolean indicating if the dataframe is valid
    - Error message if invalid
    """
    if df is None:
        return False, "No data loaded"
    
    if df.empty:
        return False, "Dataframe is empty"
    
    if df.columns.duplicated().any():
        return False, "Dataframe contains duplicate column names"
    
    # Check if all columns are valid (no null columns)
    if any(pd.isna(col) for col in df.columns):
        return False, "Dataframe contains null column names"
    
    return True, ""
