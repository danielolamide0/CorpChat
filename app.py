import streamlit as st
import pandas as pd
import os
import base64
from streamlit.components.v1 import html
from components.sidebar import render_sidebar
from components.data_preview import render_data_preview
from components.analysis_section import render_analysis_section
from components.visualization_section import render_visualization_section
from components.chat_bot import render_chat_bot, render_placeholder_chat_bot
from utils.data_loader import load_sample_data, load_file, get_data_summary

# Page configuration
st.set_page_config(
    page_title="Data Analysis & Visualization Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Theme toggle
theme = 'dark' if st.sidebar.toggle('Enable Dark Mode') else 'light'
st.markdown(f"""
    <style>
        .stApp {{
            background: {'#0e1117' if theme == 'dark' else '#ffffff'};
        }}
        div[class*="css"] {{
            color: {'#ffffff' if theme == 'dark' else '#0e1117'} !important;
        }}
        div[data-testid*="stToolbar"] {{
            color: {'#ffffff' if theme == 'dark' else '#0e1117'} !important;
        }}
        div[data-testid="stSidebar"] {{
            background: {'#262730' if theme == 'dark' else '#ffffff'};
            color: {'#ffffff' if theme == 'dark' else '#0e1117'} !important;
        }}
        .stMarkdown, label, p, span {{
            color: {'#ffffff' if theme == 'dark' else '#0e1117'} !important;
        }}
        .stButton > button {{
            color: {'#ffffff' if theme == 'dark' else '#0e1117'};
            background: {'#262730' if theme == 'dark' else '#ffffff'};
            border: 1px solid {'#4a4a4a' if theme == 'dark' else '#e0e0e0'};
        }}
        .streamlit-expanderHeader {{
            color: {'#ffffff' if theme == 'dark' else '#0e1117'} !important;
        }}
        div[data-testid="stFileUploadDropzone"] span, .stSlider span {{
            color: {'#ffffff' if theme == 'dark' else '#0e1117'} !important;
        }}
        .st-bq {{
            color: {'#ffffff' if theme == 'dark' else '#0e1117'} !important;
        }}
        .css-81oif8 {{
            color: {'#ffffff' if theme == 'dark' else '#0e1117'} !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Main app header with a modern design
st.markdown("""
<div style="background-color:#4F8BF9; padding:1.5rem; border-radius:10px; margin-bottom:20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
    <h1 style="color:white; margin:0; display:flex; align-items:center; gap:10px;">
        <span>📊</span> Data Analysis & Visualization Dashboard
    </h1>
    <p style="color:white; margin-top:10px; font-size:1.1rem; opacity:0.9;">
        Upload your data, analyze patterns, and create insightful visualizations all in one place.
    </p>
</div>
""", unsafe_allow_html=True)

# Render sidebar (file upload and navigation)
render_sidebar()

# Main content area based on selected tab
if st.session_state.current_tab == "Upload":
    if st.session_state.data is not None:
        render_data_preview()
    else:
        # Modern info box
        st.markdown("""
        <div style="padding:15px; border-radius:10px; background-color:#f0f7ff; border-left:5px solid #4F8BF9; margin-bottom:25px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size:24px;">👆</span>
                <span style="font-size:16px; font-weight:500;">Upload a CSV or Excel file using the sidebar to get started.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards with modern design
        st.markdown("""
        <h2 style="margin-bottom:20px; font-size:24px; font-weight:600;">Welcome to Your Data Analysis Platform</h2>
        """, unsafe_allow_html=True)
        
        # Modern cards layout
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background-color:white; padding:20px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height:100%;">
                <h3 style="color:#4F8BF9; margin-top:0;">🔍 Powerful Data Analysis</h3>
                <ul style="padding-left:20px;">
                    <li><strong>Process</strong> CSV and Excel files</li>
                    <li><strong>Filter</strong> and transform your data</li>
                    <li><strong>Calculate</strong> advanced statistics</li>
                    <li><strong>Clean</strong> messy data automatically</li>
                    <li><strong>Handle</strong> large datasets efficiently</li>
                    <li><strong>Export</strong> analysis results</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style="background-color:white; padding:20px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height:100%;">
                <h3 style="color:#4F8BF9; margin-top:0;">📊 Interactive Visualizations</h3>
                <ul style="padding-left:20px;">
                    <li><strong>Bar charts</strong> for categorical data</li>
                    <li><strong>Line charts</strong> for time series</li>
                    <li><strong>Scatter plots</strong> for correlations</li>
                    <li><strong>Histograms</strong> for distributions</li>
                    <li><strong>Pie charts</strong> for proportions</li>
                    <li><strong>Heatmaps, box plots</strong> and more</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # AI Assistant card
        st.markdown("""
        <div style="background-color:white; padding:20px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top:20px;">
            <h3 style="color:#4F8BF9; margin-top:0;">🤖 AI-Powered Business Intelligence</h3>
            <p>Ask questions about your data using natural language and get instant insights. The AI assistant can:</p>
            <div style="display:flex; flex-wrap:wrap; gap:10px; margin-top:15px;">
                <div style="background-color:#f0f7ff; padding:8px 15px; border-radius:20px; display:inline-block;">📝 Summarize key trends</div>
                <div style="background-color:#f0f7ff; padding:8px 15px; border-radius:20px; display:inline-block;">🔍 Identify outliers</div>
                <div style="background-color:#f0f7ff; padding:8px 15px; border-radius:20px; display:inline-block;">📊 Create visualizations</div>
                <div style="background-color:#f0f7ff; padding:8px 15px; border-radius:20px; display:inline-block;">💡 Recommend actions</div>
                <div style="background-color:#f0f7ff; padding:8px 15px; border-radius:20px; display:inline-block;">📈 Forecast trends</div>
                <div style="background-color:#f0f7ff; padding:8px 15px; border-radius:20px; display:inline-block;">🧮 Perform calculations</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload Guidelines
        st.markdown("""
        <div style="background-color:white; padding:20px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top:20px;">
            <h3 style="color:#4F8BF9; margin-top:0;">📁 File Upload Guidelines</h3>
            <ul style="padding-left:20px;">
                <li><strong>Supported formats:</strong> CSV (.csv) and Excel (.xlsx, .xls)</li>
                <li><strong>Maximum file size:</strong> 200MB</li>
                <li><strong>Structure:</strong> First row should contain column headers</li>
                <li><strong>Large files:</strong> Use the sampling option for better performance</li>
                <li><strong>Data types:</strong> Automatically detected for proper analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_tab == "Analysis":
    if st.session_state.data is not None:
        render_analysis_section()
    else:
        # Modern styled warning
        st.markdown("""
        <div style="padding:20px; border-radius:10px; background-color:#fff8e6; border-left:5px solid #ffb700; margin:20px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size:24px;">⚠️</span>
                <span style="font-size:16px; font-weight:500;">Please upload a data file first to perform analysis.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
elif st.session_state.current_tab == "Visualization":
    if st.session_state.data is not None:
        render_visualization_section()
    else:
        # Modern styled warning
        st.markdown("""
        <div style="padding:20px; border-radius:10px; background-color:#fff8e6; border-left:5px solid #ffb700; margin:20px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size:24px;">⚠️</span>
                <span style="font-size:16px; font-weight:500;">Please upload a data file first to create visualizations.</span>
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
        # Modern styled warning
        st.markdown("""
        <div style="padding:20px; border-radius:10px; background-color:#fff8e6; border-left:5px solid #ffb700; margin:20px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size:24px;">⚠️</span>
                <span style="font-size:16px; font-weight:500;">Please upload a data file first to use the AI assistant.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Modern footer with subtle gradient
st.markdown("""
<div style="margin-top: 50px; padding: 20px; border-radius: 10px; background: linear-gradient(90deg, #f0f7ff 0%, #ffffff 100%); text-align: center;">
    <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 10px;">
        <span style="font-size: 22px;">📊</span>
        <span style="font-weight: 600; color: #4F8BF9;">DataViz Analytics Dashboard</span>
    </div>
    <p style="margin: 0; font-size: 14px; color: #718096;">
        Built with Streamlit • Modern Data Analysis • <a href="#" style="color: #4F8BF9; text-decoration: none;">Documentation</a>
    </p>
</div>
""", unsafe_allow_html=True)
