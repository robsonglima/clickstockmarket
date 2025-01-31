import streamlit as st
from app import load_data, run_app, display_top_15_table, display_intraday_prices_table
from analitics import consultar_precos_intradiarios_yf

st.sidebar.title("Menu")
page = st.sidebar.radio(
    "Ir para", ["Principal", "Gráfico", "Tabela"]
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

elif page == "Gráfico":    
    st.title("Análise do Gráfico")    
    data_frame_top_15_industry, data_frame_precos_intradiarios = load_data()
    tickers_top_15 = data_frame_top_15_industry['TckrSymb'].tolist()    
    run_app(data_frame_top_15_industry, data_frame_precos_intradiarios,tickers_top_15)

elif page == "Tabela":
    st.title("Tabelas de Dados")
    
    interval_options = ["1min", "2min", "5min", "15min", "30min", "60min", "90min", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
    period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    interval = st.selectbox("Selecione Intervalo", interval_options, index=8)
    period = st.selectbox("Selecione Periodo", period_options, index=5)
    
    data_frame_top_15_industry, data_frame_precos_intradiarios = load_data()
    tickers_top_15 = data_frame_top_15_industry['TckrSymb'].tolist()
    # Button to update data from yfinance
    if st.button("Atualizar"):
         try:
            
            with st.spinner("Atualizando..."):
                updated_df_precos_intradiarios = consultar_precos_intradiarios_yf(tickers_top_15, interval, period)
                data_frame_precos_intradiarios = updated_df_precos_intradiarios
                st.success("Atualizado com sucesso!")
         except Exception as e:
             st.error(f"Ops, houve um erro ao atualizar: {e}")
    # Display tables
    
    if data_frame_top_15_industry is not None:
        st.subheader("Top 15 Empresas Listadas")
        display_top_15_table(data_frame_top_15_industry)

    if data_frame_precos_intradiarios is not None:
        st.subheader("Preços no período selecionado")
        display_intraday_prices_table(data_frame_precos_intradiarios)
