import streamlit as st
import pandas as pd

st.title("✈️ Airline Delay Dashboard")

df = pd.read_csv('Airline_Delay_Cause.csv')
df = df.dropna(subset=['arr_flights'])

st.write("Data loaded successfully!")
st.write(f"Total rows: {len(df):,}")
st.write(f"Years: {df['year'].min()} – {df['year'].max()}")
st.write(f"Airlines: {df['carrier_name'].nunique()}")
st.write(f"Airports: {df['airport'].nunique()}")

st.dataframe(df.head(10))
