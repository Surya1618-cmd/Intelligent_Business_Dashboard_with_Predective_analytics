import streamlit as st
import pandas as pd
import sqlite3

def process_file(uploaded_file):
    file_name = uploaded_file.name
    st.success(f"File {file_name} uploaded successfully!")
    
    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Display data preview
        st.write("### Data Preview:")
        st.dataframe(df.head())
        
        # Data validation (handling missing values, checking duplicates)
        if df.isnull().values.any():
            st.warning("Warning: The dataset contains missing values!")
            df.fillna("Unknown", inplace=True)  # Replace missing values with 'Unknown'
        
        if df.duplicated().any():
            st.warning("Warning: The dataset contains duplicate rows!")
            df.drop_duplicates(inplace=True)  # Remove duplicates
        
        # Store data in SQLite database
        conn = sqlite3.connect("database/business_data.db")
        table_name = file_name.split(".")[0]  # Use filename as table name
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        
        st.success(f"Data stored successfully in table: {table_name}")
    except Exception as e:
        st.error(f"Error processing file: {e}")

def main():
    st.title("📂 Upload Your Business Data")
    st.write("Upload CSV or Excel files to store them in the database.")
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        process_file(uploaded_file)

if __name__ == "__main__":
    main()