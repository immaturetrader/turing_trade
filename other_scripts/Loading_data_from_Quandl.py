# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 18:39:37 2019

@author: sravula
"""

import quandl as quandl
import csv
import pandas as pd

quandl.ApiConfig.api_key = "c4bDbeX2BmtrPMidDoEb"
scrips=pd.read_csv("scrip_list.csv")
#scrip_historical_data=pd.DataFrame(columns=['Date','Open','High','Low','Last','Close','Total Trade Quantity','Turnover (Lacs)'])


scrip_historical_data=quandl.get('NSE/3MINDIA')
#print(scrip_historical_data)
for i,row in scrips.iterrows():
    scrip=row['Exchange']+"/"+row['Scrip']
    print("Collecting data for ",scrip)
    try: 
     data = quandl.get(scrip)
     data['Exchange']=row['Exchange']
     data['Scrip']=row['Scrip']
     scrip_historical_data=scrip_historical_data.append(data)
     #scrip_historical_data.to_csv("scrip_historical_data.csv",sep=",")
     scrips.loc[i,'Data Received']='Y'
     #scrips.to_csv("scrip_list_data_processed.csv",index=False) 
    except (RuntimeError,NameError):
     print("Could not find data for the scrip",scrip)
     scrip_historical_data.to_csv("scrip_historical_data.csv",sep=",")
     scrips.loc[i,'Data Received']='N'
     scrips.to_csv("scrip_list_data_processed.csv",index=False)

scrip_historical_data.to_csv("scrip_historical_data.csv",sep=",")     
scrips.to_csv("scrip_list_data_processed.csv",index=False)