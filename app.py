import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Airline Delay Dashboard", page_icon="✈️", layout="wide")

# ============================================================
# COLORS
# ============================================================
TEAL  = '#1D9E75'
AMBER = '#BA7517'
BLUE  = '#378ADD'
CORAL = '#D85A30'
GREY  = '#888780'
COLORS = [TEAL, AMBER, BLUE, CORAL, GREY]

LAYOUT = dict(
    paper_bgcolor='#F8F9FA',
    plot_bgcolor='#F8F9FA',
    font=dict(color='#1a1a1a', size=13),
    title_font=dict(size=16, color='#1a1a1a'),
    xaxis=dict(
        tickfont=dict(color='#1a1a1a', size=12),
        titlefont=dict(color='#1a1a1a', size=13),
        linecolor='#333333',
        linewidth=1,
        gridcolor='#E0E0E0'
    ),
    yaxis=dict(
        tickfont=dict(color='#1a1a1a', size=12),
        titlefont=dict(color='#1a1a1a', size=13),
        linecolor='#333333',
        linewidth=1,
        gridcolor='#E0E0E0'
    ),
    legend=dict(
        font=dict(color='#1a1a1a', size=12),
        bgcolor='#F8F9FA',
        borderwidth=1,
        bordercolor='#E0E0E0'
    ),
    margin=dict(t=60, b=60, l=60, r=40)
)

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

cause_cols   = ['carrier_delay','weather_delay','nas_delay','security_delay','late_aircraft_delay']
cause_labels = ['Carrier','Weather','NAS','Security','Late Aircraft']

# ============================================================
# TITLE
# ============================================================
st.title("✈️ Airline Delay Analysis Dashboard")
st.markdown("Exploring why flights get delayed across US airports from 2003–2025")

# ============================================================
# METRIC CARDS
# ============================================================
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Flights",   f"{filtered['arr_flights'].sum():,.0f}")
col2.metric("Total Delayed",   f"{filtered['arr_del15'].sum():,.0f}")
col3.metric("Total Cancelled", f"{filtered['arr_cancelled'].sum():,.0f}")
col4.metric("Avg Delay Rate",  f"{filtered['delay_rate'].mean():.1f}%")
col5.metric("Avg Cancel Rate", f"{filtered['cancel_rate'].mean():.1f}%")

st.divider()

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview",
    "🏢 By Airline",
    "🌦️ Delay Causes",
    "🏆 Rankings"
])

# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Delay Rate Over Time")
        yearly = filtered.groupby('year')['delay_rate'].mean().reset_index()
        fig1 = px.line(yearly, x='year', y='delay_rate', markers=True,
                       labels={'delay_rate':'Delay Rate (%)','year':'Year'},
                       title='Average Delay Rate by Year')
        fig1.update_traces(line_color=TEAL, line_width=3,
                           marker=dict(size=8, color=TEAL))
        fig1.update_layout(**LAYOUT)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Delay Rate by Season")
        seasonal = filtered.groupby('season')['delay_rate'].mean().reset_index()
        fig2 = px.bar(seasonal, x='season', y='delay_rate', color='season',
                      color_discrete_map={
                          'Winter':BLUE,'Spring':TEAL,
                          'Summer':AMBER,'Fall':CORAL
                      },
                      labels={'delay_rate':'Delay Rate (%)','season':'Season'},
                      title='Average Delay Rate by Season')
        fig2.update_layout(**LAYOUT, showlegend=False)
        fig2.update_traces(marker_line_color='#333333', marker_line_width=1)
        st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Delay Trend")
        monthly = filtered.groupby('month')['delay_rate'].mean().reset_index()
        monthly['month_name'] = monthly['month'].map({
            1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
            7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'
        })
        fig3 = px.line(monthly, x='month_name', y='delay_rate', markers=True,
                       labels={'delay_rate':'Delay Rate (%)','month_name':'Month'},
                       title='Average Delay Rate by Month')
        fig3.update_traces(line_color=AMBER, line_width=3,
                           marker=dict(size=8, color=AMBER))
        fig3.update_layout(**LAYOUT)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.subheader("Cancellation Rate Over Time")
        yearly_cancel = filtered.groupby('year')['cancel_rate'].mean().reset_index()
        fig4 = px.bar(yearly_cancel, x='year', y='cancel_rate',
                      labels={'cancel_rate':'Cancel Rate (%)','year':'Year'},
                      title='Average Cancellation Rate by Year',
                      color_discrete_sequence=[CORAL])
        fig4.update_traces(marker_line_color='#333333', marker_line_width=1)
        fig4.update_layout(**LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Total Delay Minutes Over Time")
    yearly_delay = filtered.groupby('year')['total_delay_min'].sum().reset_index()
    fig5 = px.area(yearly_delay, x='year', y='total_delay_min',
                   labels={'total_delay_min':'Total Delay Minutes','year':'Year'},
                   title='Total Delay Minutes by Year',
                   color_discrete_sequence=[BLUE])
    fig5.update_layout(**LAYOUT)
    st.plotly_chart(fig5, use_container_width=True)

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
        fig6 = px.bar(airline_delay, x='delay_rate', y='carrier_name',
                      orientation='h',
                      labels={'delay_rate':'Delay Rate (%)','carrier_name':'Airline'},
                      title='Average Delay Rate by Airline',
                      color='delay_rate',
                      color_continuous_scale=[
                          [0,'#1D9E75'],[0.5,'#BA7517'],[1,'#D85A30']
                      ])
        fig6.update_traces(marker_line_color='#333333', marker_line_width=1)
        fig6.update_layout(**LAYOUT)
        st.plotly_chart(fig6, use_container_width=True)

    with col2:
        st.subheader("Cancellation Rate by Airline")
        airline_cancel = (
            filtered.groupby('carrier_name')['cancel_rate']
            .mean().reset_index()
            .sort_values('cancel_rate', ascending=True)
        )
        fig7 = px.bar(airline_cancel, x='cancel_rate', y='carrier_name',
                      orientation='h',
                      labels={'cancel_rate':'Cancel Rate (%)','carrier_name':'Airline'},
                      title='Average Cancellation Rate by Airline',
                      color='cancel_rate',
                      color_continuous_scale=[
                          [0,'#378ADD'],[0.5,'#BA7517'],[1,'#D85A30']
                      ])
        fig7.update_traces(marker_line_color='#333333', marker_line_width=1)
        fig7.update_layout(**LAYOUT)
        st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Top 5 Airlines — Delay Rate Over Years")
    top5 = (
        filtered.groupby('carrier_name')['arr_flights']
        .sum().nlargest(5).index.tolist()
    )
    airline_yearly = (
        filtered[filtered['carrier_name'].isin(top5)]
        .groupby(['year','carrier_name'])['delay_rate']
        .mean().reset_index()
    )
    fig8 = px.line(airline_yearly, x='year', y='delay_rate',
                   color='carrier_name', markers=True,
                   labels={'delay_rate':'Delay Rate (%)','year':'Year','carrier_name':'Airline'},
                   title='Delay Rate Over Time — Top 5 Airlines',
                   color_discrete_sequence=COLORS)
    fig8.update_traces(line_width=2)
    fig8.update_layout(**LAYOUT)
    st.plotly_chart(fig8, use_container_width=True)

    st.subheader("Flight Volume by Airline")
    airline_vol = (
        filtered.groupby('carrier_name')['arr_flights']
        .sum().reset_index()
        .sort_values('arr_flights', ascending=True)
    )
    fig9 = px.bar(airline_vol, x='arr_flights', y='carrier_name',
                  orientation='h',
                  labels={'arr_flights':'Total Flights','carrier_name':'Airline'},
                  title='Total Flights by Airline',
                  color_discrete_sequence=[BLUE])
    fig9.update_traces(marker_line_color='#333333', marker_line_width=1)
    fig9.update_layout(**LAYOUT)
    st.plotly_chart(fig9, use_container_width=True)

# ============================================================
# TAB 3 — DELAY CAUSES
# ============================================================
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Delay Minutes by Cause")
        cause_totals = filtered[cause_cols].sum().values
        fig10 = px.pie(names=cause_labels, values=cause_totals,
                       title='Total Delay Minutes by Cause',
                       color_discrete_sequence=COLORS,
                       hole=0.3)
        fig10.update_traces(
            textfont=dict(color='#1a1a1a', size=13),
            textinfo='percent+label'
        )
        fig10.update_layout(**LAYOUT)
        st.plotly_chart(fig10, use_container_width=True)

    with col2:
        st.subheader("Delay Causes by Season")
        season_cause = filtered.groupby('season')[cause_cols].sum().reset_index()
        season_cause.columns = ['season'] + cause_labels
        fig11 = px.bar(season_cause, x='season', y=cause_labels,
                       title='Delay Minutes by Cause and Season',
                       color_discrete_sequence=COLORS)
        fig11.update_traces(marker_line_color='#333333', marker_line_width=0.5)
        fig11.update_layout(**LAYOUT)
        st.plotly_chart(fig11, use_container_width=True)

    st.subheader("Delay Causes Over Time")
    yearly_causes = filtered.groupby('year')[cause_cols].sum().reset_index()
    yearly_causes.columns = ['year'] + cause_labels
    fig12 = px.area(yearly_causes, x='year', y=cause_labels,
                    title='Delay Minutes by Cause Over Time',
                    color_discrete_sequence=COLORS)
    fig12.update_layout(**LAYOUT)
    st.plotly_chart(fig12, use_container_width=True)

    st.subheader("Delay Cause Breakdown by Airline")
    airline_cause = filtered.groupby('carrier_name')[cause_cols].sum().reset_index()
    airline_cause.columns = ['Airline'] + cause_labels
    fig13 = px.bar(airline_cause, x='Airline', y=cause_labels,
                   title='Delay Minutes by Cause per Airline',
                   color_discrete_sequence=COLORS)
    fig13.update_traces(marker_line_color='#333333', marker_line_width=0.5)
    fig13.update_layout(**LAYOUT, xaxis_tickangle=-45)
    st.plotly_chart(fig13, use_container_width=True)

# ============================================================
# TAB 4 — RANKINGS
# ============================================================
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Best Airlines (Lowest Delay Rate)")
        best = (
            filtered.groupby('carrier_name')
            .agg(avg_delay=('delay_rate','mean'),
                 total_flights=('arr_flights','sum'))
            .reset_index()
            .sort_values('avg_delay')
            .head(10)
        )
        best.columns = ['Airline','Avg Delay Rate (%)','Total Flights']
        best['Avg Delay Rate (%)'] = best['Avg Delay Rate (%)'].round(2)
        st.dataframe(best, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("⚠️ Worst Airlines (Highest Delay Rate)")
        worst = (
            filtered.groupby('carrier_name')
            .agg(avg_delay=('delay_rate','mean'),
                 total_flights=('arr_flights','sum'))
            .reset_index()
            .sort_values('avg_delay', ascending=False)
            .head(10)
        )
        worst.columns = ['Airline','Avg Delay Rate (%)','Total Flights']
        worst['Avg Delay Rate (%)'] = worst['Avg Delay Rate (%)'].round(2)
        st.dataframe(worst, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Best Airports (Lowest Delay Rate)")
        best_airport = (
            filtered.groupby('airport')
            .agg(avg_delay=('delay_rate','mean'),
                 total_flights=('arr_flights','sum'))
            .reset_index()
            .sort_values('avg_delay')
            .head(10)
        )
        best_airport.columns = ['Airport','Avg Delay Rate (%)','Total Flights']
        best_airport['Avg Delay Rate (%)'] = best_airport['Avg Delay Rate (%)'].round(2)
        st.dataframe(best_airport, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("⚠️ Worst Airports (Highest Delay Rate)")
        worst_airport = (
            filtered.groupby('airport')
            .agg(avg_delay=('delay_rate','mean'),
                 total_flights=('arr_flights','sum'))
            .reset_index()
            .sort_values('avg_delay', ascending=False)
            .head(10)
        )
        worst_airport.columns = ['Airport','Avg Delay Rate (%)','Total Flights']
        worst_airport['Avg Delay Rate (%)'] = worst_airport['Avg Delay Rate (%)'].round(2)
        st.dataframe(worst_airport, use_container_width=True, hide_index=True)

st.divider()
st.caption("Data source: Bureau of Transportation Statistics (BTS) | Dashboard by Streamlit")
