import streamlit as st
import pandas as pd

st.title("✈️ Airline Delay Dashboard")

# Load data from Google Drive
file_id = "1IW3_dV5TDVFWZfSenpJob0015Va38iJ3"
url = f"https://drive.google.com/uc?export=download&id={file_id}"

df = pd.read_csv(url)
df = df.dropna(subset=['arr_flights'])

st.write("Data loaded successfully!")
st.write(f"Total rows: {len(df):,}")
st.write(f"Years: {df['year'].min()} – {df['year'].max()}")
st.write(f"Airlines: {df['carrier_name'].nunique()}")
st.write(f"Airports: {df['airport'].nunique()}")

st.dataframe(df.head(10))
