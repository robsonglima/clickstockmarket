# 'use client';

import pandas as pd
from datetime import datetime
import streamlit as st
from tremor_react import AreaChart, Card, Tab, TabGroup, TabList, TabPanel, TabPanels, Metric, Text, Bold, BarChart, Title, LineChart

def get_data_for_line_chart(df_precos_intradiarios):
    """
    Prepares data for the Tremor LineChart from the df_precos_intradiarios DataFrame.
    """
    df_copy = df_precos_intradiarios.copy()
    df_copy['datetime'] = pd.to_datetime(df_copy['date'] + ' ' + df_copy['time'])
    df_copy.drop(['date', 'time'], axis=1, inplace=True)

    # Aggregate by datetime (e.g., mean close price)
    df_agg = df_copy.groupby('datetime').agg({'close': 'mean', 'volume': 'sum'}).reset_index()
    df_agg.rename(columns={'close': 'Average Close Price', 'volume': 'Total Volume'}, inplace=True)

    data_for_line_chart = df_agg.to_dict('records')

    return data_for_line_chart

def get_data_for_bar_chart(df_top_15_industry):
    """
    Prepares data for the Tremor BarChart from the df_top_15_industry DataFrame.
    """
    df_copy = df_top_15_industry.copy()
    industry_counts = df_copy['Industry'].value_counts().reset_index()
    industry_counts.columns = ['Industry', 'Number of Companies']
    
    data_for_bar_chart = industry_counts.to_dict('records')
    
    return data_for_bar_chart


def value_formatter(number):
    return f"{number:,.0f}"

def Example(df_top_15_industry, df_precos_intradiarios):
    data_line_chart = get_data_for_line_chart(df_precos_intradiarios)
    data_bar_chart = get_data_for_bar_chart(df_top_15_industry)

    with st.container():
        st.write(
            f"""
                <div style="display:flex; justify-content: center; align-items: center; margin: auto; height: auto">
                    <h3 class="text-tremor-title font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
                        Industry Distribution
                    </h3>
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(
            f"""
                <div style="display:flex; justify-content: center; align-items: center; margin: auto; height: auto">
                   <p class="mt-1 text-tremor-default text-tremor-content dark:text-dark-tremor-content">
                     Distribution of companies across different industries
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.tremor_chart(BarChart(data=data_bar_chart, index="Industry", categories=["Number of Companies"], valueFormatter=value_formatter, yAxisWidth=45, className="h-96"))       
        st.write(
            f"""
                <div style="display:flex; justify-content: center; align-items: center; margin: auto; height: auto">
                   <p class="mt-1 text-tremor-default text-tremor-content dark:text-dark-tremor-content">
                     Time series of Average close Price and volume
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.tremor_chart(LineChart(data=data_line_chart, index="datetime", categories=["Average Close Price","Total Volume"], valueFormatter=value_formatter, yAxisWidth=45, className="h-96"))

