import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Airline Delay Dashboard", page_icon="✈️", layout="wide")

st.title("✈️ Airline Delay Dashboard")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/hetmodi2004/airline_delay_analysis/main/airline_small.csv"
    df = pd.read_csv(url)
    df['delay_rate'] = df['arr_del15'] / df['arr_flights'] * 100
    df['cancel_rate'] = df['arr_cancelled'] / df['arr_flights'] * 100
    df['total_delay_min'] = (df['carrier_delay'] + df['weather_delay'] +
                              df['nas_delay'] + df['security_delay'] +
                              df['late_aircraft_delay'])
    return df

df = load_data()

# METRIC CARDS
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Flights", f"{df['arr_flights'].sum():,.0f}")
col2.metric("Total Delayed", f"{df['arr_del15'].sum():,.0f}")
col3.metric("Avg Delay Rate", f"{df['delay_rate'].mean():.1f}%")
col4.metric("Avg Cancel Rate", f"{df['cancel_rate'].mean():.1f}%")

st.divider()

# CHART
st.subheader("📈 Delay Rate Over Time")
yearly = df.groupby('year')['delay_rate'].mean().reset_index()
fig = px.line(yearly, x='year', y='delay_rate',
              markers=True,
              labels={'delay_rate': 'Delay Rate (%)', 'year': 'Year'},
              title='Average Delay Rate by Year')
fig.update_traces(line_color='#1D9E75', line_width=2)
fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df.head(10))
