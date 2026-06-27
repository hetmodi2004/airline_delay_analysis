import streamlit as st
import pandas as pd

st.title("✈️ Airline Delay Dashboard")

url = "https://raw.githubusercontent.com/hetmodi2004/airline_delay_analysis/main/airline_small.csv"
df = pd.read_csv(url)

st.write("✅ Data loaded successfully!")
st.write(f"Rows: {len(df):,}")
st.write(f"Years: {df['year'].min()} – {df['year'].max()}")
st.dataframe(df.head(10))
