import streamlit as st
import pandas as pd 
def load_data(filepath):
    """Loads data from a CSV file into a pandas DataFrame."""
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the file: {e}")
        return None

def display_table(df):
    """Displays the table data using st.write()."""
    st.write(df)  # Display the DataFrame using st.write()
