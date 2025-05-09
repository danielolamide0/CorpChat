import streamlit as st
import pandas as pd
from utils.data_loader import get_data_summary
from utils.data_analysis import get_column_types

def render_data_preview():
    """
    Render the data preview section with data table and info
    """
    if st.session_state.data is None:
        st.warning("No data loaded yet. Please upload a file.")
        return
    
    # Check if we should show the save file dialog
    if st.session_state.get("show_save_dialog", False):
        # Create a modal-like popup asking user to save the file
        save_container = st.container()
        with save_container:
            st.markdown("""
            <div style="padding: 15px; background-color: rgba(28, 131, 225, 0.1); border: 1px solid rgba(28, 131, 225, 0.3); 
                border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin-top: 0;">Would you like to save this file for future use?</h3>
                <p style="color: white;">Saving will allow you to quickly reload this dataset without re-uploading.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Save File", key="save_file_yes", use_container_width=True):
                    # Check if file is already saved
                    already_saved = False
                    for saved_file in st.session_state.saved_files:
                        if saved_file["name"] == st.session_state.file_name:
                            already_saved = True
                            break
                    
                    if not already_saved:
                        # Add current file to saved files
                        st.session_state.saved_files.append({
                            "name": st.session_state.file_name,
                            "data": st.session_state.data.copy(),
                            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.success(f"File '{st.session_state.file_name}' saved successfully!")
                    else:
                        st.info(f"File '{st.session_state.file_name}' is already saved.")
                    
                    # Reset the dialog flag
                    st.session_state.show_save_dialog = False
                    st.rerun()
            
            with col2:
                if st.button("No, Skip", key="save_file_no", use_container_width=True):
                    # Reset the dialog flag
                    st.session_state.show_save_dialog = False
                    st.rerun()
    
    # Display data preview info
    st.markdown(f'<h1 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Data Preview: {st.session_state.file_name}</h1>', unsafe_allow_html=True)
    
    # Data summary
    summary = get_data_summary(st.session_state.data) or {}
    column_types = get_column_types(st.session_state.data) or {}
    
    # Summary statistics in multiple columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", summary.get('rows', 0))
    with col2:
        st.metric("Columns", summary.get('columns', 0))
    with col3:
        st.metric("Missing Values", summary.get('missing_values', 0))
    
    # Display data table with options
    st.markdown('<h3 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Data Table</h3>', unsafe_allow_html=True)
    
    # Search and filter options
    search_term = st.text_input("Search in data", placeholder="Enter text to search across all columns")
    
    # Column selection for display
    all_columns = st.session_state.data.columns.tolist()
    
    with st.expander("Column Selection", expanded=False):
        selected_columns = st.multiselect(
            "Select columns to display",
            options=all_columns,
            default=all_columns[:10] if len(all_columns) > 10 else all_columns
        )
    
    # Number of rows to display
    num_rows = st.slider("Rows to display", min_value=5, max_value=100, value=10, step=5)
    
    # Filter data based on search term
    filtered_data = st.session_state.data
    if search_term:
        # Create a mask for rows containing the search term
        matches = pd.Series(False, index=filtered_data.index)
        for col in filtered_data.columns:
            matches |= filtered_data[col].astype(str).str.contains(search_term, case=False, na=False)
        filtered_data = filtered_data[matches]
    
    # Display data table
    if not selected_columns:
        st.warning("Please select at least one column to display")
    else:
        if filtered_data.empty and search_term:
            st.warning(f"No results found for '{search_term}'")
        else:
            # Display the data with selected columns
            display_data = filtered_data[selected_columns].head(num_rows)
            st.dataframe(display_data, use_container_width=True)
            
            # Show how many rows are being displayed
            total_rows = len(filtered_data)
            row_count = summary.get('rows', 0)
            if search_term and total_rows != row_count:
                st.info(f"Showing {min(num_rows, total_rows)} of {total_rows} rows matching '{search_term}'")
            else:
                st.info(f"Showing {min(num_rows, total_rows)} of {total_rows} total rows")
    
    # Column information
    st.markdown('<h3 style="color: white; font-family: \'Space Grotesk\', sans-serif;">Column Information</h3>', unsafe_allow_html=True)
    
    # Prepare column info as a dataframe
    column_info = []
    for col in all_columns:
        non_null_count = st.session_state.data[col].count()
        null_count = st.session_state.data[col].isna().sum()
        unique_count = st.session_state.data[col].nunique()
        
        col_info = {
            "Column": col,
            "Type": column_types.get(col, "unknown"),
            "Non-Null Count": non_null_count,
            "Null Count": null_count,
            "Unique Values": unique_count,
            "% Missing": f"{(null_count / len(st.session_state.data) * 100):.1f}%"
        }
        column_info.append(col_info)
    
    column_info_df = pd.DataFrame(column_info)
    st.dataframe(column_info_df, use_container_width=True)
