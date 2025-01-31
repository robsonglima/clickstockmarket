
import logging
import os
import io
import requests
import pandas as pd
import yfinance as yf
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
    Analyses the initiation of upward and downward trends for given tickers.

    Args:
        tickers (list): List of stock tickers.
        start_date (date): Start date for the analysis.
        end_date (date): End date for the analysis.

    Returns:
        tuple: A tuple containing two dictionaries, one for downward trends and one for upward trends.
    """
    downward_trends = {}
    upward_trends = {}
    
    for ticker in tickers:
        company = yf.Ticker(ticker)
        history = company.history(start=start_date, end=end_date)
        
        if len(history) >= 2:
            
            if history['Close'].iloc[0] > history['Close'].iloc[1]:
                
                downward_trends[ticker] = history.index[1].strftime('%Y-%m-%d')
            
            elif history['Close'].iloc[0] < history['Close'].iloc[1]:
                
                upward_trends[ticker] = history.index[1].strftime('%Y-%m-%d')
            else:
                continue
    
    return downward_trends, upward_trends

if __name__ == "__main__":
    # Main execution block
    df = download_and_load_csv(GITHUB_CSV_URL, ';', CSV_ENCODING, 1, 'skip')

    if df is not None:
        #Incluindo .SA no TRacker para consultar no Yahoo Finance
        df['TckrSymb'] = df['TckrSymb'] + '.SA'
        df_filtrado_segmento = df[df['SgmtNm'].str.contains('CASH', na=False)]
        df_top_15 = df_filtrado_segmento.nlargest(TOP_N, 'TradQty')

        # adicionando mercado na tabela -  industry 
        df_top_15_atualizado = preencher_industry(df_top_15)
        print(df_top_15_atualizado)
        #Save industry data
        try:
            df_top_15_atualizado.to_csv(OUTPUT_FILE_INDUSTRY, index=False, sep=";")
            logging.info(f"{OUTPUT_FILE_INDUSTRY} saved successfully.")
        except Exception as e:
            logging.error(f"Error saving {OUTPUT_FILE_INDUSTRY}: {e}")

        # atualziando intraday - precos
        tickers_top_15 = df_top_15_atualizado['TckrSymb'].tolist()        
        df_precos_intradiarios = consultar_precos_intradiarios_yf(tickers_top_15)
        
        #adicionando info de mercado (industry) no df_precos_intradiarios
        industry_mapping = df_top_15_atualizado.set_index('TckrSymb')['Industry'].to_dict()
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

