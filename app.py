import streamlit as st
import pandas as pd
import gdown
import os

st.title("✈️ Airline Delay Dashboard")

# Download from Google Drive
file_id = "1IW3_dV5TDVFWZfSenpJob0015Va38iJ3"

if not os.path.exists("Airline_Delay_Cause.csv"):
    gdown.download(f"https://drive.google.com/uc?id={file_id}", "Airline_Delay_Cause.csv", quiet=False, fuzzy=True)

df = pd.read_csv("Airline_Delay_Cause.csv")
df = df.dropna(subset=['arr_flights'])

st.write("Data loaded successfully!")
st.write(f"Total rows: {len(df):,}")
st.write(f"Years: {df['year'].min()} – {df['year'].max()}")
st.write(f"Airlines: {df['carrier_name'].nunique()}")
st.write(f"Airports: {df['airport'].nunique()}")

st.dataframe(df.head(10))
