import streamlit as st
import pandas as pd
import os
import plotly.express as px
import logging
from tremor_app import TremorGraphs
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data():
    """Loads the DataFrames from CSV files."""
    logging.info("Attempting to load data...")
    csv_top_15_industry_path = "src/df_top_15_com_industry.csv"
    csv_precos_intradiarios_path = "src/precos_intradiarios_top_15.csv"

    if not os.path.exists(csv_top_15_industry_path) or not os.path.exists(csv_precos_intradiarios_path):
        st.warning("CSV files not found. Please run the analytics.py script first.")
        logging.warning("CSV files missing.")
        return None, None
    
    df_top_15_industry = pd.read_csv(csv_top_15_industry_path, sep=";")
    df_precos_intradiarios = pd.read_csv(csv_precos_intradiarios_path)
    logging.info("Data loaded successfully.")
    return df_top_15_industry, df_precos_intradiarios

# Function to display the top 15 companies table
def display_top_15_table(df):
    """Displays the table of top 15 companies."""
    logging.info("Displaying top 15 companies table...")
    if df is not None:
        logging.info(f"DataFrame content for display_top_15_table():\n{df.head()}")
        logging.info(f"DataFrame types:\n{df.dtypes}")
        st.dataframe(df)
        logging.info("Top 15 companies table displayed successfully.")
    else:
        st.error("DataFrame is empty")
        logging.error("DataFrame is empty")

def display_intraday_prices_table(df):
    """Displays the intraday prices table."""
    logging.info("Displaying intraday prices table...")
    if df is not None:
        logging.info(f"DataFrame content for display_intraday_prices_table():\n{df.head()}")
        logging.info(f"DataFrame types:\n{df.dtypes}")
        st.dataframe(df)
        logging.info("Intraday prices table displayed successfully.")
    else:
        st.error("Dataframe is empty")
        logging.error("Dataframe is empty")

# Main app structure
def run_app():
    """Main function to run the Streamlit app."""
    st.title("Stock Market Analysis")
    logging.info("Starting Streamlit app...")

    # Load the DataFrames
    df_top_15_industry, df_precos_intradiarios = load_data()
    
    if df_top_15_industry is None or df_precos_intradiarios is None:
            logging.error("One or both DataFrames are None. Content will not be displayed.")
            return
    else:
        logging.info("DataFrames loaded successfully. Displaying content.")
        # Display data frames
        display_top_15_table(df_top_15_industry)
        display_intraday_prices_table(df_precos_intradiarios)
        # Industry Distribution Chart
        st.subheader("Industry Distribution of Top 15 Companies")
        TremorGraphs(df_top_15_industry, df_precos_intradiarios, "df_precos_intradiarios")

        # Ticker Price Time Series Chart
        st.subheader("Ticker Price Time Series")
        unique_tickers = df_precos_intradiarios['symbol'].unique()
        selected_ticker = st.selectbox("Select Ticker", sorted(unique_tickers))
        if selected_ticker:
            # Filter data for the selected ticker
            ticker_data = df_precos_intradiarios[df_precos_intradiarios['symbol'] == selected_ticker]
            fig = px.line(ticker_data, x='datetime', y='close', title=f'Time Series for {selected_ticker}')
            st.plotly_chart(fig)
    elif df_top_15_industry is None or df_precos_intradiarios is None:  
        logging.error("One or both DataFrames are None. Content will not be displayed.")
