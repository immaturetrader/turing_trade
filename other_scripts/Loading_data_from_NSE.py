# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 18:39:37 2019

@author: sravula
"""

import nsetools
from pprint import pprint
from nsetools import Nse
import bsedata
import pandas as pd
nse = Nse()
from nsepy import get_history
from datetime import date
from nsepy.derivatives import get_expiry_date
import time
#q = nse.get_quote('infy')
#pprint(q['lastPrice'])

def get_nse_stocks():
 all_scrips = nse.get_stock_codes()
 #print(all_scrips)
 scrip_df=pd.DataFrame(columns=['scrip','scrip_name'])
 write_index=0
 for scrip in all_scrips:
    #print(scrip)
    #print(all_scrips[scrip])
    if scrip!='SYMBOL':
     scrip_df.loc[write_index]=scrip,all_scrips[scrip]
     write_index+=1
#print(len(all_stock_codes))
 scrip_df.to_csv("scrip_list_nse.csv",sep=",",index=False)

#vix = get_history(symbol="INDIAVIX",
#            start=date(2000,1,1),
#            end=date(2020,6,1),
#            index=True)
#print(vix)

def get_index_data():
 NIFTY_50 = get_history(symbol="NIFTY 50",
            start=date(2000,1,1),
            end=date(2020,6,1),
            index=True)
 NIFTY_50.to_csv("NIFTY_50.csv",sep=",")
 time.sleep(5)
 
def get_option_chain_data(): 
 expiry_date = get_expiry_date(year=2017, month=5, index=True, stock=False)
 year = 2020
 month = 1
 option_types = ['CE','PE']
 nifty_option_chain=pd.DataFrame(columns=['Date','Symbol','Expiry','Option Type','Strike Price','Open','High','Low','Close','Last','Settle Price','Number of Contracts','Turnover','Premium Turnover','Open Interest','Change in OI','Underlying'])
 while month<=6:
  expiry_dates = get_expiry_date(year=year, month=month, index=True, stock=False)  
  print(f"Expiry Dates {expiry_dates}")
  NIFTY = get_history(symbol="NIFTY 50",start=date(2020,month,1),end=date(2020,month,1),index=True)
  NIFTY_CLOSING = NIFTY['Close'].values[0]
  print(f"nifty closing {NIFTY_CLOSING}")
  iter_nifty = int(round(NIFTY_CLOSING*0.8,-2))
  for option_type in option_types:
   for expiry_date in expiry_dates:
    iter_nifty = int(round(NIFTY_CLOSING*0.8,-2))   
    while iter_nifty <= NIFTY_CLOSING *1.2:
     print(f"Getting option chain data for {iter_nifty} option type {option_type} and expiry {expiry_date} ")   
     nifty_opt = get_history(symbol="NIFTY",
                         start=date(2020,month,1),
                         end=date(2020,month+3,1),
                         index=True,
                         option_type=option_type,
                         strike_price=iter_nifty,
                         expiry_date=expiry_date)
     if len(nifty_opt)>0:
      nifty_option_chain=nifty_option_chain.append(nifty_opt)
      print("Option data found for the nifty expiry",nifty_opt['Expiry'])
      time.sleep(1)
     iter_nifty=iter_nifty+100 
  month+=1 
 nifty_option_chain.to_csv("nifty_option_chain.csv",sep=",")
 
if __name__ == '__main__':
   #get_index_data() 
   get_option_chain_data()