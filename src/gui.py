import streamlit as st
from app import *

from analitics import get_company_data
import pandas as pd
from datetime import date

from typing import List

st.sidebar.title("Menu")

def display_cards(stats):
    """
    Exibe três cards com estatísticas.

    Args:
        stats (list): Uma lista de dicionários, onde cada dicionário contém o
                      'name', 'stat', 'change' e 'changeType' para um card.
    """
    card_data = [
        {
            'name': 'Média de Variação Diária',
            'stat': stats[0],
            'change': stats[1],
            'changeType': stats[2]
        },
        {
            'name': 'Volume Médio Diário',
            'stat': stats[3],
            'change': stats[4],
            'changeType': stats[5],
        },
        {
            'name': 'Desvio Padrão',
            'stat': stats[6],
            'change': stats[7],
            'changeType': stats[8]
        }
    ]
    
    card_html = '<dl class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">'
    for item in card_data:
      card_html += f'''
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <div class="flex items-center justify-between">
          <dt class="truncate text-sm font-medium text-gray-500">{item['name']}</dt>
          <dd class="ml-2 flex items-baseline">
          <span class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset {'bg-emerald-100 text-emerald-800 ring-emerald-600/10 dark:bg-emerald-400/10 dark:text-emerald-500 dark:ring-emerald-400/20' if item['changeType'] == 'positive' else 'bg-red-100 text-red-800 ring-red-600/10 dark:bg-red-400/10 dark:text-red-500 dark:ring-red-400/20'}">
            {item['change']}
          </span>
            </dd>
        </div>
        <div class="mt-1 flex flex-col sm:mt-0 sm:flex-row sm:flex-wrap sm:space-x-6">
          <dd class="text-3xl font-semibold text-gray-900">
          {item['stat']}
          </dd>
        </div>
      </div>
      '''
    card_html += '</dl>'
    st.markdown(card_html, unsafe_allow_html=True)
page = st.sidebar.radio("Navegar para:", ["Principal", "Comparativo", "Gráfico", "Tabela"])

if page == "Principal":
    st.title("Análise de Ações") 
    st.markdown("""
            Bem-vindo ao Análise de Ações!

            Descubra as correlações entre ações e identifique padrões que podem indicar boas oportunidades de investimento. Nossa plataforma permite que você analise o comportamento do mercado em diferentes períodos de tempo, ajudando você a entender como os ativos se movem juntos e quais sinais podem antecipar tendências.          
            """)
    
elif page == "Comparativo":
    st.title("Comparativo")
    data_frame_top_15_industry, _, _ = load_data()
    
    if isinstance(data_frame_top_15_industry, pd.DataFrame):
        tickers_list = data_frame_top_15_industry['CD_TICKER'].tolist()
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

        if downward_trend:
              for ticker, trend_time in downward_trends.items():
                st.write(f"**Primeira Tendência de Baixa Iniciada:** {ticker} em {trend_time}")
        else:
            st.write(f"**Primeira Tendência de Baixa Iniciada:** Sem tendências detectadas.")

        if upward_trend:
              for ticker, trend_time in upward_trend.items():
                st.write(f"**Primeira Tendência de Alta Iniciada:** {ticker} em {trend_time}")
        else:
              st.write(f"**Primeira Tendência de Alta Iniciada:** Sem tendências detectadas.")

        
elif page == "Gráfico":
    st.title("Análise do Gráfico")
    data_frame_top_15_industry, data_frame_precos_intradiarios, tickers_top_15 = load_data()
    stats = run_app(data_frame_top_15_industry, data_frame_precos_intradiarios,tickers_top_15)
    display_cards(stats)    


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
