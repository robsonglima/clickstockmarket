
import pandas as pd
import yfinance as yf
import io
import requests
import logging
import os

# Configure logging
from datetime import date

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
GITHUB_CSV_URL = "https://github.com/robsonglima/StockMarket_B3/blob/5c7977ff8b2f087ce8232a937cc39855d4adbed9/TradeInformationConsolidatedFile_20250127_1.csv?raw=true"
TOP_N = 15
CSV_ENCODING = 'latin1'
OUTPUT_DIR = "src"

# Create the output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):

    os.makedirs(OUTPUT_DIR)
OUTPUT_FILE_INDUSTRY = os.path.join(OUTPUT_DIR, "df_top_15_com_industry.csv")
OUTPUT_FILE_INTRADAY = os.path.join(OUTPUT_DIR, "precos_intradiarios_top_15.csv")


def download_and_load_csv(url, delimiter, encoding, header, bad_lines_action):
    """Downloads a CSV from a URL and loads it into a Pandas DataFrame."""
    try:
        logging.info(f"Downloading CSV de {url}")
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        logging.info("CSV downloaded successfully. Loading into DataFrame.")
        df = pd.read_csv(io.StringIO(response.text), delimiter=delimiter, encoding=encoding, header=header, on_bad_lines=bad_lines_action)
        return df
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading CSV: {e}")
        return None
    except pd.errors.ParserError as e:
        logging.error(f"Error parsing CSV: {e}")
        return None

def preencher_industry(df):
    """Fetches and adds 'Industry' information to the DataFrame."""
    industries = []
    for ticker in df['TckrSymb']:
        try:
            logging.info(f"Fetching industry for {ticker}")
            info = yf.Ticker(ticker).info
            industry = info.get("industry", "N/A")
            industries.append(industry)
            logging.info(f"Industry for {ticker}: {industry}")
        except Exception as e:
            logging.error(f"Error fetching industry for {ticker}: {e}")
            industries.append("Erro")

    



    df['Industry'] = industries
    return df

def consultar_precos_intradiarios_yf(tickers, intervalo, periodo):
    """Fetches intraday price data for a list of tickers."""
    precos = []
    for ticker in tickers:
        try:
            logging.info(f"Fetching intraday data for {ticker}")
            dados = yf.download(ticker, interval=intervalo, period=periodo, progress=False)
            dados = dados.reset_index()
            dados.columns = ["datetime", "open", "high", "low", "close", "volume"]
            dados["symbol"] = ticker

            dados = dados[["datetime", "symbol", "volume", "open", "high", "low", "close"]]
            precos.append(dados)
            


            logging.info(f"Data fetched for {ticker}")
        except Exception as e:
            logging.error(f"Error fetching data for {ticker}: {e}")
    return pd.concat(precos, ignore_index=True) if precos else pd.DataFrame()



def get_company_data(ticker, start_date, end_date):
    """
    Fetches company information and historical prices for a given ticker.
    
    Args:
        ticker (str): The stock ticker symbol.
        start_date (date): The start date for historical prices.
        end_date (date): The end date for historical prices.
    
    Returns:
        dict: A dictionary containing the company's profile, market, volume, and historical prices.
    """
    try:
        company = yf.Ticker(ticker)
        info = company.info
        history = company.history(start=start_date, end=end_date)
        return {"profile": info.get("longBusinessSummary", "N/A"), "market": info.get("market", "N/A"), "volume": history.iloc[-1]['Volume'] if not history.empty else "N/A", "history": history}
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return {"profile": "N/A", "market": "N/A", "volume": "N/A", "history": pd.DataFrame()}


def analyze_trend_initiation(tickers, start_date, end_date):
    """
    Analyzes the initiation of upward and downward trends for a list of stock tickers.

    Args:
        tickers (list): List of stock tickers.
        start_date (date): Start date for the analysis.
        end_date (date): End date for the analysis.

    Returns:
        tuple: Two dictionaries, one for downward trends and one for upward trends.
               Each dictionary contains ticker symbols as keys and the trend initiation
               time as values.
    """
    downward_trends = {}
    upward_trends = {}
    for ticker in tickers:
        try:
            ticker_data = yf.download(ticker, start=start_date, end=end_date)
            if not ticker_data.empty:
                # Implement logic to detect trend initiation
                # Example: check for a series of consecutive decreases or increases
                data = ticker_data['Close']
                for i in range(1, min(len(data), 4)): # Iterate only the first 3 lines
                    if data[i] < data[i - 1]:
                        # Check for a series of decreases to consider it a trend
                        consecutive_decreases = all(data[j] < data[j-1] for j in range(i, max(0, i-3),-1))

                        if consecutive_decreases and ticker not in downward_trends:
                            downward_trends[ticker] = data.index[i].strftime('%Y-%m-%d')
                            break # Stop when one trend is found
                    elif data[i] > data[i - 1]:
                        # Check for a series of increases to consider it a trend
                        consecutive_increases = all(data[j] > data[j-1] for j in range(i, max(0, i-3),-1))
                        if consecutive_increases and ticker not in upward_trends:
                            upward_trends[ticker] = data.index[i].strftime('%Y-%m-%d')
                            break # Stop when one trend is found
        except Exception as e:
            logging.error(f"Error analyzing trends for {ticker}: {e}")
    return downward_trends, upward_trends


def load_data(interval = "1d", period="1y"):
    """
    Load the data
    """
    logging.info(f"Loading data with interval {interval} and period {period}")

    try:
        data_frame_top_15_industry = pd.read_csv("src/df_top_15_com_industry.csv", sep=";")
        data_frame_precos_intradiarios = pd.read_csv("src/precos_intradiarios_top_15.csv")
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        df = download_and_load_csv(GITHUB_CSV_URL, ';', CSV_ENCODING, 1, 'skip')

        if df is not None:
            df['TckrSymb'] = df['TckrSymb'] + '.SA'
            df_filtrado_segmento = df[df['SgmtNm'].str.contains('CASH', na=False)]
            data_frame_top_15_industry = df_filtrado_segmento.nlargest(TOP_N, 'TradQty')
            data_frame_top_15_industry = preencher_industry(data_frame_top_15_industry)
            data_frame_top_15_industry.to_csv(OUTPUT_FILE_INDUSTRY, index=False, sep=";")
    tickers_top_15 = data_frame_top_15_industry['TckrSymb'].tolist()        
    data_frame_precos_intradiarios = consultar_precos_intradiarios_yf(tickers_top_15,interval, period)
    
    industry_mapping = data_frame_top_15_industry.set_index('TckrSymb')['Industry'].to_dict()
    data_frame_precos_intradiarios['Industry'] = data_frame_precos_intradiarios['symbol'].map(industry_mapping)
    data_frame_precos_intradiarios.to_csv(OUTPUT_FILE_INTRADAY, index=False)
    logging.info("Data load with sucefull.")
    tickers_top_15 = data_frame_top_15_industry['TckrSymb'].tolist()

    return data_frame_top_15_industry, data_frame_precos_intradiarios, tickers_top_15
        

    window_size = 3
    for ticker in tickers:
        ticker_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if not ticker_data.empty:
            data = ticker_data['Close']
            for i in range(window_size, len(data)):
                if all(data[j] > data[j+1] for j in range(i - window_size + 1, i)):
                    if ticker not in downward_trends:   
                        downward_trends[ticker] = data.index[i].strftime('%Y-%m-%d')
                        break
                elif all(data[j] < data[j+1] for j in range(i - window_size + 1, i)):
                    if ticker not in upward_trends:
                        upward_trends[ticker] = data.index[i].strftime('%Y-%m-%d')
                        break
    

    
