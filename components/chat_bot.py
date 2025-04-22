import streamlit as st
import pandas as pd
import json
import os
from openai import OpenAI

def render_chat_bot():
    """
    Render the chat bot interface for data analysis assistance
    """
    st.header("📊 Business Intelligence Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
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
            f"KEY INSTRUCTIONS:\n"
            f"1. Be extremely concise - executives value brevity\n"
            f"2. Prioritize key insights over exhaustive details\n"
            f"3. Present information in a structured, scannable format\n"
            f"4. Use professional business language\n"
            f"5. Recommend clear actions when appropriate\n"
            f"6. Include only relevant data points\n"
            f"7. Present insights with confidence and authority\n"
            f"When analyzing numerical data, round to 2 decimal places unless precision is critical."
        )
        # Reset messages when loading a new dataset or restarting
        st.session_state.messages = []
        st.session_state.system_message_added = True
    
    # Chat input
    if prompt := st.chat_input("Ask a business question about your data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
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
                
                # Stream the response
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
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
    st.header("📊 Business Intelligence Assistant")
    st.info("This AI-powered assistant provides concise business insights and actionable recommendations from your data.")
    
    # Check if we have data loaded
    if st.session_state.data is None:
        st.warning("Please upload a data file first to use the chat assistant.")
        return
        
    # Display information about the dataset
    try:
        df = st.session_state.data
        st.subheader("Current Dataset")
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
    - Generate executive-ready reports
    - Recommend data-driven business strategies
    """)
    
    # Example chat interface (placeholder)
    st.subheader("Example Chat")
    with st.chat_message("user"):
        st.markdown("What age group represents our primary customer base?")
    
    with st.chat_message("assistant"):
        st.markdown("""
        **Key Customer Demographic: 25-34 age group**
        
        Primary customer base breakdown:
        • 25-34: 30% (8 customers)
        • 18-24: 22% (6 customers)
        • 35-44: 22% (6 customers)
        
        **Recommended Action:**
        Focus marketing resources on the 25-34 demographic while developing retention strategies for the younger segment.
        """)
    
    # API Key Setup
    st.subheader("API Setup")
    st.warning("To enable this feature, you'll need to provide an OpenAI API key.")
    
    api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key to enable the chat assistant")
    if api_key and api_key.strip() != "":
        if st.button("Save API Key"):
            os.environ["OPENAI_API_KEY"] = api_key
            st.session_state.openai_api_key_available = True
            st.success("API key saved successfully!")
            st.rerun()