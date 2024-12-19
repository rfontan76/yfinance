from datetime import date
import streamlit as st

# Title
st.title("Stock Prediction App")
st.write("References: FBProphet, Streamlit, YFinance, Python and Plotly")

# Time
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Stocks Selector
stocks = ("SPY", "AAPL", "GOOG", "NVDA")
selected_stocks = st.selectbox("Select symbol for prediction", stocks)

