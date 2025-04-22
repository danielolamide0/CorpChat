import streamlit as st
import pandas as pd
import os
from components.sidebar import render_sidebar
from components.data_preview import render_data_preview
from components.analysis_section import render_analysis_section
from components.visualization_section import render_visualization_section
from utils.data_loader import load_sample_data, load_file, get_data_summary

# Page configuration
st.set_page_config(
    page_title="Data Analysis & Visualization Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing data and app state
if 'data' not in st.session_state:
    # Try to load the sample data if available
    sample_data_path = './assets/sample_data.csv'
    if os.path.exists(sample_data_path):
        try:
            st.session_state.data = pd.read_csv(sample_data_path)
            st.session_state.file_name = 'sample_data.csv'
        except Exception as e:
            st.error(f"Error loading sample data: {e}")
            st.session_state.data = None
    else:
        st.session_state.data = None

if 'file_name' not in st.session_state:
    st.session_state.file_name = 'sample_data.csv' if st.session_state.data is not None else None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Upload"
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'visualizations' not in st.session_state:
    st.session_state.visualizations = []
if 'data_summary' not in st.session_state and st.session_state.data is not None:
    st.session_state.data_summary = get_data_summary(st.session_state.data)

# Main app header
st.markdown("""
# 📊 Data Analysis & Visualization Dashboard
Upload your data, analyze patterns, and create insightful visualizations all in one place.
""")

# Render sidebar (file upload and navigation)
render_sidebar()

# Main content area based on selected tab
if st.session_state.current_tab == "Upload":
    if st.session_state.data is not None:
        render_data_preview()
    else:
        st.info("👆 Upload a CSV or Excel file using the sidebar to get started.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("What you can do with this app:")
            st.markdown("""
            - Upload CSV and Excel files
            - View and filter your data
            - Calculate basic statistics
            - Clean and transform your data
            - Create various visualizations
            - Customize your charts
            - Work with large datasets
            """)
            
        with col2:
            st.subheader("Supported visualizations:")
            st.markdown("""
            - Bar charts
            - Line charts
            - Scatter plots
            - Histograms
            - Pie charts
            - Heatmaps
            - Box plots
            - And more!
            """)
        
        st.markdown("---")
        st.subheader("File upload guidelines:")
        st.markdown("""
        - Supported formats: CSV (.csv) and Excel (.xlsx, .xls)
        - Maximum file size: 200MB
        - First row should contain column headers
        - For large files, consider using the sampling option
        """)

elif st.session_state.current_tab == "Analysis":
    if st.session_state.data is not None:
        render_analysis_section()
    else:
        st.warning("Please upload a file first to perform analysis.")
        
elif st.session_state.current_tab == "Visualization":
    if st.session_state.data is not None:
        render_visualization_section()
    else:
        st.warning("Please upload a file first to create visualizations.")

# Footer
st.markdown("---")
st.markdown("📊 Data Analysis & Visualization Dashboard | Built with Streamlit")
