import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data():
    """Loads the DataFrames from CSV files."""
    logging.info("Attempting to load data...")
    csv_top_15_industry_path = "src/df_top_15_com_industry.csv"
    csv_precos_intradiarios_path = "src/precos_intradiarios_top_15.csv"

    if not os.path.exists(csv_top_15_industry_path) or not os.path.exists(csv_precos_intradiarios_path):
        st.warning("CSV files not found. Please run the analitics.py script first.")
        logging.warning("CSV files missing.")
        return None, None
    
    df_top_15_industry = pd.read_csv(csv_top_15_industry_path, sep=";")
    df_precos_intradiarios = pd.read_csv(csv_precos_intradiarios_path)
    logging.info("Data loaded successfully.")
    return df_top_15_industry, df_precos_intradiarios


# Function to create the industry distribution bar chart
def industry_distribution(df):
    """Creates a bar chart of industry distribution."""
    logging.info("Generating industry distribution chart...")
    if df is not None:
        logging.info(f"DataFrame content for industry_distribution():\n{df.head()}")
        logging.info(f"DataFrame types:\n{df.dtypes}")
        industry_counts = df['Industry'].value_counts()
        fig, ax = plt.subplots()
        sns.barplot(x=industry_counts.index, y=industry_counts.values, ax=ax)
        ax.set_title('Industry Distribution')
        ax.set_xlabel('Industry')
        ax.set_ylabel('Number of Companies')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        logging.info("Industry distribution chart generated successfully.")
    else:
        st.error("Dataframe is empty")
        logging.error("Dataframe is empty")

# Function to create the price time series line chart for a given ticker
def ticker_price_time_series(df, ticker_symbol):
    """Creates a time series plot for a given ticker symbol."""
    logging.info(f"Generating time series chart for {ticker_symbol}...")
    if df is not None:
        ticker_data = df[df['symbol'] == ticker_symbol]
        if ticker_data.empty:
            st.error(f"No data found for ticker: {ticker_symbol}")
            logging.error(f"No data found for ticker: {ticker_symbol}")
        else:
            logging.info(f"DataFrame content for ticker_price_time_series() - {ticker_symbol}:\n{ticker_data.head()}")
            logging.info(f"DataFrame types:\n{ticker_data.dtypes}")
            fig, ax = plt.subplots()
            ax.plot(ticker_data['datetime'], ticker_data['close'])
            ax.set_title(f'Closing Price Time Series for {ticker_symbol}')
            ax.set_xlabel('Date')
            ax.set_ylabel('Closing Price')
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
            logging.info(f"Time series chart generated successfully for {ticker_symbol}.")
    else:
        st.error("Dataframe is empty")
        logging.error("Dataframe is empty")

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
        st.error("Dataframe is empty")
        logging.error("Dataframe is empty")

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
    
    if df_top_15_industry is not None and df_precos_intradiarios is not None:
        logging.info("DataFrames loaded successfully. Proceeding to display content.")
        #Display data frames
        display_top_15_table(df_top_15_industry)
        display_intraday_prices_table(df_precos_intradiarios)

        # Industry Distribution Chart
        st.subheader("Industry Distribution of Top 15 Companies")
        industry_distribution(df_top_15_industry)

        # Ticker Price Time Series Chart
        st.subheader("Ticker Price Time Series")
        unique_tickers = df_precos_intradiarios['symbol'].unique()    
        selected_ticker = st.selectbox("Select Ticker", unique_tickers)    
        ticker_price_time_series(df_precos_intradiarios, selected_ticker)    
    else:
        logging.error("One or both DataFrames are None. Content will not be displayed.")
