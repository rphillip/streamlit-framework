import pandas as pd
import streamlit as st
import numpy as np
import requests
import altair as alt
from datetime import datetime as dt
from datetime import timedelta
try:
    import simplejson as json
except ImportError:
    import json


# Remarks on purpose of App
st.title("Stock Ticker Graph using Streamlit")
st.markdown("This is a submission for milestone 10. Below we enter a stock ticker symbol which generates a graph \
    of the closing price for the last month.")
# Search for symbol using AV api with ticker parameter passed, returns most likely symbol.
def symbolsearch(ticker):
#ask for SYMBOL TO SEARCH
    url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords='+ ticker +'&apikey=2PDL16JADXWMGWKT'
    r = requests.get(url)
    data = r.json()
    df = pd.json_normalize(data["bestMatches"])
    #st.dataframe(df)
    #OUTPUT to Sidebar the search results
    st.sidebar.write("Ticker = ", df.loc[0,"1. symbol"], "Likely Match? = ", float(df.loc[0,"9. matchScore"])*100, "%")
    return df.loc[0,"1. symbol"]

#Retrieves the last month of data of passed ticker symbol parameter. Returns a dataframe
def monthofdailyclose(ticker):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+ ticker +'&apikey=2PDL16JADXWMGWKT'
    r = requests.get(url)
    data = r.json()
    closeondatetime={}
    dailydata = data["Time Series (Daily)"]
    for key in dailydata:
        closevalue = dailydata[key]["4. close"]
        newkey = dt.strptime(key,"%Y-%m-%d")
        newkey = newkey + timedelta(hours=16)
        closeondatetime[newkey]= closevalue
    df=pd.DataFrame(list(closeondatetime.items()))
    df.columns = ['Date', 'Close Value (USD)']
    #st.dataframe(df)
    today = pd.datetime.now().date()
    lastmonth = today - pd.DateOffset(months=1)
    lastmonthdf = df[df['Date']>= lastmonth]
    return lastmonthdf
#ASK for USER input
ticker = st.sidebar.text_input("Enter Stock Ticker Symbol")
button_status = st.sidebar.button('submit')
#When submit button is clicked then the search and output starts
if(button_status):
    #search for symbol in AV API
    ticker = symbolsearch(ticker)
    #retrieve the last month of data
    lastmonthdata = monthofdailyclose(ticker)
    #brush = alt.selection(type='interval', encodings=['x'])

    # OUTPUT of APP. Displays interactive chart using Altair
    chart = alt.Chart(lastmonthdata).mark_line().encode(
        x=alt.X('Date:T', scale=alt.Scale(zero=False)),
        y=alt.Y('Close Value (USD):Q', axis=alt.Axis(format='$'), scale=alt.Scale(zero=False)),
        tooltip=['Date', 'Close Value (USD)']
    ).interactive(

    #).add_selection(
    #    brush
    ).properties(
        title="Stock Price of " + ticker + " over the last month"
    )
    #avg = alt.Chart().mark_rule(color='firebrick').encode(
    #    y=alt.Y('mean(Close Value (USD)):Q'),
    #    size=alt.SizeValue(3)
    #).transform_filter(
    #    brush
    #)
    #graph = alt.layer(chart, avg, data=lastmonthdata)
    st.altair_chart(chart, use_container_width=True)
