import streamlit as st
import pandas as pd
import os
import plotly.express as px
from analitics import consultar_precos_intradiarios_yf

# Configurar Logging - em testes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def show_company_info(company_data, ticker):
    """Exibe informações da empresa e um gráfico de linha para um determinado ticker.

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
        last_price = company_data["history"]["Close"].iloc[-1]
        st.write(f"**Preço Atual:** {last_price}")

        fig = px.line(
            company_data["history"],
            x=company_data["history"].index, 
            y="Close",
            title=f"Historical Prices for {ticker}",
        ) #Gera o grafico
        st.plotly_chart(fig)

def load_data(interval = "1d", period="1y"):
    """Carrega os DataFrames a partir de arquivos CSV e extrai os 15 principais tickers.

    Returns:
        tuple: Uma tupla contendo o DataFrame df_top_15_industry,
               o DataFrame df_precos_intradiarios e uma lista dos
               15 principais tickers. ou lista com os tickers.
    """
    logging.info("Attempting to load data...")
    csv_top_15_industry_path = "src/df_top_15_com_industry.csv"

    csv_precos_intradiarios_path = "src/precos_intradiarios_top_15.csv"

    if not os.path.exists(csv_top_15_industry_path):
        st.warning("Arquivos CSV não encontrados")
        logging.warning("CSV files missing.")
        return None, None, None        

    if not os.path.exists(csv_precos_intradiarios_path):
        logging.warning(f"File {csv_precos_intradiarios_path} not found.")
        st.warning("Arquivos CSV de precos nao encontrados. Por favor, execute o script analytics.py primeiro.")        
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
    """Atualiza os DataFrames consultando os preços intradiários para os tickers fornecidos.

    Args:
        tickers (list): Uma lista de tickers de ações para atualizar.
        interval (string): o intervalo de tempo para consultar
        period (string): o período de tempo para consultar
    Returns:
        tuple: Uma tupla contendo o DataFrame df_top_15_industry e o
               DataFrame df_precos_intradiarios atualizado.
    """    
    logging.info("Attempting to update data frames...")
    if not tickers:
        logging.error("Could not retrieve tickers.")
        return None
    
    df_precos_intradiarios = consultar_precos_intradiarios_yf(tickers, interval, period)   

    if df_precos_intradiarios.empty:
        st.warning("Sem dados retornados para o período selecionado. Por favor, altere a data ou período.")    
        # Save the updated df_precos_intradiarios to the CSV file
        df_precos_intradiarios.to_csv("src/precos_intradiarios_top_15.csv", index=False)
        
        logging.info("Data frames updated successfully.")
        return df_precos_intradiarios

# def para montar tabela - top 15 companies table
def display_top_15_table(df):
    """Exibe a tabela das 15 principais empresas."""
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
    """Exibe a tabela de preços intradiários."""
    logging.info("Displaying intraday prices table...")
    if df is not None:
        logging.info(f"DataFrame content for display_intraday_prices_table():\n{df.head()}")
        logging.info(f"DataFrame types:\n{df.dtypes}")
        st.dataframe(df)
        logging.info("Intraday prices table displayed successfully.")
    else: #se o dataframe for vazio
        st.error("Dataframe vazio")
        logging.error("Dataframe vazio")
# Main app structure
def run_app(df_top_15_industry, df_precos_intradiarios, tickers_top_15):
    """Função principal para executar o aplicativo Streamlit.

    Returns:
    list: uma lista com 9 valores."""
    if df_precos_intradiarios.empty:
        return [None, None, None, None, None, None, None, None, None]

    # calcualr a media daily variation
    daily_variation = df_precos_intradiarios.groupby('symbol')['close'].diff().mean()
    avg_daily_variation = daily_variation
    avg_daily_variation_str = "+" if avg_daily_variation >= 0 else "-"
    avg_daily_variation_type = "positive" if avg_daily_variation >= 0 else "negative"

    # Calculate the average volume
    avg_volume = df_precos_intradiarios['volume'].mean()
    avg_volume_diff = df_precos_intradiarios['volume'].diff().mean()
    avg_volume_str = "+" if avg_volume_diff >= 0 else "-"
    avg_volume_type = "positive" if avg_volume_diff >= 0 else "negative"

    # Calculate standard deviation of daily variation
    std_dev_daily_variation = df_precos_intradiarios.groupby('symbol')['close'].diff().std()
    std_dev_daily_variation_diff = std_dev_daily_variation.mean()
    std_dev_daily_variation_str = "+" if std_dev_daily_variation_diff >= 0 else "-"
    std_dev_daily_variation_type = "positive" if std_dev_daily_variation_diff >= 0 else "negative"
    
    st.title("Analise do Mercado de Ações")
    tickers_list = df_precos_intradiarios['symbol'].unique().tolist() if not df_precos_intradiarios.empty else []
    
    
    if df_top_15_industry is not None and df_precos_intradiarios is not None:        
        logging.info("DataFrames loaded successfully. Displaying content.")
        
        
        if st.button("Atualizar"):                
            df_precos_intradiarios = update_data_frames(tickers_list, "1d", "1y")
            st.success("Dados atualizados com sucesso!")
        # gráfico de linha - Time Series
        unique_tickers = df_precos_intradiarios['symbol'].unique()
        selected_ticker = st.selectbox("Selecione o Ticker", sorted(unique_tickers))
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

            logging.info("Starting Streamlit app...")
            st.plotly_chart(fig)

    else:
        logging.error("One or both DataFrames are None. Content will not be displayed.")

def show_comparative_graph(selected_tickers, start_date, end_date):
    """
    Exibe um gráfico de linha comparativo dos preços de fechamento dos tickers selecionados.    

    Args:
        selected_tickers (list): Uma lista de símbolos de ticker.
        start_date (date): A data de início para os preços históricos.
        end_date (date): A data de término para os preços históricos.
    """
    if not selected_tickers:
        return
    # Adiciona o disclaime dos precos normalizados
    st.write('Disclaimer: Este gráfico exibe os preços normalizados das ações selecionadas. A normalização permite comparar o desempenho relativo de diferentes ativos, ajustando seus preços para começar em 100 no início do período. Um valor acima de 100 indica valorização, enquanto abaixo de 100 indica desvalorização. Esta metodologia facilita a visualização da trajetória dos ativos, independentemente de seus preços iniciais.')
    

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

        #  graficos comparativo
        if all_data:
            comparison_df = pd.DataFrame(all_data)
            fig = px.line(comparison_df, title='Comparação de Preços Normalizados')
            fig.update_layout(xaxis_title="Data", yaxis_title="Preço Normalizado (%)")
            st.plotly_chart(fig)
    elif len(tickers_for_comparison) == 1:
        st.write("Selecione dois ou mais tickers para comparar")

def analyze_trend_initiation(selected_tickers, start_date, end_date):
    """Analisa o início de tendências de alta e baixa para os tickers selecionados.

    Args:
        selected_tickers (list): Uma lista de símbolos de ticker.
        start_date (date): A data de início para a busca de dados.
        end_date (date): A data de término para a busca de dados.

    Returns:
        tuple: Uma tupla contendo dois dicionários:
               - downward_trends (dict): Ticker e hora para a primeira tendência de baixa.
               - upward_trends (dict): Ticker e hora para a primeira tendência de alta."""
    downward_trends = {}
    upward_trends = {}

    for ticker in selected_tickers:
        try:
            data = yf.download(ticker, start=start_date, end=end_date, interval="1m")

            if data.empty:
                st.warning(f"No data found for {ticker} in the given time frame.")
                continue

            # Find the first downward trend
            first_downward_trend_time = None
            for i in range(1, len(data)):
                if data['Close'].iloc[i] < data['Close'].iloc[i - 1]:
                    first_downward_trend_time = data.index[i]
                    first_downward_trend_time_formatted = data.index[i].strftime('%Y-%m-%d %H:%M')
                    downward_trends[ticker] = first_downward_trend_time_formatted
                    break

            # Find the first upward trend
            first_upward_trend_time = None
            for i in range(1, len(data)):
                if data['Close'].iloc[i] > data['Close'].iloc[i - 1]:
                    first_upward_trend_time = data.index[i]
                    first_upward_trend_time_formatted = data.index[i].strftime('%Y-%m-%d %H:%M')
                    upward_trends[ticker] = first_upward_trend_time_formatted
                    break
        except Exception as e:
                st.error(f"Falha ao analisar tendências para {ticker}: {e}")
    return downward_trends, upward_trends
