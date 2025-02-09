
import pandas as pd
import yfinance as yf
import io
import requests
import logging
import time
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


def download_and_load_csv(url, delimiter, encoding, header, bad_lines_action, cache_file="temp_cached.csv"):
    """Downloads a CSV from a URL, caches it locally, and loads it into a Pandas DataFrame.
    
    Args:
        url (str): The URL of the CSV file.
        delimiter (str): The delimiter used in the CSV.
        encoding (str): The encoding of the CSV file.
        header (int): The row number to use as the header.
        bad_lines_action (str): The action to take on bad lines ('skip', 'error', etc.).
        cache_file (str): The local file path to cache the downloaded CSV.
    """
    if os.path.exists(cache_file):
        logging.info(f"Loading CSV from cache: {cache_file}")
        try:
            return pd.read_csv(cache_file, delimiter=delimiter, encoding=encoding, header=header, on_bad_lines=bad_lines_action)
        except pd.errors.ParserError as e:
            logging.error(f"Error parsing cached CSV: {e}. Attempting to download fresh copy.")

        response = requests.get(url, stream=True)
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
        logging.info(f"CSV downloaded and cached to {cache_file}")
        logging.error(f"Error downloading or parsing CSV: {e}")
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
                logging.info(f"Pausing for 120 seconds due to potential rate limit for {ticker}...")
                time.sleep(120)

                try:
                    logging.info(f"Retrying to fetch data for {ticker} after pause")
                    dados = yf.download(ticker, interval=intervalo, period=periodo, progress=False)
                    dados = dados.reset_index()
                    dados.columns = ["datetime", "open", "high", "low", "close", "volume"]
                    dados["symbol"] = ticker

                    dados = dados[["datetime", "symbol", "volume", "open", "high", "low", "close"]]
                    precos.append(dados)

                    logging.info(f"Data fetched for {ticker} on retry")
                except Exception as e:
                    logging.error(f"Error on retry fetch data for {ticker} after 120-second pause: {e}")
                    logging.warning(f"Failed to fetch data for {ticker} after retry. Stopping processing other tickers.")
                    return pd.DataFrame(), f"Failed to fetch data for {ticker} after retry."
            
        except Exception as e:
                logging.error(f"Error fetching data for {ticker}: {e}")
    return pd.concat(precos, ignore_index=True) if precos else pd.DataFrame(), ""

def get_company_data(ticker: str, start_date: date, end_date: date):
    """
    Gets company data from Yahoo Finance.
    Args:
        ticker: str
        start_date: date 
        end_date: date 
    
        
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return {"profile": "N/A", "market": "N/A", "volume": "N/A", "history": pd.DataFrame()}
    """    

if __name__ == "__main__":
    # Main execution block
    df = download_and_load_csv(GITHUB_CSV_URL, ';', CSV_ENCODING, 1, 'skip', cache_file='temp_cached_b3.csv')

    if df is not None:
        #Incluindo .SA no TRacker para consultar no Yahoo Finance
        df['TckrSymb'] = df['TckrSymb'] + '.SA'

        # adicionando mercado na tabela -  industry 
        df_atualizado = preencher_industry(df)
        print(df_atualizado)
        #Save industry data
        try:
            df_atualizado.to_csv(OUTPUT_FILE_INDUSTRY, index=False, sep=";")
            logging.info(f"{OUTPUT_FILE_INDUSTRY} saved successfully.")
        except Exception as e:
            logging.error(f"Error saving {OUTPUT_FILE_INDUSTRY}: {e}")

        # atualziando intraday - precos
        tickers = df_atualizado['TckrSymb'].tolist()        
        df_precos_intradiarios, warning_message = consultar_precos_intradiarios_yf(tickers,"1d", "10d")

        if warning_message:
            logging.warning(warning_message)
            # Decide whether to proceed or halt based on the warning
            # For now, let's continue processing even with the warning       
        
        #adicionando info de mercado (industry) no df_precos_intradiarios
        industry_mapping = df_atualizado.set_index('TckrSymb')['Industry'].to_dict()
        df_precos_intradiarios['Industry'] = df_precos_intradiarios['symbol'].map(industry_mapping)   
        
        #Adicionanod industry no df_precos
        df_precos = df_precos_intradiarios


        print("df_precos_intradiarios")
        print(df_precos_intradiarios.head())        

        #Salvar o intraday data - mensage somente no log
        try:
            df_precos_intradiarios.to_csv(OUTPUT_FILE_INTRADAY, index=False)
            logging.info(f"{OUTPUT_FILE_INTRADAY} saved successfully.")
        except Exception as e:
            logging.error(f"Error saving {OUTPUT_FILE_INTRADAY}: {e}")
