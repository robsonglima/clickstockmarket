import streamlit as st
from app import *

from analitics import get_company_data
from analitics import get_all_tickers, df_total_b3
from datetime import date

from typing import List

st.sidebar.title("Menu")


page = st.sidebar.radio("Navegar para:", ["Principal", "Comparativo", "Correlação", "Gráfico", "Tabela"])

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
    st.title("Comparativo entre ações")
    data_frame_top_15_industry, _, _ = df_total_b3()
    
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

elif page == "Correlação":
    st.title("Correlação entre ações")
    st.markdown(
        """
        Nesta seção, é possível analisar a correlação entre diferentes ações, ajudando a identificar padrões de movimento conjunto que podem ser cruciais para estratégias de investimento
        """
    )

    all_tickers = get_all_tickers()
    if all_tickers:
        selected_tickers = st.multiselect(
            "Selecione os Tickers", all_tickers
        )

        start_date = st.date_input("Data Inicial", date(2023, 1, 1))
        end_date = st.date_input("Data Final", date.today())

        # Removed as get_correlation doesn't exist anymore
        # if st.button("Gerar Correlação"):
        #         if selected_tickers:
        #             correlation_matrix = get_correlation(selected_tickers, start_date, end_date)
        #             if correlation_matrix is not None:
        #               st.write("Matriz de Correlação:")
        #               st.dataframe(correlation_matrix)
        #             else:
        #               st.error("Erro ao gerar a matriz de correlação.")
        #         else:
        #             st.error("Selecione ao menos duas ações para gerar a correlação.")

        
elif page == "Gráfico":
    st.title("Análise do Gráfico")
    data_frame_top_15_industry, data_frame_precos_intradiarios, tickers_top_15 = df_total_b3()
    stats = run_app(data_frame_top_15_industry, data_frame_precos_intradiarios,tickers_top_15)


elif page == "Tabela":

    st.title("Tabelas de Dados")

    interval_options = ["1min", "2min", "5min", "15min", "30min", "60min", "90min", "1h", "1d"]
    period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max",]
    interval = st.selectbox("Selecione o Intervalo", interval_options, index=8)
    period = st.selectbox("Selecione o Período", period_options, index=5)

    data_frame_top_15_industry, data_frame_precos_intradiarios, tickers_top_15 = df_total_b3()

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
