from datetime import date, timedelta
import pandas as pd
import streamlit as st
import yfinance as yf
from plotly import graph_objs as go
from prophet import Prophet


def download_historical_data(ticker):
    raw_data = yf.download(ticker, start=START, end=TODAY)
    raw_data.reset_index(inplace=True)
    return raw_data


def download_historical_data_today(ticker):
    raw_data = yf.download(ticker, start=YESTERDAY, end=TODAY)
    raw_data.reset_index(inplace=True)
    return raw_data


def download_yesterday_stock_info(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(start=YESTERDAY, end=TODAY, interval="15m")
    hist = pd.DataFrame(hist)
    return hist


def get_stock_price(ticker):
    price = yf.Ticker(ticker).fast_info.last_price
    return round(price, 2)


def remove_nth_line_csv(file_name, n):
    dataf = pd.read_csv(file_name, header=None)
    dataf.drop(dataf.index[n], inplace=True)
    dataf.to_csv(file_name, index=False, header=False)


# SET Title
st.title("Stock Prediction App")
st.write("References: FBProphet, Streamlit, YFinance, Python and Plotly")

# GET Time
START = "2015-01-01"
TODAY = date.today()
YESTERDAY = date.today() + timedelta(days=- 1)

# SET Stocks Selector
stocks = ("SPY", "AAPL", "GOOG", "NVDA", "TSLA", "YPF")
selected_stocks = st.selectbox("Select symbol for prediction", stocks)

# SET Display stock quote
st.subheader("Current price:")
st.write(get_stock_price(selected_stocks))

# SET Prediction Slider
n_years = st.slider("Years of prediction:", 1, 4)
period = n_years * 365

# GET Historical Data
data_load_state = st.text("Loading data..")
d_data = download_historical_data(selected_stocks)
e_data = download_historical_data_today(selected_stocks)
data_load_state.text("Loading data ... done!")

# GET Yesterday's Historical Data
st.subheader("Yesterday Data:")
st.write(download_yesterday_stock_info(selected_stocks))

# CREATE a sample figure
fig = go.Figure()
fig.add_trace(go.Bar(x=d_data.Date, y=d_data.Close[selected_stocks]))
fig.layout.update(title_text=f"Time Series Data For: {selected_stocks}", xaxis_rangeslider_visible=True)

# fig2 = go.Figure()
# fig2.add_trace(go.ColorBar(x=e_data.Date, y=e_data.Close[selected_stocks]))
# fig2.layout.update(title_text=f"Time Series Data For: {selected_stocks}", xaxis_rangeslider_visible=True)

# SET Historical Data Plot
st.plotly_chart(fig)
# st.plotly_chart(fig2)

# SET Forecasting DATA
df_train1 = d_data[['Date', 'Close']]
df_train2 = df_train1.rename(columns={"Date": "ds", "Close": "y"})

# SAVING Forecast to file
df_train2.to_csv('training_input', index=False)
remove_nth_line_csv("training_input", 1)

# PROCESS Forecast
df = pd.read_csv('training_input')
df.head()
m = Prophet()
m.fit(df)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

# SET Display for forecast data
st.subheader("Forecast data:")
data_frame = forecast.tail(366)
data_frame.set_index(data_frame['ds'], inplace=True)
predicted_quote_trend = data_frame.loc[data_frame['ds'] == f"{TODAY} 00:00:00", 'trend']
predicted_quote_yhat_low = data_frame.loc[data_frame['ds'] == f"{TODAY} 00:00:00", 'yhat_lower']
predicted_quote_yhat_high = data_frame.loc[data_frame['ds'] == f"{TODAY} 00:00:00", 'yhat_upper']
st.write(data_frame)

# SET Display daily quote
st.subheader("Current price:")
st.write(get_stock_price(selected_stocks))

# Display MEAN
st.subheader("Mean Predicted price:")
trend_ = predicted_quote_trend[0]
low_ = predicted_quote_yhat_low[0]
high_ = predicted_quote_yhat_high[0]
mean = (trend_+high_+low_) / 3
st.write(round(mean, 2))

# SET Display daily predicted trend
st.subheader("Predicted Trend | Low and High for today:")
st.write(predicted_quote_trend)
st.write(predicted_quote_yhat_low)
st.write(predicted_quote_yhat_high)
