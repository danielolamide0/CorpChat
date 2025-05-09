import streamlit as st
import pandas as pd
import os
import base64
from streamlit.components.v1 import html
import time
from datetime import datetime

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

# Apply the modern background image
background_image_path = './assets/modern_background.svg'
if os.path.exists(background_image_path):
    set_background(background_image_path)

# Theme toggle
theme = 'dark' if st.sidebar.toggle('Enable Dark Mode') else 'light'
st.markdown(f"""
    <style>
        .stApp {{
            /* Background is already set by the SVG, but we add a subtle overlay for theme */
            background-color: {'rgba(14, 17, 23, 0.92)' if theme == 'dark' else 'rgba(255, 255, 255, 0.92)'};
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

# Use the above get_base64_of_file function
# Professional header inspired by modern analytics dashboards
st.markdown("""
<div class="page-header">
    <div>
        <h1>
            <span style="font-size:28px; margin-right:10px;">📊</span>
            Data Analytics Platform
        </h1>
        <p class="page-header-description">
            Transform your data into actionable insights with powerful analytics and visualizations
        </p>
    </div>
    <div>
        <div style="background-color:rgba(0,0,0,0.2); border-radius:8px; padding:6px 10px; font-size:12px; color:rgba(255,255,255,0.8);">
            <span style="font-weight:600;">Last updated:</span> 
            {} 
        </div>
    </div>
</div>
""".format(datetime.now().strftime("%b %d, %Y")), unsafe_allow_html=True)

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
        # Welcome banner with call to action
        st.markdown(f"""
        <div class="dashboard-card" style="background-color:#242424; margin-bottom:30px; border:none; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:15px; padding:25px;">
                <div style="max-width:70%;">
                    <h2 style="color:white; margin-top:0; font-size:1.8rem; font-weight:600; font-family:'Space Grotesk', sans-serif;">
                        Welcome to CorpChat Analytics
                    </h2>
                    <p style="color:rgba(255,255,255,0.9); margin-bottom:20px; font-size:1rem; line-height:1.5; font-family:'Space Grotesk', sans-serif;">
                        A comprehensive solution for analyzing, visualizing, and extracting insights from your business data.
                        Powered by Synaptide AI for intelligent analysis and insights.
                    </p>
                    <div style="background-color:white; border:none; 
                        border-radius:6px; padding:12px 16px; margin-bottom:10px; display:inline-flex; align-items:center; gap:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                        <span style="font-size:18px;">👆</span>
                        <span style="color:#242424; font-size:0.95rem; font-weight:500; font-family:'Space Grotesk', sans-serif;">Upload a file using the sidebar to get started</span>
                    </div>
                </div>
                <div style="min-width:150px; text-align:center;">
                    <img src="data:image/jpeg;base64,{get_base64_of_file('assets/synaptide_logo.jpeg')}" style="max-width:160px; height:auto; border-radius:8px;">
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature grid layout inspired by modern analytics dashboards
        st.markdown("""
        <h3 style="margin-bottom:20px; font-size:1.3rem; font-weight:600; color:white;">
            Key Features & Capabilities
        </h3>
        """, unsafe_allow_html=True)

        # Enhanced feature sections with images
        st.markdown(f"""
        <div class="feature-showcase">
            <div class="feature-showcase-item" style="display:flex; margin-bottom:30px; background:rgba(55, 65, 81, 0.3); border-radius:12px; padding:20px; gap:30px; align-items:center; border:1px solid rgba(79, 139, 249, 0.2);">
                <div style="flex:1; min-width:180px;">
                    <div style="font-size:24px; margin-bottom:10px; color:white;">📈 Data Analysis</div>
                    <p style="color:rgba(255,255,255,0.9); line-height:1.6;">
                        Transform your raw data into actionable business intelligence with our comprehensive analysis tools:
                    </p>
                    <ul style="color:rgba(255,255,255,0.9); padding-left:20px; margin-top:10px;">
                        <li style="margin-bottom:5px;">Calculate detailed statistics like mean, median, standard deviation</li>
                        <li style="margin-bottom:5px;">Identify correlations and relationships between variables</li>
                        <li style="margin-bottom:5px;">Filter and segment data to focus on specific business questions</li>
                        <li style="margin-bottom:5px;">Handle outliers and missing values with intelligent algorithms</li>
                    </ul>
                </div>
                <div style="flex:1; min-width:180px; display:flex; justify-content:center;">
                    <img src="data:image/svg+xml;base64,{get_base64_of_file('assets/example_images/data_analysis.svg')}" style="max-width:100%; height:auto; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.4);">
                </div>
            </div>
            
            <div class="feature-showcase-item" style="display:flex; margin-bottom:30px; background:rgba(55, 65, 81, 0.3); border-radius:12px; padding:20px; gap:30px; align-items:center; border:1px solid rgba(79, 139, 249, 0.2);">
                <div style="flex:1; min-width:180px; display:flex; justify-content:center;">
                    <img src="data:image/svg+xml;base64,{get_base64_of_file('assets/example_images/data_visualization.svg')}" style="max-width:100%; height:auto; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.4);">
                </div>
                <div style="flex:1; min-width:180px;">
                    <div style="font-size:24px; margin-bottom:10px; color:white;">📊 Data Visualization</div>
                    <p style="color:rgba(255,255,255,0.9); line-height:1.6;">
                        Create stunning interactive visualizations that make your data come alive:
                    </p>
                    <ul style="color:rgba(255,255,255,0.9); padding-left:20px; margin-top:10px;">
                        <li style="margin-bottom:5px;">Generate beautiful bar charts, line graphs, scatter plots</li>
                        <li style="margin-bottom:5px;">Build heatmaps and correlation matrices to identify patterns</li>
                        <li style="margin-bottom:5px;">Create pie charts and box plots for distribution analysis</li>
                        <li style="margin-bottom:5px;">Export and share visualizations with your team</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Additional Features in a Card Grid -->
        <div class="feature-cards-container">
            <div class="feature-card">
                <div class="feature-card-icon">🧹</div>
                <div class="feature-card-title">Data Cleaning</div>
                <div class="feature-card-description">
                    Clean and preprocess your data with automated tools for handling missing values, outliers, and inconsistencies. Prepare your data for analysis in just a few clicks.
                </div>
            </div>
            
            <div class="feature-card">
                <div class="feature-card-icon">🤖</div>
                <div class="feature-card-title">AI Assistant</div>
                <div class="feature-card-description">
                    Ask questions in natural language to get insights, summaries, and visualizations automatically generated by our AI. No complex query language needed.
                </div>
            </div>
            
            <div class="feature-card">
                <div class="feature-card-icon">📱</div>
                <div class="feature-card-title">Responsive Design</div>
                <div class="feature-card-description">
                    Access your analytics from any device with our fully responsive dashboard that adapts to your screen size. Work seamlessly from desktop or mobile.
                </div>
            </div>
            
            <div class="feature-card">
                <div class="feature-card-icon">🔄</div>
                <div class="feature-card-title">Real-time Processing</div>
                <div class="feature-card-description">
                    Process and visualize your data in real-time with immediate feedback and interactive elements. See results instantly as you work.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # AI capabilities highlight - simplified and modern
        st.markdown("""
        <div class="chart-container" style="margin-top:30px; background-color:rgba(79, 139, 249, 0.1); border:1px solid rgba(79, 139, 249, 0.2); position:relative; overflow:hidden;">
            <div style="position:absolute; right:-30px; top:-30px; width:200px; height:200px; background:radial-gradient(circle, rgba(79, 139, 249, 0.3) 0%, rgba(79, 139, 249, 0) 70%); border-radius:50%;"></div>
            
            <div class="chart-title">
                <span class="chart-title-icon">🤖</span> AI-Powered Analytics
            </div>
            
            <div style="padding:15px 20px;">
                <p style="color:white; font-size:1rem; line-height:1.6; margin-bottom:20px;">
                    Our AI assistant transforms how you interact with your data. Just ask questions in plain English and get instant insights.
                </p>
                
                <div style="display:flex; flex-wrap:wrap; gap:20px; margin-top:20px;">
                    <div style="flex:1; min-width:250px; background:rgba(0, 31, 84, 0.3); padding:20px; border-radius:10px; border:1px solid rgba(79, 139, 249, 0.3);">
                        <h4 style="color:white; margin-bottom:15px; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
                            <span style="font-size:20px;">💬</span> Ask Questions Like
                        </h4>
                        <ul style="color:white; padding-left:20px; margin:0;">
                            <li style="margin-bottom:8px;">"What are the top-selling products?"</li>
                            <li style="margin-bottom:8px;">"Show monthly revenue trends"</li>
                            <li style="margin-bottom:8px;">"Find correlations between customer age and spending"</li>
                            <li style="margin-bottom:8px;">"Create a visualization of regional performance"</li>
                        </ul>
                    </div>
                    
                    <div style="flex:1; min-width:250px; background:rgba(0, 31, 84, 0.3); padding:20px; border-radius:10px; border:1px solid rgba(79, 139, 249, 0.3);">
                        <h4 style="color:white; margin-bottom:15px; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
                            <span style="font-size:20px;">✨</span> AI-Generated Insights
                        </h4>
                        <ul style="color:white; padding-left:20px; margin:0;">
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
        
        # Supported file formats section
        st.markdown("""
        <div class="chart-container" style="margin-top:30px;">
            <div class="chart-title">
                <span class="chart-title-icon">📁</span> Supported File Formats
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:15px; margin-top:15px;">
                <div class="pill-tag" style="font-size:0.9rem;">CSV (.csv)</div>
                <div class="pill-tag" style="font-size:0.9rem;">Excel (.xlsx)</div>
                <div class="pill-tag" style="font-size:0.9rem;">Excel 97-2003 (.xls)</div>
            </div>
            <div style="margin-top:20px; color:rgba(255,255,255,0.8); font-size:0.9rem; line-height:1.5;">
                <p><strong>Guidelines:</strong></p>
                <ul style="margin-top:5px; padding-left:20px;">
                    <li>Files should have column headers in the first row</li>
                    <li>Maximum file size: 200MB</li>
                    <li>For large files, we recommend using the sampling option</li>
                    <li>Data types are automatically detected for analysis</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_tab == "Analysis":
    if st.session_state.data is not None:
        render_analysis_section()
    else:
        # Modern styled warning
        st.markdown("""
        <div style="padding:20px; border-radius:10px; background-color:rgba(255, 248, 230, 0.2); border-left:5px solid #ffb700; margin:20px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size:24px;">⚠️</span>
                <span style="font-size:16px; font-weight:500; color:white;">Please upload a data file first to perform analysis.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
elif st.session_state.current_tab == "Visualization":
    if st.session_state.data is not None:
        render_visualization_section()
    else:
        # Modern styled warning
        st.markdown("""
        <div style="padding:20px; border-radius:10px; background-color:rgba(255, 248, 230, 0.2); border-left:5px solid #ffb700; margin:20px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size:24px;">⚠️</span>
                <span style="font-size:16px; font-weight:500; color:white;">Please upload a data file first to create visualizations.</span>
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
        <div style="padding:20px; border-radius:10px; background-color:rgba(255, 248, 230, 0.2); border-left:5px solid #ffb700; margin:20px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size:24px;">⚠️</span>
                <span style="font-size:16px; font-weight:500; color:white;">Please upload a data file first to use the AI assistant.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Modern footer with subtle gradient
st.markdown("""
<div style="margin-top: 50px; padding: 20px; border-radius: 10px; background: linear-gradient(90deg, rgba(23, 58, 130, 0.3) 0%, rgba(30, 30, 30, 0.5) 100%); text-align: center; border: 1px solid rgba(79, 139, 249, 0.2);">
    <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 10px;">
        <span style="font-size: 22px;">📊</span>
        <span style="font-weight: 600; color: white;">DataViz Analytics Dashboard</span>
    </div>
    <p style="margin: 0; font-size: 14px; color: rgba(255, 255, 255, 0.7);">
        Built with Streamlit • Modern Data Analysis • <a href="#" style="color: #4F8BF9; text-decoration: none;">Documentation</a>
    </p>
</div>
""", unsafe_allow_html=True)
