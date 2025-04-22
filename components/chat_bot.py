import streamlit as st
import pandas as pd
import json
import os
from openai import OpenAI

def render_chat_bot():
    """
    Render the chat bot interface for data analysis assistance
    """
    st.header("📊 Data Analysis Assistant")
    
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
            "You are a helpful data analysis assistant with full access to the user's dataset. "
            "You're helping the user analyze their data and suggest visualizations. "
            f"The current dataset has {df.shape[0]} rows and {df.shape[1]} columns. "
            f"Here's information about the dataset structure: {json.dumps(data_info, default=str)}\n\n"
            f"You have full access to the dataset to perform computations. "
            f"The complete dataset in CSV format is provided below between triple backticks:\n"
            f"```\n{full_data_csv}\n```\n\n"
            f"You can use this data to perform calculations, find patterns, and provide detailed insights. "
            f"When the user asks questions about the data, analyze the CSV data directly."
        )
        # Reset messages when loading a new dataset or restarting
        st.session_state.messages = []
        st.session_state.system_message_added = True
    
    # Chat input
    if prompt := st.chat_input("Ask me about your data..."):
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
    st.header("📊 Data Analysis Assistant")
    st.info("This feature will allow you to chat with an AI assistant about your data.")
    
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
        
    st.write("Once configured, the assistant can help you with:")
    st.markdown("""
    - Exploring and understanding your data
    - Suggesting appropriate visualizations
    - Explaining patterns and trends
    - Answering questions about your dataset
    - Providing insights and recommendations
    """)
    
    # Example chat interface (placeholder)
    st.subheader("Example Chat")
    with st.chat_message("user"):
        st.markdown("What are the main trends in the sales data?")
    
    with st.chat_message("assistant"):
        st.markdown("""
        Based on the sales data you've uploaded, I can see several trends:
        
        1. **Product Categories**: Electronics has the highest total sales at $11,403, followed by Furniture at $5,477 and Clothing at $1,393.
        
        2. **Regional Performance**: The North region leads in sales with $6,918, followed by West with $5,462.
        
        3. **Time Trends**: Sales peaked in March and July, with a notable increase in Q2.
        
        Would you like me to create a visualization to better illustrate any of these trends?
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