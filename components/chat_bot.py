import streamlit as st
import pandas as pd
import json
import os
import re
from openai import OpenAI
from utils.data_visualization import (
    create_bar_chart, create_line_chart, create_scatter_plot,
    create_histogram, create_pie_chart, create_heatmap,
    create_box_plot, create_correlation_heatmap
)

def detect_visualization_request(prompt):
    """
    Detect if a user prompt is requesting a visualization
    
    Returns:
    - (chart_type, params) tuple if visualization is requested, (None, None) otherwise
    """
    # Common patterns for visualization requests
    patterns = {
        'bar chart': r'(?:create|show|generate|display).*(?:bar chart|bar graph|column chart)',
        'line chart': r'(?:create|show|generate|display).*(?:line chart|line graph|trend)',
        'scatter plot': r'(?:create|show|generate|display).*(?:scatter plot|scatter graph|scatterplot)',
        'histogram': r'(?:create|show|generate|display).*(?:histogram|distribution)',
        'pie chart': r'(?:create|show|generate|display).*(?:pie chart|pie graph)',
        'heatmap': r'(?:create|show|generate|display).*(?:heatmap|heat map|correlation map)',
        'box plot': r'(?:create|show|generate|display).*(?:box plot|boxplot|box and whisker)',
        'correlation': r'(?:create|show|generate|display).*(?:correlation matrix|correlation heatmap)'
    }
    
    # Check for matches
    for chart_type, pattern in patterns.items():
        if re.search(pattern, prompt, re.IGNORECASE):
            return chart_type, None
    
    return None, None

def create_visualization_from_response(response, chart_type=None):
    """
    Attempt to create a visualization based on the AI response or detected chart type
    
    Parameters:
    - response: The AI response text
    - chart_type: Previously detected chart type (optional)
    
    Returns:
    - Plotly figure or None if no visualization could be created
    """
    df = st.session_state.data
    
    # If chart type wasn't detected in the prompt, try to detect it in the response
    if chart_type is None:
        # Look for specific visualization keywords in the response
        if re.search(r'bar chart|bar graph|column chart', response, re.IGNORECASE):
            chart_type = 'bar chart'
        elif re.search(r'line chart|line graph|trend line', response, re.IGNORECASE):
            chart_type = 'line chart'
        elif re.search(r'scatter plot|scatter graph|scatterplot', response, re.IGNORECASE):
            chart_type = 'scatter plot'
        elif re.search(r'histogram|distribution chart', response, re.IGNORECASE):
            chart_type = 'histogram'
        elif re.search(r'pie chart|pie graph', response, re.IGNORECASE):
            chart_type = 'pie chart'
        elif re.search(r'heatmap|heat map', response, re.IGNORECASE):
            chart_type = 'heatmap'
        elif re.search(r'box plot|boxplot', response, re.IGNORECASE):
            chart_type = 'box plot'
        elif re.search(r'correlation matrix|correlation heatmap', response, re.IGNORECASE):
            chart_type = 'correlation'
    
    if chart_type is None:
        return None
    
    # Extract column names from the response or use defaults
    numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    categorical_columns = [col for col in df.columns if not pd.api.types.is_numeric_dtype(df[col])]
    
    if not numeric_columns:
        return None  # Can't create visualization without numeric data
    
    # Default to first columns if we can't extract specific ones
    x_column = categorical_columns[0] if categorical_columns else numeric_columns[0]
    y_column = numeric_columns[0]
    
    # Try to extract column names from the response using regex
    # This is a simplified approach - in a production environment you'd want more robust parsing
    columns_mentioned = []
    for col in df.columns:
        if re.search(r'\b' + re.escape(col) + r'\b', response, re.IGNORECASE):
            columns_mentioned.append(col)
    
    # Use mentioned columns if found
    if len(columns_mentioned) >= 2:
        # Prefer categorical for x and numeric for y
        x_candidates = [col for col in columns_mentioned if col in categorical_columns]
        y_candidates = [col for col in columns_mentioned if col in numeric_columns]
        
        if x_candidates:
            x_column = x_candidates[0]
        else:
            x_column = columns_mentioned[0]
            
        if y_candidates:
            y_column = y_candidates[0]
        else:
            y_column = columns_mentioned[1]
    elif len(columns_mentioned) == 1:
        # If only one column is mentioned, use it as y for most charts
        if columns_mentioned[0] in numeric_columns:
            y_column = columns_mentioned[0]
        else:
            x_column = columns_mentioned[0]
    
    # Create visualization based on chart type
    try:
        title = f"Auto-generated {chart_type.title()} for {x_column} and {y_column}"
        
        if chart_type == 'bar chart':
            return create_bar_chart(df, x_column, y_column, title=title)
        
        elif chart_type == 'line chart':
            return create_line_chart(df, x_column, [y_column], title=title)
        
        elif chart_type == 'scatter plot':
            return create_scatter_plot(df, x_column, y_column, title=title)
        
        elif chart_type == 'histogram':
            return create_histogram(df, y_column, title=f"Distribution of {y_column}")
        
        elif chart_type == 'pie chart':
            return create_pie_chart(df, x_column, y_column, title=f"Proportion of {y_column} by {x_column}")
        
        elif chart_type == 'heatmap':
            if len(numeric_columns) >= 2:
                return create_heatmap(df, x_column, numeric_columns[1], y_column, title=title)
            return None
        
        elif chart_type == 'box plot':
            return create_box_plot(df, x_column, y_column, title=title)
        
        elif chart_type == 'correlation':
            return create_correlation_heatmap(df, title="Correlation Matrix")
        
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        return None
    
    return None

def render_chat_bot():
    """
    Render the chat bot interface for data analysis assistance
    """
    st.markdown('<h1 style="color: white;">📊 Business Intelligence Assistant</h1>', unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages with white text for better visibility on dark background
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f'<div style="color: white;">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Check if we have data loaded
    if st.session_state.data is None:
        st.warning("Please upload a data file first to use the chat assistant.")
        return
    
    # Check if OpenAI API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key == "":
        st.warning(
            "OpenAI API key not found. Please provide your API key to use the chat assistant."
        )
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key and api_key.strip() != "":
            os.environ["OPENAI_API_KEY"] = api_key
            st.session_state.openai_api_key_available = True
            st.success("API key set successfully!")
            st.rerun()
        else:
            return
    
    # Add a system message to help the model understand the context
    if "system_message_added" not in st.session_state:
        # Create data summary for the bot's context
        df = st.session_state.data
        data_info = {
            "columns": list(df.columns),
            "data_types": {col: str(df[col].dtype) for col in df.columns},
            "sample_data": df.head(5).to_dict(orient="records"),
            "shape": df.shape,
            "summary_stats": {
                col: {
                    "mean": float(df[col].mean()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                    "min": float(df[col].min()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                    "max": float(df[col].max()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                }
                for col in df.columns
                if pd.api.types.is_numeric_dtype(df[col])
            }
        }
        
        # Convert DataFrame to CSV string for the full dataset
        full_data_csv = df.to_csv(index=False)
        
        # Add system message (not shown to user)
        st.session_state.system_message = (
            "You are a professional business intelligence analyst providing concise, actionable insights to executives. "
            "Maintain a business-focused, direct communication style appropriate for busy professionals. "
            f"The current dataset has {df.shape[0]} rows and {df.shape[1]} columns. "
            f"Dataset structure: {json.dumps(data_info, default=str)}\n\n"
            f"The complete dataset is provided below:\n"
            f"```\n{full_data_csv}\n```\n\n"
            f"VISUALIZATION CAPABILITIES:\n"
            f"You can create visualizations for users when they request them. If a user asks for a chart or graph, "
            f"clearly recommend a specific visualization type (bar chart, line chart, scatter plot, histogram, pie chart, "
            f"heatmap, box plot, or correlation matrix) and mention which columns should be used. "
            f"When recommending visualizations, always specify column names exactly as they appear in the dataset. "
            f"The system will automatically generate the visualization based on your recommendation.\n\n"
            f"KEY INSTRUCTIONS:\n"
            f"1. Be extremely concise - executives value brevity\n"
            f"2. Prioritize key insights over exhaustive details\n"
            f"3. Present information in a structured, scannable format\n"
            f"4. Use professional business language\n"
            f"5. Recommend clear actions when appropriate\n"
            f"6. Include only relevant data points\n"
            f"7. Present insights with confidence and authority\n"
            f"8. When users ask for visualizations, recommend specific chart types and columns\n"
            f"When analyzing numerical data, round to 2 decimal places unless precision is critical."
        )
        # Reset messages when loading a new dataset or restarting
        st.session_state.messages = []
        st.session_state.system_message_added = True
    
    # Chat input
    if prompt := st.chat_input("Ask a business question about your data..."):
        # Check if user is requesting a visualization directly
        vis_type, vis_params = detect_visualization_request(prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message with white text for better visibility
        with st.chat_message("user"):
            st.markdown(f'<div style="color: white;">{prompt}</div>', unsafe_allow_html=True)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Get response from OpenAI (with error handling)
                client = OpenAI()
                stream = client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                    messages=[
                        {"role": "system", "content": st.session_state.system_message},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ],
                    stream=True,
                )
                
                # Stream the response with white text
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(f'<div style="color: white;">{full_response}▌</div>', unsafe_allow_html=True)
                
                message_placeholder.markdown(f'<div style="color: white;">{full_response}</div>', unsafe_allow_html=True)
                
                # Try to generate visualization based on:
                # 1. Direct visualization request from user
                # 2. Or visualization mentioned in the AI response
                fig = None
                if vis_type:
                    # Direct request - generate visualization based on user request
                    fig = create_visualization_from_response(full_response, vis_type)
                else:
                    # Check if AI response mentions visualization
                    fig = create_visualization_from_response(full_response)
                
                # Display the visualization if one was created
                if fig is not None:
                    st.write("**Generated Visualization:**")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add this visualization to the saved visualizations
                    # Extract a title from the chart or use a default
                    title = fig.layout.title.text if hasattr(fig.layout, 'title') and hasattr(fig.layout.title, 'text') else "Chat-generated visualization"
                    if not title or title == "":
                        title = "Chat-generated visualization"
                    
                    # Store in session state 
                    st.session_state.visualizations.append({
                        "type": "chat_generated",
                        "title": title,
                        "figure": fig
                    })
                    
                    # Let the user know the visualization was saved
                    st.info("This visualization has been saved to your Visualization tab.")
                
            except Exception as e:
                error_message = f"Error: {str(e)}"
                message_placeholder.error(error_message)
                full_response = error_message
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Add option to clear chat history
    if st.session_state.messages and st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

def render_placeholder_chat_bot():
    """
    Render a placeholder for the chat bot before API keys are set up
    """
    st.markdown('<h1 style="color: white;">📊 Business Intelligence Assistant</h1>', unsafe_allow_html=True)
    st.info("This AI-powered assistant provides concise business insights and actionable recommendations from your data.")
    
    # Check if we have data loaded
    if st.session_state.data is None:
        st.warning("Please upload a data file first to use the chat assistant.")
        return
        
    # Display information about the dataset
    try:
        df = st.session_state.data
        st.markdown('<h3 style="color: white;">Current Dataset</h3>', unsafe_allow_html=True)
        st.write(f"Using dataset: {st.session_state.file_name}")
        st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        
        # Show sample of the data
        st.write("Sample of your data:")
        st.dataframe(df.head(3))
    except Exception as e:
        st.error(f"Error displaying data preview: {str(e)}")
        
    st.write("This business intelligence assistant will help you:")
    st.markdown("""
    - Extract actionable business insights
    - Identify market opportunities and risks
    - Track KPIs and performance metrics
    - Create visualizations directly from your questions
    - Recommend data-driven business strategies
    """)
    
    # Example chat interface (placeholder) with white text for better visibility
    st.markdown('<h3 style="color: white;">Example Chat</h3>', unsafe_allow_html=True)
    with st.chat_message("user"):
        st.markdown('<div style="color: white;">What age group represents our primary customer base and can you create a visualization?</div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        st.markdown("""
        <div style="color: white;">
        <strong>Key Customer Demographic: 25-34 age group</strong>
        
        Primary customer base breakdown:
        • 25-34: 30% (8 customers)
        • 18-24: 22% (6 customers)
        • 35-44: 22% (6 customers)
        
        <strong>Recommended Action:</strong>
        Focus marketing resources on the 25-34 demographic while developing retention strategies for the younger segment.
        
        <strong>Visualization:</strong>
        I recommend a bar chart showing customer count by age group. This will help visualize the distribution of your customer base across different demographics.
        </div>
        """, unsafe_allow_html=True)
        
    # Show example visualization below the chat
    st.write("**Generated Visualization:**")
    st.info("Visualizations will appear here when you ask for them in the chat.")
    
    # API Key Setup
    st.markdown('<h3 style="color: white;">API Setup</h3>', unsafe_allow_html=True)
    st.warning("To enable this feature, you'll need to provide an OpenAI API key.")
    
    api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key to enable the chat assistant")
    if api_key and api_key.strip() != "":
        if st.button("Save API Key"):
            os.environ["OPENAI_API_KEY"] = api_key
            st.session_state.openai_api_key_available = True
            st.success("API key saved successfully!")
            st.rerun()