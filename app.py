import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Airline Delay Dashboard", page_icon="✈️", layout="wide")

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/hetmodi2004/airline_delay_analysis/main/airline_small.csv"
    df = pd.read_csv(url)
    df['delay_rate'] = df['arr_del15'] / df['arr_flights'] * 100
    df['cancel_rate'] = df['arr_cancelled'] / df['arr_flights'] * 100
    df['total_delay_min'] = (df['carrier_delay'] + df['weather_delay'] +
                              df['nas_delay'] + df['security_delay'] +
                              df['late_aircraft_delay'])
    df['season'] = df['month'].map({
        12:'Winter',1:'Winter',2:'Winter',
        3:'Spring', 4:'Spring',5:'Spring',
        6:'Summer', 7:'Summer',8:'Summer',
        9:'Fall',  10:'Fall', 11:'Fall'
    })
    return df

df = load_data()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
st.sidebar.title("🔧 Filters")

year_range = st.sidebar.slider(
    "Year Range",
    int(df['year'].min()),
    int(df['year'].max()),
    (2015, int(df['year'].max()))
)

all_airlines = sorted(df['carrier_name'].unique())
selected_airlines = st.sidebar.multiselect(
    "Select Airlines",
    all_airlines,
    default=all_airlines[:6]
)

all_seasons = ['Winter','Spring','Summer','Fall']
selected_seasons = st.sidebar.multiselect(
    "Select Seasons",
    all_seasons,
    default=all_seasons
)

filtered = df[
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1]) &
    (df['carrier_name'].isin(selected_airlines)) &
    (df['season'].isin(selected_seasons))
]

# ============================================================
# TITLE
# ============================================================
st.title("✈️ Airline Delay Analysis Dashboard")
st.markdown("Exploring why flights get delayed across US airports from 2003–2025")

# ============================================================
# METRIC CARDS
# ============================================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Flights", f"{filtered['arr_flights'].sum():,.0f}")
col2.metric("Total Delayed", f"{filtered['arr_del15'].sum():,.0f}")
col3.metric("Avg Delay Rate", f"{filtered['delay_rate'].mean():.1f}%")
col4.metric("Avg Cancel Rate", f"{filtered['cancel_rate'].mean():.1f}%")

st.divider()

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3 = st.tabs(["📈 Overview", "🏢 By Airline", "🌦️ Delay Causes"])

# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Delay Rate Over Time")
        yearly = filtered.groupby('year')['delay_rate'].mean().reset_index()
        fig1 = px.line(yearly, x='year', y='delay_rate',
                       markers=True,
                       labels={'delay_rate': 'Delay Rate (%)', 'year': 'Year'},
                       title='Average Delay Rate by Year')
        fig1.update_traces(line_color='#1D9E75', line_width=2)
        fig1.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Delay Rate by Season")
        seasonal = filtered.groupby('season')['delay_rate'].mean().reset_index()
        fig2 = px.bar(seasonal, x='season', y='delay_rate',
                      color='season',
                      color_discrete_sequence=['#1D9E75','#BA7517','#378ADD','#D85A30'],
                      labels={'delay_rate': 'Delay Rate (%)', 'season': 'Season'},
                      title='Average Delay Rate by Season')
        fig2.update_layout(paper_bgcolor='white', plot_bgcolor='white', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Monthly Delay Trend")
    monthly = filtered.groupby('month')['delay_rate'].mean().reset_index()
    monthly['month_name'] = monthly['month'].map({
        1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
        7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'
    })
    fig3 = px.line(monthly, x='month_name', y='delay_rate',
                   markers=True,
                   labels={'delay_rate': 'Delay Rate (%)', 'month_name': 'Month'},
                   title='Average Delay Rate by Month')
    fig3.update_traces(line_color='#BA7517', line_width=2)
    fig3.update_layout(paper_bgcolor='white', plot_bgcolor='white')
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# TAB 2 — BY AIRLINE
# ============================================================
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Delay Rate by Airline")
        airline_delay = (
            filtered.groupby('carrier_name')['delay_rate']
            .mean().reset_index()
            .sort_values('delay_rate', ascending=True)
        )
        fig4 = px.bar(airline_delay, x='delay_rate', y='carrier_name',
                      orientation='h',
                      labels={'delay_rate': 'Delay Rate (%)', 'carrier_name': 'Airline'},
                      title='Average Delay Rate by Airline',
                      color='delay_rate',
                      color_continuous_scale='teal')
        fig4.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        st.subheader("Flight Volume by Airline")
        airline_vol = (
            filtered.groupby('carrier_name')['arr_flights']
            .sum().reset_index()
            .sort_values('arr_flights', ascending=True)
        )
        fig5 = px.bar(airline_vol, x='arr_flights', y='carrier_name',
                      orientation='h',
                      labels={'arr_flights': 'Total Flights', 'carrier_name': 'Airline'},
                      title='Total Flights by Airline',
                      color_discrete_sequence=['#378ADD'])
        fig5.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Airline Delay Rate Over Years")
    top5 = (
        filtered.groupby('carrier_name')['arr_flights']
        .sum().nlargest(5).index.tolist()
    )
    airline_yearly = (
        filtered[filtered['carrier_name'].isin(top5)]
        .groupby(['year','carrier_name'])['delay_rate']
        .mean().reset_index()
    )
    fig6 = px.line(airline_yearly, x='year', y='delay_rate',
                   color='carrier_name',
                   markers=True,
                   labels={'delay_rate': 'Delay Rate (%)', 'year': 'Year', 'carrier_name': 'Airline'},
                   title='Delay Rate Over Time — Top 5 Airlines',
                   color_discrete_sequence=['#1D9E75','#BA7517','#378ADD','#D85A30','#888780'])
    fig6.update_layout(paper_bgcolor='white', plot_bgcolor='white')
    st.plotly_chart(fig6, use_container_width=True)

# ============================================================
# TAB 3 — DELAY CAUSES
# ============================================================
with tab3:
    col1, col2 = st.columns(2)

    cause_cols = ['carrier_delay','weather_delay','nas_delay',
                  'security_delay','late_aircraft_delay']
    cause_labels = ['Carrier','Weather','NAS','Security','Late Aircraft']

    with col1:
        st.subheader("Delay Minutes by Cause")
        cause_totals = filtered[cause_cols].sum().values
        fig7 = px.pie(
            names=cause_labels,
            values=cause_totals,
            title='Total Delay Minutes by Cause',
            color_discrete_sequence=['#1D9E75','#BA7517','#378ADD','#D85A30','#888780']
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        st.subheader("Delay Causes by Season")
        season_cause = filtered.groupby('season')[cause_cols].sum().reset_index()
        season_cause.columns = ['season'] + cause_labels
        fig8 = px.bar(season_cause, x='season', y=cause_labels,
                      title='Delay Minutes by Cause and Season',
                      color_discrete_sequence=['#1D9E75','#BA7517','#378ADD','#D85A30','#888780'])
        fig8.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        st.plotly_chart(fig8, use_container_width=True)

    st.subheader("Delay Causes Over Time")
    yearly_causes = filtered.groupby('year')[cause_cols].sum().reset_index()
    yearly_causes.columns = ['year'] + cause_labels
    fig9 = px.area(yearly_causes, x='year', y=cause_labels,
                   title='Delay Minutes by Cause Over Time',
                   color_discrete_sequence=['#1D9E75','#BA7517','#378ADD','#D85A30','#888780'])
    fig9.update_layout(paper_bgcolor='white', plot_bgcolor='white')
    st.plotly_chart(fig9, use_container_width=True)

st.divider()
st.caption("Data source: Bureau of Transportation Statistics (BTS) | Dashboard by Streamlit")
