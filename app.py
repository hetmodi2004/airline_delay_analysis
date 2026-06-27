import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
import io

st.set_page_config(page_title="Airline Delay Dashboard", page_icon="✈️", layout="wide")

@st.cache_data
def load_data():
    file_id = "1IW3_dV5TDVFWZfSenpJob0015Va38iJ3"
    
    session = requests.Session()
    
    # First request to get confirmation token
    URL = "https://docs.google.com/uc?export=download"
    response = session.get(URL, params={'id': file_id}, stream=True)
    
    # Get confirmation token
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break
    
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)
    
    # Read content
    content = response.content
    df = pd.read_csv(io.BytesIO(content))
    df = df.dropna(subset=['arr_flights'])
    df['delay_rate'] = df['arr_del15'] / df['arr_flights'] * 100
    return df

df = load_data()

st.title("✈️ Airline Delay Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Total Flights", f"{df['arr_flights'].sum():,.0f}")
col2.metric("Total Delayed", f"{df['arr_del15'].sum():,.0f}")
col3.metric("Avg Delay Rate", f"{df['delay_rate'].mean():.1f}%")

yearly = df.groupby('year')['delay_rate'].mean().reset_index()
fig = px.line(yearly, x='year', y='delay_rate', title='Average Delay Rate by Year')
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df.head(10))
