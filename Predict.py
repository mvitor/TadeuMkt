#!/usr/local/bin/python3

import quandl, math
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble.forest import RandomForestClassifier


df = quandl.get("WIKI/GOOGL")
#df = quandl.get("GOOG/BVMF_PETR4.4")
#petr4 = Quandl.get("GOOG/BVMF_PETR4", authtoken="
df = df[['Adj. Open',  'Adj. High',  'Adj. Low',  'Adj. Close', 'Adj. Volume']]
df['HL_PCT'] = (df['Adj. High'] - df['Adj. Low']) / df['Adj. Close'] * 100.0
df['PCT_change'] = (df['Adj. Close'] - df['Adj. Open']) / df['Adj. Open'] * 100.0
print (df.head())
print (df.tail())
print (len(df))
df = df[['Adj. Close', 'HL_PCT', 'PCT_change', 'Adj. Volume']]
forecast_col = 'Adj. Close'
df.fillna(value=-99999, inplace=True)
forecast_out = int(math.ceil(0.01 * len(df)))
df['label'] = df[forecast_col].shift(-forecast_out)

X = np.array(df.drop(['label'], 1))
X = preprocessing.scale(X)
X = X[:-forecast_out]
df.dropna(inplace=True)
y = np.array(df['label'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
clf = LinearRegression(n_jobs=-1)
clf.fit(X_train, y_train)
confidence = clf.score(X_test, y_test)
print(confidence)
print (X_train[1])
print (y_train[1])
exit()

rf=RandomForestClassifier(max_depth=8,n_estimators=5)
rf_cv_score=cross_val_score(estimator=rf,X=X_train,y=y_train,cv=5)
print(rf_cv_score)



