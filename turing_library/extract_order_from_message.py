# -*- coding: utf-8 -*-
"""
Created on Fri May 30 23:25:54 2020

@author: sravula
"""

import pandas as pd
import re
import regex
import os
import json
global scrip_list
import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#print("current directory",os.getcwd())
new_dir = os.getcwd()
os.chdir(new_dir)
#print("new directory",os.getcwd())

class order_details():
    print("Initialized order details")
    order_found=False
    channel_type = None
    channel = None
    channel_id = None
    segment = None
    exchange = None
    scrip = None
    scrip_name = None
    transaction_type = None
    order_type = None
    price = 0.0
    sl = 0.0
    target = 0.0
    order_duration = None
    time = None
    timezone = None

    m_id = 0
    m_timestamp=None
    message=None
    reply_m_id=0
    reply_to_message=None

    def __init__(self,source):
        self.source = source

    def clean_message(self):
        self.message = ' ' + str(self.message)
        self.message=str(self.message).replace('\n',' ')
        self.message=self.message.replace('  ',' ')
        self.message=str(self.message).upper()
        self.message=self.message.replace('SL OF','SL')
        self.message=self.message.replace('BTST','BTST BUY')
        self.message=self.message.replace('BUY BUY','BUY')

        self.reply_to_message=str(self.reply_to_message).replace('\n',' ')
        self.reply_to_message=self.reply_to_message.replace('  ',' ')
        self.reply_to_message=str(self.reply_to_message).upper()

    def __dict__(self):
        if self.source == 'telegram':
           return   {
                "source": {"telegram" : {"channel_type":self.channel_type,"channel":self.channel,"channel_id":self.channel_id,"m_id":self.m_id,"m_timestamp":self.m_timestamp,"message":self.message,"reply_m_id":self.reply_m_id,"reply_to_message":self.reply_to_message} },
                "order": { "segment":self.segment,"exchange":self.exchange,"scrip":self.scrip,"transaction_type":self.transaction_type,"order_type":self.order_type,"price":self.price,"sl":self.sl,"target":self.target },
                "order_duration" : self.order_duration ,
                "timestamp" :{"time":self.time,"timezone":self.timezone}
                }

        elif self.source == 'chartink':
           self.source = 'chartink'
           return {"source": "chartink"}

    def check_for_order(self,regex_expr):
        params=re.findall(regex_expr,self.message)
              #print(params)
        if params:

               self.exchange='NSE'
               self.order_type=params[0][0]
               self.scrip=params[0][1]
               self.price=float(params[0][2])
               self.sl=float(params[0][3])


               if 'FUTURE' in self.order_type:
                   self.segment = 'FUT'
                   print(self.scrip)
                   self.scrip=self.scrip.replace('FUT','')
                   self.scrip=self.scrip.replace('FUTURES','')
                   #self.scrip=self.scrip.replace('  ','')
               if 'BTST' in self.order_type:
                   self.order_duration='BTST'
               elif 'STBT' in self.order_type:
                   self.order_duration='STBT'
               elif 'INTRADAY' in self.order_type:
                   self.order_duration='INTRADAY'
               else:
                   self.order_duration='POSITIONAL'

               nse_scrip_code,nse_scrip_name=self.check_for_the_scrip(self.scrip)
               if nse_scrip_code:
                  self.scrip= nse_scrip_code
                  self.scrip_name=nse_scrip_name
                  self.order_found=True
               else:
                  self.order_found=False

    def extract_intents(self):
        if self.message:
           if self.channel in ['rajdattani','at_test_incoming_0901']:
              if not self.order_found:
               self.check_for_order("(.+)BUY ([A-Z]+ ?[A-Z]+ ?[A-Z]+ ?) @(\d*\.?\d*)-?\d*.?\d* SL (\d*\.?\d*)")
               self.transaction_type = 'BUY'
              elif not self.order_found:
               self.check_for_order("(.+)SELL ([A-Z]+ ?[A-Z]+ ?[A-Z]+ ?) @(\d*\.?\d*)-?\d*.?\d* SL (\d*\.?\d*)")
               self.transaction_type = 'SELL'
           elif self.channel in ['PATELWEALTH','test26021994']:
                print("checking for buy order")
                self.extract_from_patel_wealth("(.+)BUY (.+) @ (\d*\.?\d*)-?\d*.?\d* ?S*?L (\d*\.?\d*)")
                self.transaction_type = 'BUY'
                print("order_found",self.order_found)
                if not self.order_found:
                    print("checking for sell order")
                    self.extract_from_patel_wealth("(.+)SELL (.+) @ (\d*\.?\d*)-?\d*.?\d* ?S*?L (\d*\.?\d*)")
                    self.transaction_type = 'SELL'

        else:
            print("No message found")

    def extract_from_patel_wealth(self,regex_exp):
              params=re.findall(regex_exp,self.message)
              print(params)
              print("order_found",self.order_found)
              if params:
                #print("order_found",self.order_found)
                self.exchange='NSE'
                self.order_type=params[0][0]
                self.scrip=params[0][1]
                self.scrip=self.scrip.replace('ON NSE CASH','').replace('FUT','').replace('CASH','').replace('/','').strip()
                if self.scrip:
                 nse_scrip,nse_scrip_name=self.check_for_the_scrip(self.scrip)
                self.price=float(params[0][2])
                self.sl=float(params[0][3])
                if nse_scrip:
                 self.scrip=nse_scrip
                 self.order_found=True
                 print("order_found",self.order_found)
                else:
                 self.order_found=False
              else:
                 self.order_found=False



    def check_for_the_scrip(self,string):
       scrip_list=pd.read_csv("scrip_list_nse.csv")
       string=string.strip()
       print("searching for the scrip",string)
       scrip_lower = scrip_list['scrip'].str.lower()
       scrip_lower = scrip_lower.str.replace(" ","")
       matched_1 = scrip_list.loc[(scrip_list['scrip']  == string)]
       matched_2 = scrip_list.loc[(scrip_list['scrip'].str.lower() == string.lower().replace(" ",""))]
       matched_3 = scrip_list.loc[(scrip_list['scrip_name'].str.contains(string,case=False))]
       matched=False
       #matched_record = matched.to_dict('records')
       if len(matched_1)==1:
          matched=True
          return str(matched_1['scrip'].item()),str(matched_1['scrip_name'].item())

       elif len(matched_2)==1 and not matched:
          matched=True
          return str(matched_2['scrip'].item()),str(matched_2['scrip_name'].item())
       elif len(matched_3)==1 and not matched:
          matched=True
          return str(matched_3['scrip'].item()),str(matched_3['scrip_name'].item())
        #Fuzzy Search
       if not matched:
         print(f"Fuzzy searching the scrip {string}")
         for i,row in scrip_list.iterrows():
          scrip_name = row['scrip_name']
          #print("'({})e<=1', '{}'".format(scrip_name,string))
          ratio=fuzz.partial_ratio(string.lower(),scrip_name.lower().replace(" limited",""))
          #print("Found an approx match",string,scrip_name,ratio)
          if ratio > 82:
             print("Found an approx match",string,scrip_name,ratio)
             return row['scrip'],scrip_name
             break
         return '',''




def fuzz_search(scrip):
   for i,row in scrip_list.iterrows():
     scrip_name = row['scrip_name']
     ratio=fuzz.partial_ratio(scrip.lower(),scrip_name.lower().replace(" limited",""))
     if ratio > 80:
        print(scrip,scrip_name,ratio)


if __name__ == '__main__1':
    messages=pd.read_csv("rajdattani_history.csv")
    orders=pd.DataFrame(columns=['message','order_type','scrip','price','sl','order_found'])
    for i,row in messages.iterrows():
        #print(row)
        order = order_details('telegram')
        order.channel='rajdattani'
        order.channel_type='public'
        order.message=row['message']
        order.clean_message()
        order.extract_intents()
        orders.loc[i]=order.message,order.order_type,order.scrip,order.price,order.sl,order.order_found
        if order.scrip:
         print(order.__dict__())
         #orders.append(order.__dict__())



    #df=pd.DataFrame(orders)
    #print(len(df))
    print(len(orders))
    orders.to_csv("generated_orders.csv",index=False)
