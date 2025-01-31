import streamlit as st
from app import load_data, run_app  # Changed import statement
from tremor_app import Example as TremorGraphs


# --- Sidebar navigation ---
st.sidebar.title("Menu")
page = st.sidebar.radio(
    "Go to", ["Home", "Tabela", "App"]
)  # Updated menu options and page names

# --- Page Content ---
if page == "Home":
    st.title("Stock Analysis")  # Changed title
    st.write(
        """
            Bem-vindo ao Stock Analysis!

            Descubra as correlações entre ações e identifique padrões que podem indicar boas oportunidades de investimento. Nossa plataforma permite analisar o comportamento do mercado em diferentes períodos de tempo, ajudando você a entender como os ativos se movem juntos e quais sinais podem antecipar tendências.

            Use o menu para explorar os dados e aprimorar suas estratégias

        """
    )
    if st.button("Home"):
        st.write("Home!")

elif page == "Table":

    data_frame_top_15_industry, data_frame_precos_intradiarios = load_data()
    # Call to display the table
    TremorGraphs(data_frame_top_15_industry, data_frame_precos_intradiarios)


elif page == "App":
    # Call to run the content of app.py
    run_app()


