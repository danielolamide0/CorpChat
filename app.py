import streamlit as st
import pandas as pd
import os
import base64
from streamlit.components.v1 import html
import time
from datetime import datetime

# Set default page configuration
st.set_page_config(
    page_title="CorpChat Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

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

# Function to set background image
def set_background(background_image_path):
    """Apply a background image to the Streamlit app"""
    background_base64 = get_base64_of_file(background_image_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/svg+xml;base64,{background_base64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
from components.sidebar import render_sidebar
from components.data_preview import render_data_preview
from components.analysis_section import render_analysis_section
from components.visualization_section import render_visualization_section
from components.chat_bot import render_chat_bot, render_placeholder_chat_bot
from utils.data_loader import load_sample_data, load_file, get_data_summary

# Page configuration is set at the top of the file

# Load custom CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

# Load the custom CSS if it exists
css_path = ".streamlit/styles.css"
if os.path.exists(css_path):
    load_css(css_path)

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

# Check if OpenAI API key is available
if 'openai_api_key_available' not in st.session_state:
    api_key = os.environ.get("OPENAI_API_KEY")
    st.session_state.openai_api_key_available = api_key is not None and api_key != ""

# Theme toggle in sidebar - light mode as default
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'  # Default to light theme

# Create theme settings dictionary
theme_light = {
    "base": "light",
    "primaryColor": "#4F8BF9",
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F0F2F6",
    "textColor": "#242424",
    "font": "sans-serif"
}

theme_dark = {
    "base": "dark",
    "primaryColor": "#4F8BF9",
    "backgroundColor": "#0E1117",
    "secondaryBackgroundColor": "#262730",
    "textColor": "#FAFAFA",
    "font": "sans-serif"
}

# Update theme state based on toggle
use_dark_theme = st.sidebar.toggle('Enable Dark Mode', value=False)
if use_dark_theme:
    st.session_state.theme = 'dark'
else:
    st.session_state.theme = 'light'

# Get current theme
theme = st.session_state.theme

# Set the appropriate background image based on theme
if theme == 'dark':
    background_image_path = './assets/corpchat_background.svg'
else:
    background_image_path = './assets/light_background.svg'

# Apply the appropriate background
if os.path.exists(background_image_path):
    set_background(background_image_path)

# Apply theme styling
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        
        /* Set sidebar background color as CSS variable based on theme */
        :root {{
            --sidebar-bg-color: {f'#242424' if theme == 'dark' else '#ffffff'};
        }}
        
        /* Navigation bar in dark mode */
        header[data-testid="stHeader"] {{
            background-color: {f'#242424' if theme == 'dark' else ''} !important;
        }}
        
        /* Hamburger menu button for sidebar */
        button[kind="header"] {{
            color: {f'white' if theme == 'dark' else ''} !important;
        }}
        
        .stApp {{
            /* Background is set by the SVG */
            background-color: {f'rgba(20, 20, 20, 0.3)' if theme == 'dark' else 'rgba(255, 255, 255, 0.3)'};
        }}
        
        /* General text styling */
        body, .stMarkdown, p, span, label, div {{
            font-family: 'Space Grotesk', sans-serif !important;
            color: {f'#ffffff' if theme == 'dark' else '#333333'} !important;
        }}
        
        /* Ensure all text in sidebar also respects theme */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] div {{
            color: {f'#ffffff' if theme == 'dark' else '#333333'} !important;
        }}
        
        /* Target specific Streamlit sidebar elements */
        .sidebar .sidebar-content {{
            background-color: {f'#242424' if theme == 'dark' else '#ffffff'} !important;
        }}
        
        /* Target all elements within sidebar - important for proper theme application */
        .css-1d391kg, .css-1v3fvcr, .css-12oz5g7 {{
            background-color: {f'#242424' if theme == 'dark' else '#ffffff'} !important;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 600 !important;
            color: {f'#ffffff' if theme == 'dark' else '#242424'} !important;
        }}
        
        /* Sidebar styling */
        div[data-testid="stSidebar"] {{
            background: {f'#242424' if theme == 'dark' else '#ffffff'} !important;
            border-right: 1px solid {f'#333333' if theme == 'dark' else '#e0e0e0'} !important;
        }}
        
        section[data-testid="stSidebar"] {{
            background: {f'#242424' if theme == 'dark' else '#ffffff'} !important;
        }}
        
        div[data-testid="stSidebarContent"] {{
            background: {f'#242424' if theme == 'dark' else '#ffffff'} !important;
        }}
        
        .css-6qob1r {{
            background: {f'#242424' if theme == 'dark' else '#ffffff'} !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            font-family: 'Space Grotesk', sans-serif !important;
            color: {f'#ffffff' if theme == 'dark' else '#242424'};
            background: {f'#333333' if theme == 'dark' else '#f5f5f5'};
            border: 1px solid {f'#4a4a4a' if theme == 'dark' else '#e0e0e0'};
            border-radius: 6px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        /* Input elements */
        .stTextInput input, .stSelectbox, .stMultiselect {{
            border: 1px solid {f'#4a4a4a' if theme == 'dark' else '#e0e0e0'};
            background: {f'#333333' if theme == 'dark' else '#ffffff'};
            border-radius: 6px;
            color: {f'#ffffff' if theme == 'dark' else '#333333'};
        }}
        
        /* File upload zone */
        div[data-testid="stFileUploadDropzone"] {{
            background: {f'#333333' if theme == 'dark' else '#f5f5f5'};
            border: 2px dashed {f'#4a4a4a' if theme == 'dark' else '#e0e0e0'};
            border-radius: 8px;
        }}
        
        /* Fix for file dropzone text color in dark mode - stronger selector to override other styles */
        div[data-testid="stFileUploadDropzone"] p,
        div[data-testid="stFileUploadDropzone"] [data-testid="stMarkdownContainer"] p,
        div[data-testid="stFileUploadDropzone"] span,
        div[data-testid="stFileUploadDropzone"] div {{
            color: {f'black' if theme == 'dark' else '#333333'} !important;
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 500 !important;
            color: {f'#ffffff' if theme == 'dark' else '#242424'} !important;
            background: {f'#333333' if theme == 'dark' else '#f9f9f9'};
            border: 1px solid {f'#4a4a4a' if theme == 'dark' else '#e0e0e0'};
            border-radius: 6px;
        }}
        
        /* Metrics */
        div[data-testid="stMetric"] {{
            background-color: {f'rgba(51, 51, 51, 0.7)' if theme == 'dark' else 'rgba(245, 245, 245, 0.7)'};
            border-radius: 6px;
            padding: 10px;
            border: 1px solid {f'#4a4a4a' if theme == 'dark' else '#e0e0e0'};
        }}
        
        div[data-testid="stMetric"] > div:first-child {{
            color: {f'#ffffff' if theme == 'dark' else '#242424'} !important;
        }}
        
        div[data-testid="stMetric"] > div:nth-child(2) {{
            color: {f'#e0e0e0' if theme == 'dark' else '#666666'} !important;
        }}
        
        /* Make dataframes more visible */
        div[data-testid="stDataFrame"] {{
            background-color: {f'rgba(51, 51, 51, 0.7)' if theme == 'dark' else 'rgba(245, 245, 245, 0.7)'};
            border-radius: 6px;
            padding: 10px;
            border: 1px solid {f'#4a4a4a' if theme == 'dark' else '#e0e0e0'};
        }}
        
        /* Toggle switch styling */
        div[data-testid="stCheckbox"] {{
            background-color: {f'rgba(51, 51, 51, 0.3)' if theme == 'dark' else 'rgba(245, 245, 245, 0.3)'};
            border-radius: 6px;
            padding: 10px 15px;
            border: 1px solid {f'#4a4a4a' if theme == 'dark' else '#e0e0e0'};
        }}
        
        /* Sidebar toggle button specific styles */
        [data-testid="stSidebar"] [data-testid="stCheckbox"] {{
            background-color: {f'rgba(100, 100, 100, 0.5)' if theme == 'dark' else 'rgba(245, 245, 245, 0.3)'} !important;
        }}
        
        /* Ensure sidebar toggle text is visible */
        [data-testid="stSidebar"] [data-testid="stCheckbox"] p {{
            color: {f'#ffffff' if theme == 'dark' else '#333333'} !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Use the above get_base64_of_file function
# Professional header inspired by modern analytics dashboards with theme-specific colors
st.markdown(f"""
<div class="page-header">
    <div>
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: {f'#ffffff' if theme == 'dark' else '#242424'};">
            CorpChat Analytics
        </h1>
        <p class="page-header-description" style="font-family: 'Space Grotesk', sans-serif; color: {f'#e0e0e0' if theme == 'dark' else '#666666'};">
            Transform your data into actionable insights with powerful analytics and Synaptide AI
        </p>
    </div>
    <div>
        <div style="background-color:{f'#333333' if theme == 'dark' else '#f5f5f5'}; border-radius:8px; padding:6px 10px; font-size:12px; color:{f'#ffffff' if theme == 'dark' else '#333333'}; border: 1px solid {f'#4a4a4a' if theme == 'dark' else '#e0e0e0'}; font-family: 'Space Grotesk', sans-serif;">
            <span style="font-weight:600;">Last updated:</span> 
            {datetime.now().strftime("%b %d, %Y")} 
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Add key metrics bar if data is loaded
if st.session_state.data is not None and hasattr(st.session_state, 'data_summary') and st.session_state.data_summary:
    summary = st.session_state.data_summary
    
    st.markdown("""
    <div class="metrics-container">
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Rows</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Columns</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Missing Values</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{:.1f} MB</div>
            <div class="metric-label">Memory Usage</div>
        </div>
    </div>
    """.format(
        summary.get('rows', 0),
        summary.get('columns', 0),
        summary.get('missing_values', 0),
        summary.get('memory_usage', 0)
    ), unsafe_allow_html=True)

# Render sidebar (file upload and navigation)
render_sidebar()

# Main content area based on selected tab
if st.session_state.current_tab == "Upload":
    if st.session_state.data is not None:
        render_data_preview()
    else:
        # Welcome banner with call to action - theme aware
        st.markdown(f"""
        <div class="dashboard-card" style="background-color:{f'#242424' if theme == 'dark' else '#f9f9f9'}; margin-bottom:30px; border:{f'none' if theme == 'dark' else '1px solid #e0e0e0'}; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:15px; padding:25px;">
                <div style="max-width:70%;">
                    <h2 style="color:{f'white' if theme == 'dark' else '#242424'}; margin-top:0; font-size:1.8rem; font-weight:600; font-family:'Space Grotesk', sans-serif;">
                        Welcome to CorpChat Analytics
                    </h2>
                    <p style="color:{f'rgba(255,255,255,0.9)' if theme == 'dark' else '#555555'}; margin-bottom:20px; font-size:1rem; line-height:1.5; font-family:'Space Grotesk', sans-serif;">
                        A comprehensive solution for analyzing, visualizing, and extracting insights from your business data.
                        Powered by Synaptide AI for intelligent analysis and insights.
                    </p>
                    <div style="background-color:{f'#333333' if theme == 'dark' else 'white'}; border:{f'1px solid #4a4a4a' if theme == 'dark' else 'none'}; 
                        border-radius:6px; padding:12px 16px; margin-bottom:10px; display:inline-flex; align-items:center; gap:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                        <span style="font-size:18px;">👆</span>
                        <span style="color:{f'white' if theme == 'dark' else '#242424'}; font-size:0.95rem; font-weight:500; font-family:'Space Grotesk', sans-serif;">Upload a file using the sidebar to get started</span>
                    </div>
                </div>
                <div style="min-width:150px; text-align:center;">
                    <img src="data:image/jpeg;base64,{get_base64_of_file('assets/synaptide_logo.jpeg')}" style="max-width:160px; height:auto; border-radius:8px;">
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature grid layout inspired by modern analytics dashboards with theme-specific styling
        st.markdown(f"""
        <h3 style="margin-bottom:20px; font-size:1.4rem; font-weight:600; color:{f'#ffffff' if theme == 'dark' else '#242424'}; font-family:'Space Grotesk', sans-serif;">
            Key Features & Capabilities
        </h3>
        """, unsafe_allow_html=True)

        # Enhanced feature sections with images - updated to black/white/gray theme
        st.markdown(f"""
        <div class="feature-showcase">
            <div class="feature-showcase-item" style="display:flex; margin-bottom:30px; background:white; border-radius:12px; padding:25px; gap:30px; align-items:center; border:1px solid #E0E0E0; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
                <div style="flex:1; min-width:180px;">
                    <div style="font-size:24px; margin-bottom:10px; color:#242424; font-family:'Space Grotesk', sans-serif; font-weight:600;">Data Analysis</div>
                    <p style="color:#333; line-height:1.6; font-family:'Space Grotesk', sans-serif;">
                        Transform your raw data into actionable business intelligence with our comprehensive analysis tools:
                    </p>
                    <ul style="color:#333; padding-left:20px; margin-top:10px; font-family:'Space Grotesk', sans-serif;">
                        <li style="margin-bottom:5px;">Calculate detailed statistics like mean, median, standard deviation</li>
                        <li style="margin-bottom:5px;">Identify correlations and relationships between variables</li>
                        <li style="margin-bottom:5px;">Filter and segment data to focus on specific business questions</li>
                        <li style="margin-bottom:5px;">Handle outliers and missing values with intelligent algorithms</li>
                    </ul>
                </div>
                <div style="flex:1; min-width:180px; display:flex; justify-content:center;">
                    <img src="data:image/svg+xml;base64,{get_base64_of_file('assets/example_images/data_analysis.svg')}" style="max-width:100%; height:auto; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                </div>
            </div>
            
            <div class="feature-showcase-item" style="display:flex; margin-bottom:30px; background:white; border-radius:12px; padding:25px; gap:30px; align-items:center; border:1px solid #E0E0E0; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
                <div style="flex:1; min-width:180px; display:flex; justify-content:center;">
                    <img src="data:image/svg+xml;base64,{get_base64_of_file('assets/example_images/data_visualization.svg')}" style="max-width:100%; height:auto; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                </div>
                <div style="flex:1; min-width:180px;">
                    <div style="font-size:24px; margin-bottom:10px; color:#242424; font-family:'Space Grotesk', sans-serif; font-weight:600;">Data Visualization</div>
                    <p style="color:#333; line-height:1.6; font-family:'Space Grotesk', sans-serif;">
                        Create stunning interactive visualizations that make your data come alive:
                    </p>
                    <ul style="color:#333; padding-left:20px; margin-top:10px; font-family:'Space Grotesk', sans-serif;">
                        <li style="margin-bottom:5px;">Generate beautiful bar charts, line graphs, scatter plots</li>
                        <li style="margin-bottom:5px;">Build heatmaps and correlation matrices to identify patterns</li>
                        <li style="margin-bottom:5px;">Create pie charts and box plots for distribution analysis</li>
                        <li style="margin-bottom:5px;">Export and share visualizations with your team</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Additional Features in a Card Grid - updated to black/white/gray theme -->
        <div class="feature-cards-container">
            <div class="feature-card" style="background:white; border:1px solid #E0E0E0;">
                <div class="feature-card-icon" style="color:#242424; font-family:'Space Grotesk', sans-serif;">Cleaning</div>
                <div class="feature-card-title" style="color:#242424; font-family:'Space Grotesk', sans-serif;">Data Cleaning</div>
                <div class="feature-card-description" style="color:#474747; font-family:'Space Grotesk', sans-serif;">
                    Clean and preprocess your data with automated tools for handling missing values, outliers, and inconsistencies. Prepare your data for analysis in just a few clicks.
                </div>
            </div>
            
            <div class="feature-card" style="background:white; border:1px solid #E0E0E0;">
                <div class="feature-card-icon" style="color:#242424; font-family:'Space Grotesk', sans-serif;">Assistant</div>
                <div class="feature-card-title" style="color:#242424; font-family:'Space Grotesk', sans-serif;">AI Assistant</div>
                <div class="feature-card-description" style="color:#474747; font-family:'Space Grotesk', sans-serif;">
                    Ask questions in natural language to get insights, summaries, and visualizations automatically generated by our AI. No complex query language needed.
                </div>
            </div>
            
            <div class="feature-card" style="background:white; border:1px solid #E0E0E0;">
                <div class="feature-card-icon" style="color:#242424; font-family:'Space Grotesk', sans-serif;">Responsive</div>
                <div class="feature-card-title" style="color:#242424; font-family:'Space Grotesk', sans-serif;">Responsive Design</div>
                <div class="feature-card-description" style="color:#474747; font-family:'Space Grotesk', sans-serif;">
                    Access your analytics from any device with our fully responsive dashboard that adapts to your screen size. Work seamlessly from desktop or mobile.
                </div>
            </div>
            
            <div class="feature-card" style="background:white; border:1px solid #E0E0E0;">
                <div class="feature-card-icon" style="color:#242424; font-family:'Space Grotesk', sans-serif;">Real-time</div>
                <div class="feature-card-title" style="color:#242424; font-family:'Space Grotesk', sans-serif;">Real-time Processing</div>
                <div class="feature-card-description" style="color:#474747; font-family:'Space Grotesk', sans-serif;">
                    Process and visualize your data in real-time with immediate feedback and interactive elements. See results instantly as you work.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # AI capabilities highlight - updated to black theme with white content
        st.markdown(f"""
        <div class="chart-container" style="margin-top:30px; background-color:#242424; border:1px solid #333; position:relative; overflow:hidden; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
            <div style="position:absolute; right:-30px; top:-30px; width:200px; height:200px; background:radial-gradient(circle, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 70%); border-radius:50%;"></div>
            
            <div style="padding:25px;">
                <div style="font-size:24px; margin-bottom:15px; color:white; font-family:'Space Grotesk', sans-serif; font-weight:600; display:flex; align-items:center; gap:10px;">
                    <img src="data:image/jpeg;base64,{get_base64_of_file('assets/synaptide_logo.jpeg')}" style="width:32px; height:32px; border-radius:4px;">
                    <span>Synaptide AI-Powered Analytics</span>
                </div>
                
                <p style="color:white; font-size:1rem; line-height:1.6; margin-bottom:20px; font-family:'Space Grotesk', sans-serif;">
                    Our AI assistant transforms how you interact with your data. Just ask questions in plain English and get instant insights.
                </p>
                
                <div style="display:flex; flex-wrap:wrap; gap:20px; margin-top:20px;">
                    <div style="flex:1; min-width:250px; background:white; padding:20px; border-radius:10px; border:1px solid #E0E0E0; box-shadow:0 4px 8px rgba(0,0,0,0.08);">
                        <h4 style="color:#242424; margin-bottom:15px; font-size:1.1rem; display:flex; align-items:center; gap:8px; font-family:'Space Grotesk', sans-serif; font-weight:600;">
                            Ask Questions Like
                        </h4>
                        <ul style="color:#333; padding-left:20px; margin:0; font-family:'Space Grotesk', sans-serif;">
                            <li style="margin-bottom:8px;">"What are the top-selling products?"</li>
                            <li style="margin-bottom:8px;">"Show monthly revenue trends"</li>
                            <li style="margin-bottom:8px;">"Find correlations between customer age and spending"</li>
                            <li style="margin-bottom:8px;">"Create a visualization of regional performance"</li>
                        </ul>
                    </div>
                    
                    <div style="flex:1; min-width:250px; background:white; padding:20px; border-radius:10px; border:1px solid #E0E0E0; box-shadow:0 4px 8px rgba(0,0,0,0.08);">
                        <h4 style="color:#242424; margin-bottom:15px; font-size:1.1rem; display:flex; align-items:center; gap:8px; font-family:'Space Grotesk', sans-serif; font-weight:600;">
                            AI-Generated Insights
                        </h4>
                        <ul style="color:#333; padding-left:20px; margin:0; font-family:'Space Grotesk', sans-serif;">
                            <li style="margin-bottom:8px;">Automatic trend detection and anomaly identification</li>
                            <li style="margin-bottom:8px;">Smart visualization recommendations based on your data</li> 
                            <li style="margin-bottom:8px;">Natural language explanations of complex patterns</li>
                            <li style="margin-bottom:8px;">Instant responses to your business questions</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Supported file formats section - updated to white background
        st.markdown("""
        <div class="chart-container" style="margin-top:30px; background-color:white; border:1px solid #E0E0E0; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
            <div style="padding:25px;">
                <div style="font-size:20px; margin-bottom:15px; color:#242424; font-family:'Space Grotesk', sans-serif; font-weight:600; display:flex; align-items:center; gap:8px;">
                    Supported File Formats
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:12px; margin-top:15px;">
                    <div style="background-color:#F5F5F5; border:1px solid #E0E0E0; border-radius:100px; padding:8px 16px; display:inline-block; font-size:0.9rem; color:#242424; font-family:'Space Grotesk', sans-serif;">CSV (.csv)</div>
                    <div style="background-color:#F5F5F5; border:1px solid #E0E0E0; border-radius:100px; padding:8px 16px; display:inline-block; font-size:0.9rem; color:#242424; font-family:'Space Grotesk', sans-serif;">Excel (.xlsx)</div>
                    <div style="background-color:#F5F5F5; border:1px solid #E0E0E0; border-radius:100px; padding:8px 16px; display:inline-block; font-size:0.9rem; color:#242424; font-family:'Space Grotesk', sans-serif;">Excel 97-2003 (.xls)</div>
                </div>
                <div style="margin-top:20px; color:#333; font-size:0.95rem; line-height:1.5; font-family:'Space Grotesk', sans-serif;">
                    <p style="font-weight:600; margin-bottom:8px;">Guidelines:</p>
                    <ul style="margin-top:5px; padding-left:20px;">
                        <li style="margin-bottom:5px;">Files should have column headers in the first row</li>
                        <li style="margin-bottom:5px;">Maximum file size: 200MB</li>
                        <li style="margin-bottom:5px;">For large files, we recommend using the sampling option</li>
                        <li style="margin-bottom:5px;">Data types are automatically detected for analysis</li>
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_tab == "Analysis":
    if st.session_state.data is not None:
        render_analysis_section()
    else:
        # Modern styled warning with new color scheme
        st.markdown("""
        <div style="padding:25px; border-radius:10px; background-color:#FFF8E1; border:1px solid #FFECB3; margin:20px 0; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size:16px; font-weight:600; color:#F9A825; font-family:'Space Grotesk', sans-serif;">Warning:</span>
                <span style="font-size:16px; font-weight:500; color:#333; font-family:'Space Grotesk', sans-serif;">Please upload a data file first to perform analysis.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
elif st.session_state.current_tab == "Visualization":
    if st.session_state.data is not None:
        render_visualization_section()
    else:
        # Modern styled warning with new color scheme
        st.markdown("""
        <div style="padding:25px; border-radius:10px; background-color:#FFF8E1; border:1px solid #FFECB3; margin:20px 0; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size:16px; font-weight:600; color:#F9A825; font-family:'Space Grotesk', sans-serif;">Warning:</span>
                <span style="font-size:16px; font-weight:500; color:#333; font-family:'Space Grotesk', sans-serif;">Please upload a data file first to create visualizations.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
elif st.session_state.current_tab == "Chat Bot":
    if st.session_state.data is not None:
        # Check if we have an API key available
        if st.session_state.get('openai_api_key_available', False):
            render_chat_bot()
        else:
            render_placeholder_chat_bot()
    else:
        # Modern styled warning with new color scheme
        st.markdown("""
        <div style="padding:25px; border-radius:10px; background-color:#FFF8E1; border:1px solid #FFECB3; margin:20px 0; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size:16px; font-weight:600; color:#F9A825; font-family:'Space Grotesk', sans-serif;">Warning:</span>
                <span style="font-size:16px; font-weight:500; color:#333; font-family:'Space Grotesk', sans-serif;">Please upload a data file first to use the AI assistant.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Modern footer with new black/white theme
st.markdown(f"""
<div style="margin-top: 50px; padding: 25px; border-radius: 10px; background: #242424; text-align: center; border: 1px solid #333;">
    <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-bottom: 15px;">
        <img src="data:image/jpeg;base64,{get_base64_of_file('assets/synaptide_logo.jpeg')}" style="width: 32px; height: 32px; border-radius: 4px;">
        <span style="font-weight: 600; color: white; font-family: 'Space Grotesk', sans-serif; font-size: 18px;">CorpChat Analytics</span>
    </div>
    <p style="margin: 0; font-size: 14px; color: rgba(255, 255, 255, 0.7); font-family: 'Space Grotesk', sans-serif;">
        Powered by Synaptide AI • Advanced Business Intelligence • <a href="#" style="color: white; text-decoration: none; border-bottom: 1px dotted white;">Support</a>
    </p>
</div>
""", unsafe_allow_html=True)
