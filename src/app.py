import streamlit as st
import pandas as pd
import os
import yfinance as yf
import plotly.express as px
import logging
from analitics import consultar_precos_intradiarios_yf

# Configurar Logging - em testes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def show_company_info(company_data, ticker):
    """
    Exibe informações da empresa e um gráfico de linha para um determinado ticker.

    Args:
        company_data (dict): Um dicionário contendo os dados da empresa.
        ticker (str): O símbolo do ticker.
    """
    st.subheader(f"Informaçoes da empresa: {ticker}")
    
    if "profile" in company_data and company_data["profile"] != "N/A":
        st.write(f"**Perfil:** {company_data['profile']}")
    
    if "market" in company_data and company_data["market"] != "N/A":
        st.write(f"**Mercado:** {company_data['market']}")

    if "volume" in company_data and company_data["volume"] != "N/A":
        st.write(f"**Volume:** {company_data['volume']}")
    
    if "history" in company_data and not company_data["history"].empty:
        # Obtém o último preço
        last_price = company_data["history"]["Close"].iloc[-1]
        
        #Exibe o último preço
        st.write(f"**Preço Atual:** {last_price}")
        
        #Gera o grafico
        fig = px.line(
            company_data["history"],
            x=company_data["history"].index, 
            y="Close",
            title=f"Historical Prices for {ticker}",
        ) #Gera o grafico
        st.plotly_chart(fig)
    



# def para carregar Dataframes
def load_data():
    """
    Loads the DataFrames from CSV files and extracts the top 15 tickers.

    Returns:
        tuple: A tuple containing the df_top_15_industry DataFrame,
               the df_precos_intradiarios DataFrame, and a list of
               the top 15 tickers. or list with tickers.
    """
    logging.info("Attempting to load data...")
    csv_top_15_industry_path = "src/df_top_15_com_industry.csv"

    csv_precos_intradiarios_path = "src/precos_intradiarios_top_15.csv"

    if not os.path.exists(csv_top_15_industry_path) or not os.path.exists(csv_precos_intradiarios_path):
        st.warning("Arquivos CSV não encontrados. Por favor, execute o script analytics.py primeiro.")
        logging.warning("CSV files missing.")
        return None, None
    if not os.path.exists(csv_precos_intradiarios_path):
        return None, None, None

    df_top_15_industry = pd.read_csv(csv_top_15_industry_path, sep=";")
    try:
        df_precos_intradiarios = pd.read_csv(csv_precos_intradiarios_path)
    except pd.errors.EmptyDataError:
        return None, None, None
    
    
    logging.info("Data loaded successfully.")




    
    
    tickers_top_15 = df_precos_intradiarios['symbol'].unique().tolist() if not df_precos_intradiarios.empty else []

    return df_top_15_industry, df_precos_intradiarios, tickers_top_15


def update_data_frames(tickers, interval, period):
    """
    Updates the DataFrames by consulting intraday prices for the given tickers.

    Args:
        tickers (list): A list of stock tickers to update.
        interval (string): the interval of time to consult
        period (string): the period of time to consult
    Returns:
        tuple: A tuple containing the df_top_15_industry DataFrame, and the 
               updated df_precos_intradiarios DataFrame.
    """
    logging.info("Attempting to update data frames...")
    if not tickers:
        logging.error("Could not retrieve tickers.")
        return None
    

    df_precos_intradiarios = consultar_precos_intradiarios_yf(tickers, interval, period)
    
    if df_precos_intradiarios.empty:
        return None
    else:
        # Save the updated df_precos_intradiarios to the CSV file
        df_precos_intradiarios.to_csv("src/precos_intradiarios_top_15.csv", index=False)
        
        logging.info("Data frames updated successfully.")
        return df_precos_intradiarios

    

# def para montar tabelas
# def para montar tabela - top 15 companies table
def display_top_15_table(df):
    """Displays the table of top 15 companies."""
    logging.info("Displaying top 15 companies table...")
    if df is not None:
        logging.info(f"DataFrame content for display_top_15_table():\n{df.head()}")
        logging.info(f"DataFrame types:\n{df.dtypes}")
        st.dataframe(df)
        logging.info("Top 15 companies table displayed successfully.")
    else: # se o df for vazio
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
    else: #se o dataframe for vazio
        st.error("Dataframe vazio")
        logging.error("Dataframe vazio")

# def para rodar o app
# Main app structure
def run_app(df_top_15_industry, df_precos_intradiarios, tickers_top_15):
    """Main function to run the Streamlit app."""
    st.title("Análise do Mercado de Ações")
    logging.info("Starting Streamlit app...")
    
    
    tickers_list = df_precos_intradiarios['symbol'].unique().tolist() if not df_precos_intradiarios.empty else []

    
    if df_top_15_industry is not None and df_precos_intradiarios is not None:        
        logging.info("DataFrames loaded successfully. Displaying content.")
        
        
        if st.button("Atualizar"):
            df_precos_intradiarios = update_data_frames(tickers_list, "1d", "1mo")
            
            if  df_precos_intradiarios is not None and df_top_15_industry is not None:
                st.success("Dados atualizados com sucesso!")
                logging.info("Data updated successfully.")
            else :
                st.error("Falha ao atualizar os dados.")
                logging.error("Falha ao atualizar os dados.")
            
                
        # grafico de linha - Time Series
        st.subheader("Série Temporal do Preço do Ticker") #Time Series
        unique_tickers = df_precos_intradiarios['symbol'].unique()
        selected_ticker = st.selectbox("Selecione o Ticker", sorted(unique_tickers)) #select box
        if selected_ticker:
            # Filtra os dados para o ticker selecionado
            ticker_data = df_precos_intradiarios[df_precos_intradiarios['symbol'] == selected_ticker].copy()
            # Calcula a cor da linha com base no primeiro e último preço
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

def show_comparative_graph(selected_tickers, start_date, end_date):
    """
    Displays a comparative line graph of the closing prices of selected tickers.

    Args:
        selected_tickers (list): A list of ticker symbols.
        start_date (date): The start date for historical prices.
        end_date (date): The end date for historical prices.
    """
    if not selected_tickers:
        return

    # Exclude BOVA11.SA from comparative analysis
    tickers_for_comparison = [t for t in selected_tickers if t != "BOVA11.SA"]

    if not tickers_for_comparison:
        if "BOVA11.SA" in selected_tickers:
             # Fetch data for BOVA11.SA
            company_data = get_company_data("BOVA11.SA", start_date, end_date)
            # Display information for BOVA11.SA
            show_company_info(company_data, "BOVA11.SA")
        return
    
    if len(tickers_for_comparison) > 1:
        # Fetch historical data for each ticker
        all_data = {}
        for ticker in tickers_for_comparison:
            try:
                data = yf.download(ticker, start=start_date, end=end_date)
                if not data.empty:
                    data['pct_change'] = data['Close'].pct_change() * 100
                    data['normalized'] = (100 + data['pct_change'].cumsum())
                    all_data[ticker] = data['normalized']
            except Exception as e:
                st.error(f"Error fetching data for {ticker}: {e}")
        
        # Create comparative graph
        if all_data:
            comparison_df = pd.DataFrame(all_data)
            fig = px.line(comparison_df, title='Comparação de Preços Normalizados')
            fig.update_layout(xaxis_title="Data", yaxis_title="Preço Normalizado (%)")
            st.plotly_chart(fig)
    elif len(tickers_for_comparison) == 1:
            st.write("Selecione dois ou mais tickers para comparar")
