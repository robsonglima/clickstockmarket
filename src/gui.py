import streamlit as st
from app import *

from analitics import get_company_data
import pandas as pd
from datetime import date

from typing import List

st.sidebar.title("Menu")

def format_number(number):
    """
    Formats a number to two decimal places if it's a float, otherwise returns the number as is.
    """
    if isinstance(number, float):
        return "{:.2f}".format(number)
    return number


def display_cards(stats):
    """Displays three cards with statistics using a modern design.

    Args:
        stats (list): A list containing the statistical data.
    """
    if stats is None:
        print('Stats are none')
        return
    card_data = [
        {
            'name': 'Média de Variação Diária',
            'description': 'Variação média das ações em um dia',
            'stat': format_number(stats[0]),
            'change': stats[1],
            'changeType': stats[2]
        },
        {
            'name': 'Volume Médio Diário',
            'description': 'Volume médio de negociações por dia',
            'stat': format_number(stats[3]),
            'change': stats[4],
            'changeType': stats[5],
        },
        {
            'name': 'Desvio Padrão',
            'description': 'Volatilidade das variações diárias',
            'stat': format_number(stats[6]),
            'change': stats[7],
            'changeType': stats[8]
        }
    ]

    card_html = '<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">'
    for item in card_data:
        change_type_class = {
            'positive': 'bg-green-200 text-green-800',
            'negative': 'bg-red-200 text-red-800',
            'neutral': 'bg-gray-200 text-gray-800'
        }.get(item['changeType'], 'bg-gray-200 text-gray-800')
        
        card_html += f"""
            <div class="bg-white rounded-lg shadow-md p-6 flex flex-col justify-between">
                <h3 class="text-lg font-bold text-gray-800 mb-1">{item['name']}</h3>
                <p class="text-gray-600 text-sm mb-4">{item['description']}</p>
                <div class="text-4xl font-extrabold text-blue-600 mb-4">{item['stat']}</div>
                <div class="flex items-center">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium {change_type_class}">{item['change']}</span>
                </div>
            </div>
        """
    card_html += '</div>'
    st.markdown(card_html, unsafe_allow_html=True)
    
page = st.sidebar.radio("Navegar para:", ["Principal", "Comparativo", "Gráfico", "Tabela"])

if page == "Principal":

    st.title("Análise de Ações")
    st.markdown(
        """
            Bem-vindo ao Análise de Ações!

            Descubra as correlações entre ações e identifique padrões que podem indicar boas oportunidades de investimento. Nossa plataforma permite que você analise o comportamento do mercado em diferentes períodos de tempo, ajudando você a entender como os ativos se movem juntos e quais sinais podem antecipar tendências.

            Use a barra lateral para explorar os dados e melhorar suas estratégias.

        """
        )
    if st.button("Recarregar Principal"):
        
        st.rerun()    
elif page == "Comparativo":
    st.title("Comparativo")
    data_frame_top_15_industry, _, _ = load_data()
    
    if isinstance(data_frame_top_15_industry, pd.DataFrame):
        tickers_list = data_frame_top_15_industry['TckrSymb'].tolist()
        selected_tickers = st.multiselect("Selecione os Tickers", tickers_list, key="dashboard_tickers")
    else:
        selected_tickers = []

    start_date = st.date_input("Data Inicial", date(2023, 1, 1))
    end_date = st.date_input("Data Final", date.today())

    company_data_list = []
    if selected_tickers:
        show_comparative_graph(selected_tickers, start_date, end_date)
        for ticker in selected_tickers:
            company_data = get_company_data(ticker, start_date, end_date)
            company_data_list.append(company_data)

        for ticker, company_data in zip(selected_tickers,company_data_list):
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
