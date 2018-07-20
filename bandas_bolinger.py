"""Plot High prices for IBM"""
import os
import pandas as pd
import matplotlib.pyplot as plt

def test_run():
    # Data Ranges
    start_date = '2017-12-01'
    end_date = '2018-06-05'
    dates = pd.date_range(start_date,end_date)
    symbols = ['ITUB4','BBAS3','GOAU4','MRVE3','BBDC4','PETR4','CCRO3','VAlE3','ABEV3']
    #symbols = ['ABEV3']
    df = get_data(symbols,dates)
    df = df.dropna(how='all')
    #df = get_symbol_data('BBAS3',df)
    symbol = 'ABEV3'
    rm_symbol = get_rolling_mean(df[symbol],window=20)
    rstd_symbol = get_rolling_std(df[symbol],window=20)
    upper_band, lower_band = get_bollinger_bands(rm_symbol,rstd_symbol)
    ax = df[symbol].plot(title='Bandas de Bollinger',label=symbol)
    rm_symbol.plot(label='Rolling mean',ax=ax)
    upper_band.plot(label='Upper band',ax=ax)
    lower_band.plot(label='Lower band',ax=ax)
    # Add axis labels and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='upper left')
    plt.show()

    #df = calculate_mean(symbols,df)

    #plot_media(symbols,df)
    #plot_data(df,symbols)
    #plot_data(df,'BBAS3')
    #plot_selected(df,symbols,'2018-05-01','2018-05-21')
def plot_selected (df,columns,start_index,end_index):
    plot_data(df.ix[start_index:end_index,columns],columns,title="Select Data")

def normalize_data (df):
    return df/df.ix[0,:]

def plot_data (df,symbols,title="Stock prices"):
    #symbols
    ax = df[symbols].plot(title=title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    #df[symbols].plot()
    plt.show()  # must be called to show plots

def get_data(symbols,dates):
    df = pd.DataFrame(index=dates)
    if 'ITUB4' not in symbols:
        symbols.insert(0,'ITUB4')
    for symbol in symbols:
        print symbol
        df_temp = pd.read_csv("csvs/{}.csv".format(symbol),sep='\t', index_col="Date",parse_dates=True,usecols=['Date','Close'],na_values=['nan'])
        df_temp = df_temp.rename(columns={'Close':symbol})
        print df_temp.tail()
        df = df.join(df_temp)
    return df

def get_symbol_data (symbol,df):
    df =  df.ix[:, [symbol]]
    return df
def get_rolling_mean (values,window):
    return pd.rolling_mean(values,window=window)
def get_rolling_std(values,window):
    return pd.rolling_std(values,window=window)
def get_bollinger_bands(rm,rstd):
    upper_band = rm + rstd * 2
    lower_band = rm - rstd * 2
    return upper_band, lower_band
def symbol_to_path (symbol, base_dir="csvs"):
    return os.path.join(base_dir,"{}.csv".format(str(symbol)))
def calculate_mean (symbols,df):
    # calculate mean
    for symbol in symbols:
        last_five = list()
        # last_five = [1,1,1,1,1]
        periods = 5
        old_mme = None
        for i, row in df.iterrows():
            #print len(last_five)
            if (len(last_five) == periods):
                # last_five[9] = last_five[8]
                # last_five[8] = last_five[7]
                # last_five[7] = last_five[6]
                # last_five[6] = last_five[5]
                # last_five[5] = last_five[4]
                last_five[4] = last_five[3]
                last_five[3] = last_five[2]
                last_five[2] = last_five[1]
                last_five[1] = last_five[0]
                last_five[0] = row[symbol]
            elif (len(last_five) < periods):
                last_five.append(row[symbol])

            df.loc[i, 'MMS{}'.format(symbol)] = sum(last_five) / len(last_five)
            multiplier = (2 / (periods + 1))
            #if old_mme is None:
            #df.loc[i, 'MME{}'.format(symbol)] = (float(row[symbol]) - old_mme) * (float(multiplier) + old_mme)
            if (row[symbol] >= old_mme):
                old_close = row[symbol]
                df.loc[i, 'Status{}'.format(symbol)] = 'UP'
            else:
                df.loc[i, 'Status{}'.format(symbol)] = 'DOWN'
            old_mme = float(row[symbol])
    return df

if __name__ == "__main__":
    test_run()
