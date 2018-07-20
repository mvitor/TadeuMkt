import requests
from pandas.io.common import urlencode
from pandas.tseries.frequencies import to_offset
import pandas as pd


#import pymongo
#from pymongo import MongoClient
#from alpha_vantage.timeseries import TimeSeries
#from pandas import Series,DataFrame

ALPHAVANTAGE_API_URL = "http://www.alphavantage.co/query"
ALPHAVANTAGE_API_KEY_DEFAULT = "BCG76IDVSIVKYQVJ"



# https://gist.github.com/femtotrader/e57bc5aefb15d41de379b8dd5cefc802

# Stock data
#ts = TimeSeries(key='BCG76IDVSIVKYQVJ')
#data, meta_data = ts.get_intraday('CSNA3')

# Connect DB
#connection = MongoClient('mongodb://localhost:27017/marketing')
#connection.database_names()
#db = connection.marketing


# Save DB
#stocks = db.CSNA3

#from bson import json_util
#data = json_util.loads(data)

#jsonString = jsonString.replace("\"_id\":", "\"id\":");

#stock_id = stocks.insert(data,check_keys=False)




#for stock in db.CSNA3.find({}):
#    print stock.
#, {'entities.user_mentions.screen_name':1}).sort({u'entities.user_mentions.screen_name':1}):

#print (stock_id)
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

    # interval
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
    print (params)
    r = session.get(ALPHAVANTAGE_API_URL, params=params)
    url_long= _url(ALPHAVANTAGE_API_URL, params)

    # print(url_long)
    if r.status_code == requests.codes.ok:
        #ts = TimeSeries(key='BCG76IDVSIVKYQVJ')
        #dat, meta_data = ts.get_intraday('CSNA3')
        dat = r.json()
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
        for col in ["Open", "High", "Low", "Close"]:
            if col in df.columns:
                df[col] = df[col].astype(float)
        df["Volume"] = df["Volume"].astype(int)
        df.index = pd.to_datetime(df.index)
        df.index.name = "Date"
        return df , metadata
    else:
        params["apikey"] = "HIDDEN"
        raise Exception(r.status_code, r.reason, url_long)


import os
import pandas as pd
pd.set_option("max_rows", 30)
import datetime
import requests_cache
import sys
import time
papel = sys.argv

# moving average
# moving_average = df['score'].rolling(window=period).mean().iloc[-1]
expire_after = datetime.timedelta(days=1)
session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
symbols = ['ITUB4','BBAS3','GOAU4','MRVE3','BBDC4','PETR4','CCRO3','VAlE3','ABEV3']
#symbols = ['^BVSP']
#symbols = ['ABEV3']
api_key = os.environ.get("ALPHAVANTAGE_API_KEY")  # api_key = "YOURAPIKEY"
interval = "5T"
for symbol in symbols:
    # new symbols
#df = get_ts_data(symbol="CCRO3.SA", interval="D", api_key=api_key, session=session)
    print ("Parsing data for %s",symbol)
    #df_temp = pd.read_csv("csvs/{}.csv".format(symbol), sep='\t', index_col="Date", parse_dates=True,usecols=['Date', 'Close'], na_values=['nan'])
    #last_date = df_temp.index[-1]
    #del df_temp
    #print ("Last date is got data of %s was %s",last_date)
    df, metadata = get_ts_data(symbol="{}".format(symbol), interval="D", api_key=api_key, session=session)

    #df =  df[df.index > last_date]
    #df.to_csv('csvs/{}.csv'.format(symbol),sep='\t',mode = 'a',header=False)
    df.to_csv('csvs/{}.csv'.format(symbol),sep='\t',mode = 'a',header=True)
#sys.exit(1)
#df['mediamovelsimples'] = Series((df['High']*2), index=df.index)
exit()
last_five = list()
#last_five = [1,1,1,1,1]
periods = 5
old_mme=None
for i, row in df.iterrows():
    print len(last_five)
    if (len(last_five) == periods):
        #last_five[9] = last_five[8]
        #last_five[8] = last_five[7]
        #last_five[7] = last_five[6]
        #last_five[6] = last_five[5]
        #last_five[5] = last_five[4]
        last_five[4] = last_five[3]
        last_five[3] = last_five[2]
        last_five[2] = last_five[1]
        last_five[1] = last_five[0]
        last_five[0] =  row['Close']
    elif (len(last_five) < periods):
        last_five.append(row['Close'])

    df.loc[i,'MMS'] = sum(last_five) / len(last_five)
    multiplier = (2/(periods+1))

    if old_mme is None:
        old_mme = float(row['Close'])
    df.loc[i,'MME'] = (float(row['Close'])-old_mme)*(float(multiplier)+old_mme)
    if (row['Close'] >= old_mme):
        old_close = row['Close']
        df.loc[i,'Status'] = 'UP'
    else:
        df.loc[i,'Status'] = 'DOWN'
    #df.loc[i,'MME'] = (float(row['Close']))
    #old_mme = df.loc[i,'MME']

#print(df.sort_values(4))

print (df)
