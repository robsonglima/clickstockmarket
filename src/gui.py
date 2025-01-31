import streamlit as st
from app import load_data, run_app, display_top_15_table, display_intraday_prices_table
from analitics import consultar_precos_intradiarios_yf
 
data_frame_top_15_industry, data_frame_precos_intradiarios = load_data()
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to", ["Home", "App", "Table"]
)  # Updated menu options and page names

# --- Page Content ---
if page == "Home":    
    st.title("Stock Market Analysis")  # Changed title
    st.markdown(
        """
            Bem-vindo ao Stock Analysis!

            Descubra as correlações entre ações e identifique padrões que podem indicar boas oportunidades de investimento. Nossa plataforma permite analisar o comportamento do mercado em diferentes períodos de tempo, ajudando você a entender como os ativos se movem juntos e quais sinais podem antecipar tendências.

            Use o menu para explorar os dados e aprimorar suas estratégias

        """
    )
    if st.button("Reload Home"):
        st.rerun()

elif page == "App":
    st.title("App")
    run_app(data_frame_top_15_industry, data_frame_precos_intradiarios)

elif page == "Table":
    st.title("Data Tables")
    # Button to update data from yfinance
    if st.button("Update Data"):
        try:
            with st.spinner("Updating data..."):
                # Get intraday prices
                interval_options = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
                period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
                interval = st.selectbox("Select Interval", interval_options, index=7)  # Default to "1h"
                period = st.selectbox("Select Period", period_options, index=5)  # Default to "1y"
                tickers_top_15 = data_frame_top_15_industry['TckrSymb'].tolist()
                updated_df_precos_intradiarios = consultar_precos_intradiarios_yf(tickers_top_15, interval, period)
                data_frame_precos_intradiarios = updated_df_precos_intradiarios
        except Exception as e:
             st.error(f"An error occurred while updating the data: {e}")
            st.success("Data updated successfully!")
    
    # Filter the data based on the selected period and interval
    # Display tables
    if data_frame_top_15_industry is not None:
        st.subheader("Top 15 Companies")
        display_top_15_table(data_frame_top_15_industry)

    if data_frame_precos_intradiarios is not None:
        st.subheader("Intraday Prices")
        display_intraday_prices_table(data_frame_precos_intradiarios)
    # User input for interval and period
    interval_options = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
    period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    interval = st.selectbox("Select Interval", interval_options, index=7)  # Default to "1h"
    period = st.selectbox("Select Period", period_options, index=5)  # Default to "1y"
    
    
   



