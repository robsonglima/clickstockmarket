import streamlit as st
from app import *

from analitics import analyze_trend_initiation, get_company_data
import pandas as pd
from datetime import date

st.sidebar.title("Menu")

from app import display_intraday_prices_table, display_top_15_table, load_data
from app import show_company_info, show_comparative_graph, update_data_frames
from analitics import analyze_trend_initiation, get_company_data

def load_data_no_tickers():
    """Load the data without tickers."""
    data_frame_top_15_industry, data_frame_precos_intradiarios, _ = load_data(interval='1d', period='1y')
    return data_frame_top_15_industry, data_frame_precos_intradiarios
    
page = st.sidebar.radio("Navegar para:", ["Principal", "Comparativo", "Gráfico", "Tabela"])


end_date = date.today()

    
if page == "Principal":

    st.title("Análise de Ações")
    st.markdown(
        """
            Bem-vindo ao Análise de Ações!

            Descubra as correlações entre ações e identifique padrões que podem indicar boas oportunidades de investimento. Nossa plataforma permite que você analise o comportamento do mercado em diferentes períodos de tempo, ajudando você a entender como os ativos se movem juntos e quais sinais podem antecipar tendências.

            Use a barra lateral para explorar os dados e melhorar suas estratégias.

        """
    )    
elif page == "Comparativo":
    st.title("Comparativo")
    data_frame_top_15_industry, data_frame_precos_intradiarios = load_data_no_tickers()

    if isinstance(data_frame_top_15_industry, pd.DataFrame):
        tickers_list = data_frame_top_15_industry['TckrSymb'].tolist()

        
        selected_tickers = st.multiselect("Selecione os Tickers", tickers_list, key="dashboard_tickers")
    else:
        selected_tickers = []

    start_date = st.date_input("Data Inicial", date(2023, 1, 1))

    company_data_list = []

    if selected_tickers:
        
        show_comparative_graph(selected_tickers, start_date, end_date)       

        for ticker in selected_tickers:
            company_data = get_company_data(ticker, start_date, end_date)
            company_data_list.append(company_data)
            
        for ticker, company_data in zip(selected_tickers, company_data_list):
            show_company_info(company_data, ticker)
        downward_trends, upward_trends = analyze_trend_initiation(selected_tickers, start_date, end_date)

        if downward_trends:
            for ticker, trend_time in downward_trends.items():
                st.write(f"**Primeira Tendência de Baixa Iniciada:** {ticker} em {trend_time}")
        else:
            st.write(f"**Primeira Tendência de Baixa Iniciada:** Sem tendências detectadas.")

        if upward_trends:
            for ticker, trend_time in upward_trends.items():
                st.write(f"**Primeira Tendência de Alta Iniciada:** {ticker} em {trend_time}")
        else:
            st.write(f"**Primeira Tendência de Alta Iniciada:** Sem tendências detectadas.")
        

elif page == "Gráfico":
    st.title("Gráfico")

elif page == "Tabela":

    st.title("Tabelas de Dados")

    interval_options = ["1min", "2min", "5min", "15min", "30min", "60min", "90min", "1h", "1d"]
    period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max",]
    interval = st.selectbox("Selecione o Intervalo", interval_options, index=8)
    period = st.selectbox("Selecione o Período", period_options, index=5)

    data_frame_top_15_industry, data_frame_precos_intradiarios, tickers_top_15 = load_data()

    if isinstance(data_frame_top_15_industry, pd.DataFrame):
        if st.button("Atualizar"):
            tickers_top_15 = data_frame_top_15_industry['TckrSymb'].tolist()
            try:
                with st.spinner("Atualizando..."):
                    data_frame_precos_intradiarios = update_data_frames(tickers_top_15, interval, period)
                    st.success("Atualizado com sucesso!")

                data_frame_precos_intradiarios = pd.read_csv("src/precos_intradiarios_top_15.csv")
                tickers_top_15 = data_frame_precos_intradiarios["symbol"].unique().tolist()

            except Exception as e:
                st.error(f"Ops, houve um erro ao atualizar: {e}")
    
    if isinstance(data_frame_top_15_industry, pd.DataFrame):
        st.subheader("Top 15 Empresas Listadas")
        display_top_15_table(data_frame_top_15_industry)

    if isinstance(data_frame_precos_intradiarios, pd.DataFrame):
        st.subheader("Preços no período selecionado")
        display_intraday_prices_table(data_frame_precos_intradiarios)
