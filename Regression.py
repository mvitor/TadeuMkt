import math 
import numpy as np
import pandas as pd
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib import style
import datetime
# Load datafream
symbol =  "ITUB4"
#df = pd.read_csv("assets/VALE3.csv",sep='\t', index_col="Date",parse_dates=True,usecols=['Date','Close'],na_values=['nan'])
df = pd.read_csv("assets/ITUB4.csv",sep='\t',index_col="Date",parse_dates=True,usecols=['Date','Close'],na_values=['nan'])
#df = pd.read_csv("assets/BBAS3.csv",sep='\t', index_col="Date",parse_dates=True,usecols=['Date','Close'],na_values=['nan'])
#df = pd.read_csv("assets/MRVE3.csv",sep='\t', index_col="Date",parse_dates=True,usecols=['Date','Close'],na_values=['nan'])
# select the float columns
if symbol == 'ITUB4a':
    print (df.iloc[100])
    df = df.drop(df.index[100])
    print (df.iloc[100])
#df['Date'] = pd.to_datetime(df['Date'])
df_orig  = df.tail()
print (df.head())
#df = df.set_index('Date')
#df_num = df.select_dtypes(include=[np.float])
# select non-numeric columns
#df_num = df.select_dtypes(exclude=[np.number])
print (df.tail())
forecast_col = 'Close'
last_date = df.index[-1]
last_price = df.iloc[-1].Close
last_price = float(last_price)
#last_price = 100
forecast_out = int(math.ceil(0.02 * len(df)))

df.fillna(value=-99999, inplace=True)
df['label'] = df[forecast_col].shift(-forecast_out)

X = np.array(df.drop(['label'], 1))
X = preprocessing.scale(X)
X_lately = X[-forecast_out:]
X = X[:-forecast_out]

print (df.tail())
df.dropna(inplace=True)

y = np.array(df['label'])

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)
clf = LinearRegression(n_jobs=-1)
clf.fit(X_train, y_train)
confidence = clf.score(X_test, y_test)
print (confidence)
forecast_set = clf.predict(X_lately)
df['Forecast'] = np.nan

print(last_price,last_date,forecast_set, confidence, forecast_out)
last_date = df.iloc[-1].name
print(last_price,last_date,forecast_set, confidence, forecast_out)
last_unix = last_date.timestamp()
print(last_price,last_unix,last_date,forecast_set, confidence, forecast_out)
one_day = 86400
#one_day = 106400
next_unix = last_unix + one_day
next_date = datetime.datetime.fromtimestamp(next_unix)
print (df.tail())
for i in (forecast_set):
    next_unix += 86400
    next_date = datetime.datetime.fromtimestamp(next_unix)
    df.loc[next_date] = [np.nan for _ in range(len(df.columns)-1)]+[i]
    if (df.loc[next_date].Forecast > last_price):
        print ( "maior: ")
        last_price = df.loc[next_date].Forecast
        print (last_price,next_date)
print (df.tail())
print (df_orig.tail())
df['Close'].plot()
df['Forecast'].plot()
plt.legend(loc=4)
plt.xlabel('Date')
plt.ylabel('Price')
#plt.show()
