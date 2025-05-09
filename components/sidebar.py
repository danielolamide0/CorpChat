import streamlit as st
import pandas as pd
import base64
from utils.data_loader import load_file, get_data_summary

# Function to convert image to base64 for embedding in CSS
def get_base64_of_file(file_path):
    """Convert file to base64 encoded string for embedding in HTML/CSS"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Error loading file {file_path}: {e}")
        return ""

def render_sidebar():
    """
    Render the sidebar with file upload and navigation controls
    """
    # Get current theme from session state
    theme = st.session_state.get('theme', 'light')
    
    with st.sidebar:
        # Logo and branding with CorpChat Analytics and Synaptide AI - theme aware
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <img src="data:image/jpeg;base64,{get_base64_of_file("assets/synaptide_logo.jpeg")}" width="40" height="40" style="border-radius: 4px;">
            <div>
                <h2 style="margin: 0; padding: 0; font-size: 1.4rem; font-weight: 600; color: {f'#ffffff' if theme == 'dark' else '#242424'}; font-family: 'Space Grotesk', sans-serif;">CorpChat</h2>
                <p style="margin: 0; padding: 0; font-size: 0.8rem; color: {f'#e0e0e0' if theme == 'dark' else '#474747'}; letter-spacing: 0.05em; font-family: 'Space Grotesk', sans-serif;">POWERED BY SYNAPTIDE AI</p>
            </div>
        </div>
        <hr style="margin: 0 0 20px 0; padding: 0; border-color: {f'#4a4a4a' if theme == 'dark' else '#E0E0E0'};">
        """, unsafe_allow_html=True)
        
        # Modern File Upload Section - theme aware
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h3 style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; color: {f'#ffffff' if theme == 'dark' else '#333333'}; margin-bottom: 12px; font-family: 'Space Grotesk', sans-serif;">
                DATA SOURCE
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize saved files in session state if not already there
        if "saved_files" not in st.session_state:
            st.session_state.saved_files = []
        
        # Initialize the flag for the save file dialog
        if "show_save_dialog" not in st.session_state:
            st.session_state.show_save_dialog = False
            
        # File upload section
        uploaded_file = st.file_uploader(
            "Upload your dataset",
            type=["csv", "xlsx", "xls"],
            help="Upload your data file to start analysis (max 200MB)"
        )
        
        # Add a custom file upload container with a clear color scheme for dark mode
        theme = 'dark' if st.session_state.get('dark_mode', False) else 'light'
        
        # Create a custom styled file upload label - ensure it's visible in both themes
        st.markdown(f"""
        <style>
        /* Target file upload without affecting other components */
        div[data-testid="stFileUploader"] div[data-testid="stFileUploadDropzone"] div,
        div[data-testid="stFileUploader"] div[data-testid="stFileUploadDropzone"] p,
        div[data-testid="stFileUploader"] div[data-testid="stFileUploadDropzone"] span {
            color: {f'#ffffff !important' if theme == 'dark' else '#242424 !important'};
            font-weight: 500;
        }
        
        /* Make the background brighter in dark mode */
        div[data-testid="stFileUploader"] div[data-testid="stFileUploadDropzone"] {
            background-color: {f'#555555 !important' if theme == 'dark' else '#f5f5f5 !important'};
            border: 2px dashed {f'#999999' if theme == 'dark' else '#e0e0e0'};
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Saved Files dropdown - modernized with delete option - theme aware
        st.markdown(f"""
        <div style="margin-top: 10px; margin-bottom: 10px;">
            <h4 style="font-size: 0.9rem; color: {f'#ffffff' if theme == 'dark' else '#333333'}; font-family: 'Space Grotesk', sans-serif;">Saved Files</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Display saved files if any exist
        if len(st.session_state.saved_files) > 0:
            # Create columns for the dropdown and delete button
            file_names = [file["name"] for file in st.session_state.saved_files]
            selected_file = st.selectbox(
                "Select a saved file",
                options=file_names,
                key="saved_file_selector"
            )
            
            # Display load and delete buttons side by side
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Load File", key="load_saved_file", use_container_width=True):
                    # Find the selected file in the saved files
                    for saved_file in st.session_state.saved_files:
                        if saved_file["name"] == selected_file:
                            # Load the data
                            with st.spinner("Loading saved file..."):
                                df = saved_file["data"]
                                
                                # Store in session state
                                st.session_state.data = df
                                st.session_state.file_name = saved_file["name"]
                                
                                # Show success message with data summary
                                summary = get_data_summary(df)
                                if summary:
                                    st.success(f"Loaded: {summary['rows']} rows, {summary['columns']} columns")
                                else:
                                    st.success(f"File loaded successfully")
                                
                                # Automatically switch to data view
                                st.session_state.current_tab = "Upload"
                                st.rerun()
            
            with col2:
                if st.button("Delete", key="delete_saved_file", use_container_width=True):
                    # Find and remove the selected file
                    for i, saved_file in enumerate(st.session_state.saved_files):
                        if saved_file["name"] == selected_file:
                            del st.session_state.saved_files[i]
                            st.success(f"Deleted: {selected_file}")
                            st.rerun()
                            break
        else:
            st.markdown(f'<p style="color: {f"#aaaaaa" if theme == "dark" else "#666"}; font-size: 0.9rem; font-family: \'Space Grotesk\', sans-serif;">No saved files yet. Upload a file to begin.</p>', unsafe_allow_html=True)
        
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
        
        # Load data button - includes automatic save dialog
        if uploaded_file is not None:
            if st.button("Load Data", key="load_uploaded_file"):
                with st.spinner("Loading data..."):
                    # Load the data
                    df = load_file(uploaded_file, sample_size)
                    
                    if df is not None:
                        # Store in session state
                        st.session_state.data = df
                        st.session_state.file_name = uploaded_file.name
                        
                        # Show success message with data summary
                        summary = get_data_summary(df)
                        if summary:
                            st.success(f"Data loaded successfully: {summary['rows']} rows, {summary['columns']} columns")
                        else:
                            st.success(f"Data loaded successfully")
                        
                        # Set flag to show save dialog
                        st.session_state.show_save_dialog = True
                        
                        # Automatically switch to data view
                        st.session_state.current_tab = "Upload"
                        st.rerun()
        
        # Navigation tabs (only enabled when data is loaded) - theme aware
        st.markdown(f"<h4 style='margin-top:20px; color: {f'#ffffff' if theme == 'dark' else '#333333'}; font-family: \"Space Grotesk\", sans-serif;'>Menu</h4>", unsafe_allow_html=True)
        
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
        if st.button("Upload & Preview", disabled=False, key="nav_upload"):
            st.session_state.current_tab = "Upload"
            st.rerun()
        
        # Analysis button
        active_class = "background-color: #E8F0FE;" if active_tab == "Analysis" else ""
        if st.button("Analysis", disabled=not tabs_enabled, key="nav_analysis"):
            if tabs_enabled:
                st.session_state.current_tab = "Analysis"
                st.rerun()
            else:
                st.info("Please upload data first")
        
        # Visualization button
        active_class = "background-color: #E8F0FE;" if active_tab == "Visualization" else ""
        if st.button("Visualization", disabled=not tabs_enabled, key="nav_visualization"):
            if tabs_enabled:
                st.session_state.current_tab = "Visualization"
                st.rerun()
            else:
                st.info("Please upload data first")
                
        # Business AI button
        active_class = "background-color: #E8F0FE;" if active_tab == "Chat Bot" else ""
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
            
            # Display data stats if summary exists - theme aware
            if summary:
                st.markdown(f'<div style="color: {f"#ffffff" if theme == "dark" else "#333333"}; font-family: \'Space Grotesk\', sans-serif;"><strong>Rows:</strong> {summary["rows"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color: {f"#ffffff" if theme == "dark" else "#333333"}; font-family: \'Space Grotesk\', sans-serif;"><strong>Columns:</strong> {summary["columns"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color: {f"#ffffff" if theme == "dark" else "#333333"}; font-family: \'Space Grotesk\', sans-serif;"><strong>Missing Values:</strong> {summary["missing_values"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color: {f"#ffffff" if theme == "dark" else "#333333"}; font-family: \'Space Grotesk\', sans-serif;"><strong>Memory Usage:</strong> {summary["memory_usage"]:.2f} MB</div>', unsafe_allow_html=True)
            
            # Add option to show save dialog again
            if st.button("Save to Library"):
                st.session_state.show_save_dialog = True
                st.rerun()
