#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

import os
import pandas as pd
pd.set_option("max_rows", 30)
import datetime
import requests_cache
import sys
import time
import requests
from pandas.io.common import urlencode
from pandas.tseries.frequencies import to_offset



#import pymongo
#from pymongo import MongoClient
#from alpha_vantage.timeseries import TimeSeries
#from pandas import Series,DataFrame

ALPHAVANTAGE_API_URL = "http://www.alphavantage.co/query"
ALPHAVANTAGE_API_KEY_DEFAULT = "BCG76IDVSIVKYQVJ"


def _init_session(session):
    if session is None:
        session = requests.Session()
    return session


def _url(url, params):
    if params is not None and len(params) > 0:
        return url + "?" + urlencode(params)
    else:
        return url

def get_ts_data(symbol=None, interval=None, outputsize=None, api_key=None, adjusted=False, session=None):
    session = _init_session(session)
    if symbol  != 'CCRO3':
        symbol = symbol + '.SA'
    # apikey
    if api_key is None:
        api_key = ALPHAVANTAGE_API_KEY_DEFAULT

    # function
    d_functions = {
        to_offset("D").freqstr: "TIME_SERIES_DAILY",
        to_offset("W").freqstr: "TIME_SERIES_WEEKLY",
        to_offset("M").freqstr: "TIME_SERIES_MONTHLY",
    }
    try:
        if adjusted and to_offset(interval).freqstr == "D":
            function_api = "TIME_SERIES_DAILY_ADJUSTED"
        else:
            function_api = d_functions[to_offset(interval).freqstr]
    except KeyError:
        function_api = "TIME_SERIES_INTRADAY"

    #`interval
    if interval is None:
        interval = "D"
    d_intervals = {
        to_offset("1T").freqstr: "1min",
        to_offset("5T").freqstr: "5min",
        to_offset("15T").freqstr: "15min",
        to_offset("30T").freqstr: "30min",
        to_offset("H").freqstr: "60min",
        to_offset("D").freqstr: "daily",
        to_offset("W").freqstr: "weekly",
        to_offset("M").freqstr: "monthly"
    }
    try:
        interval_api = d_intervals[to_offset(interval).freqstr]
    except KeyError:
        interval_api = "60min"

    # outputsize
    if outputsize is None:
        outputsize = "compact"

    params = {
        "function": function_api,
        "symbol": symbol,
        "interval": interval_api,
        "outputsize": outputsize,
        "apikey": api_key
    }
    execution_mode = 'debug'
    if execution_mode  == 'debug':
        print (params)
    print (ALPHAVANTAGE_API_URL)
    with requests.Session() as s:
        r = s.get(ALPHAVANTAGE_API_URL, params=params)
        url_long= _url(ALPHAVANTAGE_API_URL, params)
        if execution_mode  == 'debug':
            print(url_long)
        if r.status_code == requests.codes.ok:
            dat = r.json()
            #print dat
            metadata = dat["Meta Data"]
            key_dat = list(dat.keys())[1]  # ugly
            ts = dat[key_dat]
            df = pd.DataFrame(ts).T
            df = df.rename(columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume",
            })
            df["Volume"] = df["Volume"].astype(int)
            df.index = pd.to_datetime(df.index)
            df.index.name = "Date"
            for col in ["Open", "High", "Low", "Close","HL_PCT","PCT_change"]:
                if col in df.columns:
                    df[col] = df[col].astype(float)
            hilo = (df['High'] - df['Low']) / df['Close'] * 99.0
            df['HL_PCT'] = hilo
            change = (df['Close'] - df['Open']) / df['Open'] * 100.0
            df['PCT_change'] = change
            return df , metadata
        else:
            params["apikey"] = "HIDDEN"
            raise Exception(r.status_code, r.reason, url_long)

papel = sys.argv

# moving average
# moving_average = df['score'].rolling(window=period).mean().iloc[-1]
expire_after = datetime.timedelta(days=1)
session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
#symbols = ['^BVSP','ITUB4','BBAS3','GOAU4','MRVE3','PETR4','VALE3','ABEV3']
#symbols = ['ITUB4','BBAS3','GOAU4','MRVE3','PETR4','VALE3','ABEV3','CCRO3']
symbols = ['ITUB4']
api_key = os.environ.get("ALPHAVANTAGE_API_KEY") 
interval = "D"
#client = InfluxDBClient('localhost', 8086, 'root', 'root', 'undercontrol_stocks')
# You can generate a Token from the "Tokens Tab" in the UI


from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "_jlwPA9a8_p1yecgevGkxPR18BwBBddiTjaVoRpn_ZQsLj093jocHEI2NQZaSx3RdlPW7e0kT-4KMef7n5zikQ=="
org = "cromo.jml@gmail.com"
bucket = "cromo.jml's Bucket"

client = InfluxDBClient(url="https://eastus-1.azure.cloud2.influxdata.com", token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)


for symbol in symbols:
   print ("Parsing data for %s",symbol)
   try:
         #df_temp = pd.read_csv("assets/{}.csv".format(symbol), sep='\t', index_col="Date", parse_dates=True,usecols=['Date', 'Close'], na_values=['nan'])
         #last_date = df_temp.index[-1]
         #last_date = df_temp.iloc[-1]
        # print ("Last date is got data of %s was %s",last_date)
         df, metadata = get_ts_data(symbol="{}".format(symbol), interval="D", api_key=api_key, session=session)
         #df =  df[df.index > last_date]
         print (df.tail)
         save_csv = False
         #if save_csv:
         #ddf.to_csv('assets/{}.csv'.format(symbol),sep='\t',header=True)

        

        #data = "mem,host=host1 used_percent=23.43234543"
         write_api.write(bucket, record=df, data_frame_measurement_name='stock',data_frame_tag_columns=['stock'])
        #write_api.write(bucket, org, df.to_json())
        #client.create_database('undercontrol_stocks')
         df.to_json('assets/{}.csv'.format(symbol))

   except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
write_api.__del__()
client.__del__()