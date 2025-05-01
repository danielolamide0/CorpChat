import streamlit as st
import pandas as pd
from utils.data_loader import load_file, get_data_summary

def render_sidebar():
    """
    Render the sidebar with file upload and navigation controls
    """
    with st.sidebar:
        st.image("assets/app_logo.svg", width=50)
        st.title("CorpChat Analytics")
        st.caption("by SynaptideAI")
        st.title("Navigation")
        
        # File upload section
        st.header("Data Source")
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            help="Upload your data file to start analysis (max 200MB)"
        )
        
        # Sampling option for large files
        sample_size = None
        if uploaded_file is not None:
            st.write("File options:")
            use_sampling = st.checkbox("Sample data (for large files)", value=False)
            if use_sampling:
                sample_size = st.number_input(
                    "Number of rows to sample",
                    min_value=100,
                    max_value=100000,
                    value=1000,
                    step=100
                )
        
        # Load data button
        if uploaded_file is not None:
            if st.button("Load Data"):
                with st.spinner("Loading data..."):
                    # Load the data
                    df = load_file(uploaded_file, sample_size)
                    
                    if df is not None:
                        # Store in session state
                        st.session_state.data = df
                        st.session_state.file_name = uploaded_file.name
                        
                        # Show success message with data summary
                        summary = get_data_summary(df)
                        st.success(f"Data loaded successfully: {summary['rows']} rows, {summary['columns']} columns")
                        
                        # Automatically switch to data view
                        st.session_state.current_tab = "Upload"
                        st.rerun()
        
        # Navigation tabs (only enabled when data is loaded)
        st.header("Menu")
        
        # Determine if tabs should be enabled
        tabs_enabled = st.session_state.data is not None
        
        # Navigation buttons
        if st.button("Upload & Preview", disabled=False, key="nav_upload"):
            st.session_state.current_tab = "Upload"
            st.rerun()
        
        if st.button("Analysis", disabled=not tabs_enabled, key="nav_analysis"):
            if tabs_enabled:
                st.session_state.current_tab = "Analysis"
                st.rerun()
            else:
                st.info("Please upload data first")
        
        if st.button("Visualization", disabled=not tabs_enabled, key="nav_visualization"):
            if tabs_enabled:
                st.session_state.current_tab = "Visualization"
                st.rerun()
            else:
                st.info("Please upload data first")
                
        if st.button("Business AI", disabled=not tabs_enabled, key="nav_chatbot"):
            if tabs_enabled:
                st.session_state.current_tab = "Chat Bot"
                st.rerun()
            else:
                st.info("Please upload data first")
        
        # Reset application
        st.markdown("---")
        if st.button("Reset Application", key="reset_app"):
            # Clear session state
            st.session_state.data = None
            st.session_state.file_name = None
            st.session_state.current_tab = "Upload"
            st.session_state.analysis_results = {}
            st.session_state.visualizations = []
            if "messages" in st.session_state:
                st.session_state.messages = []
            if "system_message_added" in st.session_state:
                del st.session_state.system_message_added
            st.rerun()
        
        # Display current data source info
        if st.session_state.data is not None:
            st.markdown("---")
            st.subheader("Current Data Source")
            st.info(f"File: {st.session_state.file_name}")
            
            # Get data summary
            summary = get_data_summary(st.session_state.data)
            
            # Display data stats
            st.markdown(f"**Rows:** {summary['rows']}")
            st.markdown(f"**Columns:** {summary['columns']}")
            st.markdown(f"**Missing Values:** {summary['missing_values']}")
            st.markdown(f"**Memory Usage:** {summary['memory_usage']:.2f} MB")
