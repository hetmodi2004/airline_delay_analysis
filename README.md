# ✈️ Airline Delay Analysis Dashboard

## Overview
This project analyzes US airline delay data from 2003–2025 using the Bureau of Transportation Statistics (BTS) dataset. It explores patterns in flight delays across airlines, airports, seasons, and delay causes.

## Dataset
- **Source:** Bureau of Transportation Statistics (BTS)
- **File:** airline_small.csv
- **Rows:** ~397,000
- **Years:** 2003–2025
- **Features:** Year, Month, Carrier, Airport, Delay causes (Weather, NAS, Carrier, Security, Late Aircraft)

## Project Structure
airline_delay_analysis/
├── app.py                  # Streamlit dashboard
├── airline_small.csv       # Cleaned dataset
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation

## Dashboard Features
- 📈 Overview — delay trends over time, seasonal and monthly patterns
- 🏢 By Airline — delay rates, cancellations, flight volumes per airline
- 🌦️ Delay Causes — breakdown by cause over time and by season
- 🏆 Rankings — best and worst airlines and airports
- 🔧 Sidebar filters — filter by year range, airline, and season
- 
## Live Dashboard
👉 https://your-app-url.streamlit.app

## How to Run Locally
pip install -r requirements.txt
streamlit run app.py

## Tools Used
- Python
- Pandas
- Plotly
- Streamlit

## Author
Het Modi
Data Visualization Final Project — 2026
