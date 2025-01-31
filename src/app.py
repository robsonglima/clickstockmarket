import streamlit as st
import pandas as pd
import os
import plotly.express as px
import logging
from analitics import consultar_precos_intradiarios_yf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to Load the DataFrames
def load_data():
    """Loads the DataFrames from CSV files."""
    logging.info("Attempting to load data...")
    csv_top_15_industry_path = "src/df_top_15_com_industry.csv"
    csv_precos_intradiarios_path = "src/precos_intradiarios_top_15.csv"

    if not os.path.exists(csv_top_15_industry_path) or not os.path.exists(csv_precos_intradiarios_path):
        st.warning("Arquivos CSV não encontrados. Por favor, execute o script analytics.py primeiro.")
        logging.warning("CSV files missing.")
        return None, None
    
    df_top_15_industry = pd.read_csv(csv_top_15_industry_path, sep=";")
    df_precos_intradiarios = pd.read_csv(csv_precos_intradiarios_path)
    logging.info("Data loaded successfully.")
    return df_top_15_industry, df_precos_intradiarios

# Functions to display tables
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
        st.error("DataFrame vazio")
        logging.error("DataFrame vazio")

def display_intraday_prices_table(df):
    """Displays the intraday prices table."""
    logging.info("Displaying intraday prices table...")
    if df is not None:
        logging.info(f"DataFrame content for display_intraday_prices_table():\n{df.head()}")
        logging.info(f"DataFrame types:\n{df.dtypes}")
        st.dataframe(df)
        logging.info("Intraday prices table displayed successfully.")
    else:
        st.error("Dataframe vazio")
        logging.error("Dataframe vazio")

# Function to run the app
# Main app structure
def run_app(df_top_15_industry, df_precos_intradiarios, tickers_top_15):
    """Main function to run the Streamlit app."""
    st.title("Análise do Mercado de Ações")
    logging.info("Starting Streamlit app...")

    if df_top_15_industry is not None and df_precos_intradiarios is not None:
        logging.info("DataFrames loaded successfully. Displaying content.")
        
        if st.button("Update Data"):
            try:
                # Update data from yfinance
                logging.info("Updating data from yfinance...")
                new_df_precos_intradiarios = consultar_precos_intradiarios_yf(tickers_top_15,"15min","1d")
                if new_df_precos_intradiarios is not None:
                    df_precos_intradiarios = new_df_precos_intradiarios
                    st.success("Dados atualizados com sucesso!")
                    logging.info("Data updated successfully.")
                else:
                    st.error("Falha ao atualizar os dados.")
                    logging.error("Falha ao atualizar os dados.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao atualizar os dados: {e}")
                logging.error(f"Ocorreu um erro ao atualizar os dados: {e}")
                
        st.subheader("Distribuição por Setor das 15 Maiores Empresas")
        st.subheader("Série Temporal do Preço do Ticker")
        unique_tickers = df_precos_intradiarios['symbol'].unique()
        selected_ticker = st.selectbox("Selecione o Ticker", sorted(unique_tickers))
        if selected_ticker:
            # Filter data for the selected ticker
            ticker_data = df_precos_intradiarios[df_precos_intradiarios['symbol'] == selected_ticker].copy()
            # Calculate line color based on first and last price
            first_price = ticker_data['close'].iloc[0]
            last_price = ticker_data['close'].iloc[-1]
            if last_price >= first_price:
                line_color = 'green'
            else:
                line_color = 'red'
            fig = px.line(ticker_data, x='datetime', y='close', title=f'Time Series for {selected_ticker}', color_discrete_sequence=[line_color])
            st.plotly_chart(fig)

    else:
        logging.error("One or both DataFrames are None. Content will not be displayed.")

