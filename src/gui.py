import streamlit as st
from app import load_data, run_app, display_top_15_table, display_intraday_prices_table, update_data_frames, show_company_info

from analitics import get_company_data
import pandas as pd
from datetime import date
 
st.sidebar.title("Menu")
page = st.sidebar.radio(
    "Ir para", ["Principal", "Dashboard", "Gráfico", "Tabela"]
)

if page == "Principal":
    st.title("Análise de Ações")
    st.markdown(
        """
            Bem-vindo ao Análise de Ações!

            Descubra as correlações entre ações e identifique padrões que podem indicar boas oportunidades de investimento. Nossa plataforma permite que você analise o comportamento do mercado em diferentes períodos de tempo, ajudando você a entender como os ativos se movem juntos e quais sinais podem antecipar tendências.

            Use o menu para explorar os dados e melhorar suas estratégias.

        """
        )
    if st.button("Recarregar Principal"):
        st.rerun()    

elif page == "Dashboard":
    st.title("Dashboard")
    tickers_list = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "NVDA", "BRK-B", "JPM", "JNJ", "V", "WMT", "MA", "PG", "UNH", "HD"]
    selected_tickers = st.multiselect("Selecione os Tickers", tickers_list, key="dashboard_tickers")

    start_date = st.date_input("Start date", date(2023, 1, 1))
    end_date = st.date_input("End date", date.today())

    company_data_list = []
    if selected_tickers:
        for ticker in selected_tickers:
            company_data = get_company_data(ticker, start_date, end_date)
            company_data_list.append(company_data)

        for ticker, company_data in zip(selected_tickers, company_data_list):
            show_company_info(company_data, ticker)

elif page == "Gráfico":
    st.title("Análise do Gráfico")
    data_frame_top_15_industry, data_frame_precos_intradiarios, tickers_top_15 = load_data()
    run_app(data_frame_top_15_industry, data_frame_precos_intradiarios,tickers_top_15)

elif page == "Tabela":

    st.title("Tabelas de Dados")

    interval_options = ["1min", "2min", "5min", "15min", "30min", "60min", "90min", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
    period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    interval = st.selectbox("Selecione Intervalo", interval_options, index=8)
    period = st.selectbox("Selecione Periodo", period_options, index=5)

    data_frame_top_15_industry, data_frame_precos_intradiarios, tickers_top_15 = load_data()

    if isinstance(data_frame_top_15_industry, pd.DataFrame):
        if st.button("Atualizar"):
            tickers_top_15 = data_frame_top_15_industry['TckrSymb'].tolist()
            try:
                with st.spinner("Atualizando..."):
                    data_frame_precos_intradiarios= update_data_frames(tickers_top_15, interval, period)
                    st.success("Atualizado com sucesso!")

                data_frame_precos_intradiarios = pd.read_csv("src/precos_intradiarios_top_15.csv")
                tickers_top_15 = data_frame_precos_intradiarios['symbol'].unique().tolist()

            except Exception as e:
                st.error(f"Ops, houve um erro ao atualizar: {e}")

    if isinstance(data_frame_top_15_industry, pd.DataFrame):
        st.subheader("Top 15 Empresas Listadas")
        display_top_15_table(data_frame_top_15_industry)

    if isinstance(data_frame_precos_intradiarios, pd.DataFrame):
        st.subheader("Preços no período selecionado")
        display_intraday_prices_table(data_frame_precos_intradiarios)
