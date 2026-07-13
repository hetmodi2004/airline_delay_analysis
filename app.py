import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="FLIGHT DELAY CONTROL", page_icon="\u2708\ufe0f", layout="wide")

# ============================================================
# DESIGN TOKENS — "Control Tower" identity
# Dark navy ops-room background, amber/teal signal colors
# (the same palette a radar screen or split-flap board would
# use), monospace display type for numbers so it reads like
# real terminal data rather than a generic light dashboard.
# ============================================================
INK      = '#0B1220'
PANEL    = '#111B2E'
LINE     = '#233250'
TEXT     = '#E7ECF5'
SUBTEXT  = '#8593AD'
AMBER    = '#FFB020'
TEAL     = '#37D6C4'
CORAL    = '#FF5D5D'
BLUE     = '#4C8DFF'
VIOLET   = '#9B7BFF'
SEQ = [AMBER, TEAL, BLUE, CORAL, VIOLET]

DISPLAY_FONT = "'JetBrains Mono', 'IBM Plex Mono', monospace"
BODY_FONT = "'Inter', -apple-system, sans-serif"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap');

.stApp {{ background: {INK}; color: {TEXT}; font-family: {BODY_FONT}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 1.5rem; max-width: 1400px; }}

.tower-title {{
    font-family: {DISPLAY_FONT}; font-weight: 800; font-size: 2.1rem;
    letter-spacing: 0.04em; color: {TEXT}; margin: 0;
}}
.tower-title span {{ color: {AMBER}; }}
.tower-sub {{
    font-family: {DISPLAY_FONT}; font-size: 0.78rem; color: {SUBTEXT};
    letter-spacing: 0.12em; text-transform: uppercase;
}}
.tower-clock {{
    font-family: {DISPLAY_FONT}; color: {TEAL}; font-size: 0.85rem;
    letter-spacing: 0.08em; text-align: right;
}}

div[data-testid="stMetric"] {{
    background: {PANEL}; border: 1px solid {LINE}; border-left: 3px solid {AMBER};
    border-radius: 4px; padding: 14px 16px 10px 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.3);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
div[data-testid="stMetric"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.4);
}}
div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) div[data-testid="stMetric"] {{ border-left-color: {AMBER}; }}
div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) div[data-testid="stMetric"] {{ border-left-color: {CORAL}; }}
div[data-testid="stHorizontalBlock"] > div:nth-of-type(3) div[data-testid="stMetric"] {{ border-left-color: {VIOLET}; }}
div[data-testid="stHorizontalBlock"] > div:nth-of-type(4) div[data-testid="stMetric"] {{ border-left-color: {TEAL}; }}
div[data-testid="stHorizontalBlock"] > div:nth-of-type(5) div[data-testid="stMetric"] {{ border-left-color: {BLUE}; }}
div[data-testid="stMetricLabel"] {{
    font-family: {DISPLAY_FONT}; font-size: 0.68rem !important; letter-spacing: 0.1em;
    text-transform: uppercase; color: {SUBTEXT} !important;
}}
div[data-testid="stMetricValue"] {{
    font-family: {DISPLAY_FONT} !important; color: {TEXT} !important; font-weight: 700 !important;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {PANEL} 0%, {INK} 100%);
    border-right: 1px solid {LINE};
}}
section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {{
    color: {SUBTEXT} !important; font-family: {DISPLAY_FONT}; font-size: 0.75rem;
    letter-spacing: 0.06em; text-transform: uppercase;
}}
section[data-testid="stSidebar"] h3 {{
    color: {AMBER} !important; font-family: {DISPLAY_FONT}; letter-spacing: 0.08em;
    border-bottom: 1px solid {LINE}; padding-bottom: 8px;
}}
section[data-testid="stSidebar"] hr {{ border-color: {LINE}; }}

section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"] {{
    background-color: {AMBER} !important; border-color: {AMBER} !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="slider"] > div > div {{
    background: linear-gradient(90deg, {TEAL}, {AMBER}) !important;
}}

section[data-testid="stSidebar"] span[data-baseweb="tag"] {{
    background-color: rgba(255,176,32,0.16) !important;
    border: 1px solid {AMBER} !important;
    color: {TEXT} !important;
}}

button[data-baseweb="tab"] {{
    font-family: {DISPLAY_FONT}; letter-spacing: 0.08em; text-transform: uppercase;
    font-size: 0.8rem; color: {SUBTEXT};
}}
button[data-baseweb="tab"][aria-selected="true"] {{ color: {AMBER} !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: {AMBER} !important; }}
div[data-baseweb="tab-border"] {{ background-color: {LINE} !important; }}

.panel-label {{
    font-family: {DISPLAY_FONT}; font-size: 0.72rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: {AMBER}; border-bottom: 1px solid {LINE};
    padding-bottom: 6px; margin-bottom: 4px; margin-top: 6px;
}}
div[data-testid="stDataFrame"] {{
    font-family: {DISPLAY_FONT};
    border: 1px solid {LINE}; border-radius: 6px; overflow: hidden;
}}
hr {{ border-color: {LINE}; }}
</style>
""", unsafe_allow_html=True)


def apply_layout(fig, h=None):
    """Console-style chart chrome: transparent panel, amber/teal signal colors,
    hairline gridlines only on the axis that carries the comparison."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family=BODY_FONT, color=TEXT, size=12),
        title=dict(font=dict(family=DISPLAY_FONT, size=14, color=TEXT), x=0, xanchor='left'),
        legend=dict(font=dict(color=SUBTEXT, size=11), bgcolor='rgba(0,0,0,0)',
                    orientation='h', y=-0.18),
        margin=dict(t=50, b=40, l=50, r=20), height=h,
        hoverlabel=dict(bgcolor=PANEL, font_color=TEXT, bordercolor=LINE,
                        font_family=DISPLAY_FONT),
    )
    fig.update_xaxes(tickfont=dict(color=SUBTEXT, size=11), showgrid=False,
                     linecolor=LINE, linewidth=1, ticks='outside', tickcolor=LINE,
                     title_font=dict(color=SUBTEXT, size=11))
    fig.update_yaxes(tickfont=dict(color=SUBTEXT, size=11), showgrid=True,
                     gridcolor=LINE, gridwidth=1, zeroline=False,
                     linecolor=LINE, linewidth=1, title_font=dict(color=SUBTEXT, size=11))
    return fig


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
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    })
    return df


df = load_data()

# ============================================================
# MASTHEAD
# ============================================================
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"""
        <p class="tower-sub">Bureau of Transportation Statistics &middot; {int(df['year'].min())}&ndash;{int(df['year'].max())}</p>
        <h1 class="tower-title">FLIGHT<span>DELAY</span>CONTROL</h1>
    """, unsafe_allow_html=True)
with h2:
    st.markdown(f"""
        <div class="tower-clock">LIVE FEED<br>{len(df):,} RECORDS<br>{df['carrier_name'].nunique()} CARRIERS &middot; {df['airport'].nunique()} AIRPORTS</div>
    """, unsafe_allow_html=True)

# ============================================================
# SIDEBAR — OPS PANEL
# ============================================================
st.sidebar.markdown("### \u2708\ufe0f OPS PANEL")
st.sidebar.markdown("**YEAR RANGE**")
year_range = st.sidebar.slider(
    "Year Range", int(df['year'].min()), int(df['year'].max()),
    (2015, int(df['year'].max())), label_visibility="collapsed"
)

st.sidebar.markdown("**CARRIERS**")
all_airlines = sorted(df['carrier_name'].unique())
top6_by_volume = df.groupby('carrier_name')['arr_flights'].sum().nlargest(6).index.tolist()
selected_airlines = st.sidebar.multiselect(
    "Select Airlines", all_airlines, default=top6_by_volume, label_visibility="collapsed"
)

st.sidebar.markdown("**SEASON**")
all_seasons = ['Winter', 'Spring', 'Summer', 'Fall']
selected_seasons = st.sidebar.multiselect(
    "Select Seasons", all_seasons, default=all_seasons, label_visibility="collapsed"
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='font-size:0.68rem; color:{SUBTEXT};'>DATA: BTS &middot; UPDATED THROUGH {int(df['year'].max())}</p>", unsafe_allow_html=True)

filtered = df[
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1]) &
    (df['carrier_name'].isin(selected_airlines)) &
    (df['season'].isin(selected_seasons))
]

cause_cols = ['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']
cause_labels = ['Carrier', 'Weather', 'NAS', 'Security', 'Late Aircraft']

st.markdown("<hr>", unsafe_allow_html=True)

# ============================================================
# METRIC STRIP
# ============================================================
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("TOTAL FLIGHTS", f"{filtered['arr_flights'].sum():,.0f}")
c2.metric("DELAYED", f"{filtered['arr_del15'].sum():,.0f}")
c3.metric("CANCELLED", f"{filtered['arr_cancelled'].sum():,.0f}")
c4.metric("AVG DELAY RATE", f"{filtered['delay_rate'].mean():.1f}%")
c5.metric("AVG CANCEL RATE", f"{filtered['cancel_rate'].mean():.1f}%")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["OVERVIEW", "BY CARRIER", "DELAY CAUSES", "RANKINGS"])

# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="panel-label">Delay Rate &middot; Year over Year</p>', unsafe_allow_html=True)
        yearly = filtered.groupby('year')['delay_rate'].mean().reset_index()
        fig1 = px.line(yearly, x='year', y='delay_rate', markers=True,
                       labels={'delay_rate': 'Delay Rate (%)', 'year': ''})
        fig1.update_traces(line_color=AMBER, line_width=2.5,
                           marker=dict(size=6, color=AMBER, line=dict(width=0)))
        st.plotly_chart(apply_layout(fig1, 320), use_container_width=True)

    with col2:
        st.markdown('<p class="panel-label">Delay Rate &middot; By Season</p>', unsafe_allow_html=True)
        seasonal = filtered.groupby('season')['delay_rate'].mean().reindex(all_seasons).reset_index()
        fig2 = px.bar(seasonal, x='season', y='delay_rate',
                      labels={'delay_rate': 'Delay Rate (%)', 'season': ''},
                      color_discrete_sequence=[TEAL])
        fig2.update_traces(marker_line_width=0)
        st.plotly_chart(apply_layout(fig2, 320), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="panel-label">Monthly Delay Pattern</p>', unsafe_allow_html=True)
        monthly = filtered.groupby('month')['delay_rate'].mean().reset_index()
        monthly['month_name'] = monthly['month'].map({1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                                                        7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})
        fig3 = px.area(monthly, x='month_name', y='delay_rate',
                       labels={'delay_rate': 'Delay Rate (%)', 'month_name': ''},
                       color_discrete_sequence=[BLUE])
        fig3.update_traces(line_width=2)
        st.plotly_chart(apply_layout(fig3, 300), use_container_width=True)

    with col4:
        st.markdown('<p class="panel-label">Total Delay Minutes &middot; Year over Year</p>', unsafe_allow_html=True)
        yearly_delay = filtered.groupby('year')['total_delay_min'].sum().reset_index()
        fig5 = px.bar(yearly_delay, x='year', y='total_delay_min',
                      labels={'total_delay_min': 'Delay Minutes', 'year': ''},
                      color_discrete_sequence=[VIOLET])
        fig5.update_traces(marker_line_width=0)
        st.plotly_chart(apply_layout(fig5, 300), use_container_width=True)

# ============================================================
# TAB 2 — BY CARRIER
# ============================================================
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="panel-label">Delay Rate &middot; By Carrier</p>', unsafe_allow_html=True)
        airline_delay = (filtered.groupby('carrier_name')['delay_rate'].mean()
                         .reset_index().sort_values('delay_rate'))
        fig6 = px.bar(airline_delay, x='delay_rate', y='carrier_name', orientation='h',
                      labels={'delay_rate': 'Delay Rate (%)', 'carrier_name': ''},
                      color='delay_rate',
                      color_continuous_scale=[[0, TEAL], [0.5, AMBER], [1, CORAL]])
        fig6.update_traces(marker_line_width=0)
        fig6.update_layout(coloraxis_showscale=False)
        st.plotly_chart(apply_layout(fig6, 380), use_container_width=True)

    with col2:
        st.markdown('<p class="panel-label">Top Carriers &middot; Delay Rate Trend</p>', unsafe_allow_html=True)
        top5 = filtered.groupby('carrier_name')['arr_flights'].sum().nlargest(5).index.tolist()
        airline_yearly = (filtered[filtered['carrier_name'].isin(top5)]
                          .groupby(['year', 'carrier_name'])['delay_rate'].mean().reset_index())
        fig8 = px.line(airline_yearly, x='year', y='delay_rate', color='carrier_name', markers=True,
                       labels={'delay_rate': 'Delay Rate (%)', 'year': '', 'carrier_name': ''},
                       color_discrete_sequence=SEQ)
        fig8.update_traces(line_width=2, marker=dict(size=5))
        st.plotly_chart(apply_layout(fig8, 380), use_container_width=True)

    st.markdown('<p class="panel-label">Flight Volume &middot; By Carrier</p>', unsafe_allow_html=True)
    airline_vol = (filtered.groupby('carrier_name')['arr_flights'].sum()
                  .reset_index().sort_values('arr_flights'))
    fig9 = px.bar(airline_vol, x='arr_flights', y='carrier_name', orientation='h',
                  labels={'arr_flights': 'Total Flights', 'carrier_name': ''},
                  color_discrete_sequence=[BLUE])
    fig9.update_traces(marker_line_width=0)
    st.plotly_chart(apply_layout(fig9, 340), use_container_width=True)

# ============================================================
# TAB 3 — DELAY CAUSES
# ============================================================
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="panel-label">Delay Minutes &middot; By Cause</p>', unsafe_allow_html=True)
        cause_totals = filtered[cause_cols].sum().values
        fig10 = px.pie(names=cause_labels, values=cause_totals, hole=0.62,
                       color_discrete_sequence=SEQ)
        fig10.update_traces(textfont=dict(color=TEXT, family=DISPLAY_FONT, size=12),
                            textinfo='percent', marker=dict(line=dict(color=INK, width=2)))
        st.plotly_chart(apply_layout(fig10, 360), use_container_width=True)

    with col2:
        st.markdown('<p class="panel-label">Delay Causes &middot; By Season</p>', unsafe_allow_html=True)
        season_cause = filtered.groupby('season')[cause_cols].sum().reindex(all_seasons).reset_index()
        season_cause.columns = ['season'] + cause_labels
        fig11 = px.bar(season_cause, x='season', y=cause_labels,
                       labels={'value': 'Delay Minutes', 'season': ''},
                       color_discrete_sequence=SEQ)
        fig11.update_traces(marker_line_width=0)
        st.plotly_chart(apply_layout(fig11, 360), use_container_width=True)

    st.markdown('<p class="panel-label">Delay Causes &middot; Year over Year</p>', unsafe_allow_html=True)
    yearly_causes = filtered.groupby('year')[cause_cols].sum().reset_index()
    yearly_causes.columns = ['year'] + cause_labels
    fig12 = px.area(yearly_causes, x='year', y=cause_labels,
                    labels={'value': 'Delay Minutes', 'year': ''},
                    color_discrete_sequence=SEQ)
    st.plotly_chart(apply_layout(fig12, 340), use_container_width=True)

    st.markdown('<p class="panel-label">Delay Cause Breakdown &middot; By Carrier</p>', unsafe_allow_html=True)
    airline_cause = filtered.groupby('carrier_name')[cause_cols].sum().reset_index()
    airline_cause.columns = ['Carrier'] + cause_labels
    fig13 = px.bar(airline_cause, x='Carrier', y=cause_labels,
                   labels={'value': 'Delay Minutes'},
                   color_discrete_sequence=SEQ)
    fig13.update_traces(marker_line_width=0)
    fig13.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(apply_layout(fig13, 380), use_container_width=True)

# ============================================================
# TAB 4 — RANKINGS
# ============================================================
with tab4:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="panel-label">Best Carriers &middot; Lowest Delay Rate</p>', unsafe_allow_html=True)
        best = (filtered.groupby('carrier_name')
               .agg(avg_delay=('delay_rate', 'mean'), total_flights=('arr_flights', 'sum'))
               .reset_index().sort_values('avg_delay').head(10))
        best.columns = ['Carrier', 'Avg Delay Rate (%)', 'Total Flights']
        best['Avg Delay Rate (%)'] = best['Avg Delay Rate (%)'].round(2)
        st.dataframe(best, use_container_width=True, hide_index=True)

    with col2:
        st.markdown('<p class="panel-label">Worst Carriers &middot; Highest Delay Rate</p>', unsafe_allow_html=True)
        worst = (filtered.groupby('carrier_name')
                .agg(avg_delay=('delay_rate', 'mean'), total_flights=('arr_flights', 'sum'))
                .reset_index().sort_values('avg_delay', ascending=False).head(10))
        worst.columns = ['Carrier', 'Avg Delay Rate (%)', 'Total Flights']
        worst['Avg Delay Rate (%)'] = worst['Avg Delay Rate (%)'].round(2)
        st.dataframe(worst, use_container_width=True, hide_index=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="panel-label">Best Airports &middot; Lowest Delay Rate</p>', unsafe_allow_html=True)
        best_airport = (filtered.groupby('airport')
                        .agg(avg_delay=('delay_rate', 'mean'), total_flights=('arr_flights', 'sum'))
                        .reset_index().sort_values('avg_delay').head(10))
        best_airport.columns = ['Airport', 'Avg Delay Rate (%)', 'Total Flights']
        best_airport['Avg Delay Rate (%)'] = best_airport['Avg Delay Rate (%)'].round(2)
        st.dataframe(best_airport, use_container_width=True, hide_index=True)

    with col4:
        st.markdown('<p class="panel-label">Worst Airports &middot; Highest Delay Rate</p>', unsafe_allow_html=True)
        worst_airport = (filtered.groupby('airport')
                         .agg(avg_delay=('delay_rate', 'mean'), total_flights=('arr_flights', 'sum'))
                         .reset_index().sort_values('avg_delay', ascending=False).head(10))
        worst_airport.columns = ['Airport', 'Avg Delay Rate (%)', 'Total Flights']
        worst_airport['Avg Delay Rate (%)'] = worst_airport['Avg Delay Rate (%)'].round(2)
        st.dataframe(worst_airport, use_container_width=True, hide_index=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""
    <p style="font-family:{DISPLAY_FONT}; font-size:0.7rem; color:{SUBTEXT}; letter-spacing:0.08em;">
    DATA SOURCE: BUREAU OF TRANSPORTATION STATISTICS (BTS) &middot; DASHBOARD: STREAMLIT + PLOTLY
    </p>
""", unsafe_allow_html=True)
