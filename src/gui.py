import streamlit as st
from table_app import display_table
from app import main as app_main

# --- Sidebar navigation ---
st.sidebar.title("Menu")
page = st.sidebar.radio(
    "Go to", ["Home", "Table", "App"]
)  # Updated menu options and page names

# --- Page Content ---
if page == "Home":
    st.title("Stock Analysis")  # Changed title
    st.write(
        """
        Welcome to the Stock Analysis app!
        
        This application offers a suite of tools for in-depth stock market data analysis. 
        You can investigate stock performance, interact with detailed tables, and much more.
        
        Use the menu on the left to navigate through the different sections of the application.
        """
    )
    if st.button("Click Me"):
        st.write("Home button clicked!")

elif page == "Table":
    # Call to display the table
    display_table()

elif page == "App":
    # Call to run the content of app.py
    app_main()