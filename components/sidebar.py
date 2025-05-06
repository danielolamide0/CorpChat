import streamlit as st
import pandas as pd
from utils.data_loader import load_file, get_data_summary

def render_sidebar():
    """
    Render the sidebar with file upload and navigation controls
    """
    with st.sidebar:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("assets/app_logo.svg", width=60)
        with col2:
            st.markdown("<h2 style='margin-bottom:0; padding-bottom:0'>DataViz</h2>", unsafe_allow_html=True)
            st.markdown("<p style='margin-top:0; padding-top:0; color:#4F8BF9; font-size:14px'>ANALYTICS DASHBOARD</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Modern navigation menu with icons
        st.markdown("<h3>📊 Navigation</h3>", unsafe_allow_html=True)
        
        # File upload section with a modern design
        st.markdown("<h4 style='margin-top:20px'>📁 Data Source</h4>", unsafe_allow_html=True)
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
        st.markdown("<h4 style='margin-top:20px'>🧭 Menu</h4>", unsafe_allow_html=True)
        
        # Determine if tabs should be enabled
        tabs_enabled = st.session_state.data is not None
        
        # Create custom styled navigation buttons
        btn_style = """
        <style>
        div.stButton > button {
            width: 100%;
            height: 3em;
            border-radius: 10px;
            margin-bottom: 8px;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding-left: 15px;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        div.stButton > button:focus {
            border-left: 5px solid #4F8BF9;
        }
        </style>
        """
        st.markdown(btn_style, unsafe_allow_html=True)
        
        # Active tab indicator
        active_tab = st.session_state.current_tab
        
        # Upload & Preview button
        active_class = "background-color: #E8F0FE;" if active_tab == "Upload" else ""
        if st.button("📋 Upload & Preview", disabled=False, key="nav_upload"):
            st.session_state.current_tab = "Upload"
            st.rerun()
        
        # Analysis button
        active_class = "background-color: #E8F0FE;" if active_tab == "Analysis" else ""
        if st.button("📈 Analysis", disabled=not tabs_enabled, key="nav_analysis"):
            if tabs_enabled:
                st.session_state.current_tab = "Analysis"
                st.rerun()
            else:
                st.info("Please upload data first")
        
        # Visualization button
        active_class = "background-color: #E8F0FE;" if active_tab == "Visualization" else ""
        if st.button("📊 Visualization", disabled=not tabs_enabled, key="nav_visualization"):
            if tabs_enabled:
                st.session_state.current_tab = "Visualization"
                st.rerun()
            else:
                st.info("Please upload data first")
                
        # Business AI button
        active_class = "background-color: #E8F0FE;" if active_tab == "Chat Bot" else ""
        if st.button("🤖 Business AI", disabled=not tabs_enabled, key="nav_chatbot"):
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
