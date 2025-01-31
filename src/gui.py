import streamlit as st
from app import load_data, run_app, display_top_15_table, display_intraday_prices_table
from analitics import consultar_precos_intradiarios_yf
 
data_frame_top_15_industry, data_frame_precos_intradiarios = load_data()
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to", ["Home", "App", "Tabela"]
)

if page == "Home":
    st.title("Stock Market Analysis")
    st.markdown(
        """
            Welcome to Stock Analysis!

            Discover the correlations between stocks and identify patterns that may indicate good investment opportunities. Our platform allows you to analyze market behavior over different time periods, helping you understand how assets move together and what signs can anticipate trends.

            Use the menu to explore the data and improve your strategies.

        """
    )
    if st.button("Reload Home"):
        st.rerun()

elif page == "App":    
    st.title("Ticker Analysis")
    data_frame_top_15_industry, data_frame_precos_intradiarios = load_data()    
    run_app(data_frame_top_15_industry, data_frame_precos_intradiarios)

elif page == "Tabela":    
    st.title("Tabelas de Dados")
    interval_options = ["1min", "2min", "5min", "15min", "30min", "60min", "90min", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
    period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    interval = st.selectbox("Select Interval", interval_options, index=8)
    period = st.selectbox("Select Period", period_options, index=5)

    # Button to update data from yfinance
    if st.button("Update Data"):
        try:
            with st.spinner("Updating..."):
                tickers_top_15 = data_frame_top_15_industry['TckrSymb'].tolist()
                updated_df_precos_intradiarios = consultar_precos_intradiarios_yf(tickers_top_15, interval, period)
                data_frame_precos_intradiarios = updated_df_precos_intradiarios
        except Exception as e:
            st.error(f"An error occurred while updating the data: {e}")

    st.success("Updated successfully!")
    # Display tables
    if data_frame_top_15_industry is not None:
        st.subheader("Top 15 Listed Companies")
        display_top_15_table(data_frame_top_15_industry)

    if data_frame_precos_intradiarios is not None:
        st.subheader("Prices in the selected timeframe")
        display_intraday_prices_table(data_frame_precos_intradiarios)




