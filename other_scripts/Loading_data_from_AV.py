# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 14:46:15 2020

@author: sravula
"""
import pandas as pd
import sys
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange

ts = TimeSeries(key='3U3JP65KDYURVEA6',output_format='pandas')

#data, meta_data = ts.get_intraday(symbol='BSE:YESBANK',interval='1min', outputsize='full')
#data, meta_data = ts.get_daily_adjusted('BSE:YESBANK')
#
#print(type(data))
#df=data
#print(df.index)
write_rows=pd.DataFrame(['open','high','low','close','adjusted_close','volume','divident_amount','split_coefficient'])
stock_list = pd.read_csv('D:/Personal/Stocks/Data/Stock_List_innd.csv')
#print(stock_list.head())

#for index,row in stock_list.iterrows():
#    symbol_value= row['exchange'] + ":" + row['scrip_code']
#    print(index,symbol_value)
#    try:
#        data, meta_data = ts.get_daily_adjusted(symbol_value)
#        print(data)
#        for d_intex,datum in data.iterrows():
#            print(d_intex,datum)
#            #write_rows.iloc[index+d_intex]=datum['open'],datum['high'],datum['low'],datum['close'],datum['adjusted_close'],datum['volume'],datum['divident_amount'],datum['split_coefficient']
#    except:
#        print(sys.exc_info()[0], " occurred")
#    print(type(data))

#write_rows.to_csv('stock_historical_eod.csv',index=False)



#Forex

forex = ForeignExchange(key='3U3JP65KDYURVEA6',output_format='pandas')
data, meta_data = forex.get_currency_exchange_daily(from_symbol='USD',to_symbol='INR')
print(data)
data.to_csv("usd_exchange_rate.csv")