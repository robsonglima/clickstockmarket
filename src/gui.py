import streamlit as st
from app import load_data, display_intraday_prices_table, display_top_15_table, run_app
import pandas as pd
from analitics import consultar_precos_intradiarios_yf, preencher_industry, analyze_trend_initiation, get_company_data, show_graph_selected_tickers

st.sidebar.title("Menu")

# Use radio button in the sidebar for page selection
page = st.sidebar.radio("Ir para", ["Principal", "Gráfico", "Tabela", "Comparativo"])

if page == "Principal":
    st.title("Análise de Ações") 
    st.markdown("""
            Bem-vindo ao Análise de Ações!

            Descubra as correlações entre ações e identifique padrões que podem indicar boas oportunidades de investimento. Nossa plataforma permite que você analise o comportamento do mercado em diferentes períodos de tempo, ajudando você a entender como os ativos se movem juntos e quais sinais podem antecipar tendências.          
            """)
    
elif page == "Comparativo":
    st.title("Comparativo")
    data_frame_top_15_industry, data_frame_precos_intradiarios = load_data()    

    if isinstance(data_frame_top_15_industry, pd.DataFrame):
        tickers_list = data_frame_top_15_industry['TckrSymb'].tolist()
        selected_tickers = st.multiselect("Selecione os Tickers", tickers_list, key="dashboard_tickers")
    else:
        selected_tickers = []

    from datetime import date
    start_date = st.date_input("Data Inicial", date(2023, 1, 1))
    end_date = st.date_input("Data Final", date.today())

    company_data_list = []
    if selected_tickers :
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

    if selected_tickers:
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
        

elif page == "Gráfico":
    st.title("Gráfico")

elif page == "Tabela":
    st.title("Tabelas de Dados")

    interval_options = ["1min", "2min", "5min", "15min", "30min", "60min", "90min", "1h", "1d"]
    period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max",]

    interval = st.selectbox("Selecione o Intervalo", interval_options, index=8)    
    period = st.selectbox("Selecione o Período", period_options, index=5)

    data_frame_top_15_industry, data_frame_precos_intradiarios = load_data(interval, period)
   
    if isinstance(data_frame_top_15_industry, pd.DataFrame):
        st.subheader("Top 15 Empresas Listadas")
        display_top_15_table(data_frame_top_15_industry)

    if isinstance(data_frame_precos_intradiarios, pd.DataFrame):
        st.subheader("Preços no período selecionado")
        display_intraday_prices_table(data_frame_precos_intradiarios)

