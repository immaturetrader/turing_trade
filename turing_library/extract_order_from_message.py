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
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime as dt
import datetime
import time
from time import gmtime, strftime
from datetime import datetime as dt_time
import copy
#print("current directory",os.getcwd())
new_dir = os.getcwd()
os.chdir(new_dir)
#print("new directory",os.getcwd())
from turing_library.firestore_client import fire_store
fs=fire_store()
from turing_library.alice_blue import AliceBlue, TransactionType, OrderType, ProductType, LiveFeedType, Instrument
from turing_library.alice_blue_execution import alice_blue_execution
chat_id=626127126
alice_admin=alice_blue_execution(fs,chat_id)

user_details=fs.fetch_user_creds(chat_id)
scrip_market_data = {}
alice=alice_admin.generate_client(username=user_details['client_id'].upper(), password=user_details['password'], twoFA=user_details['twoFA'],  api_secret=user_details['api_secret'],access_token=user_details['access_token'],app_id=user_details['app_id'],master_contracts_to_download=['NSE','NFO'])
from time import gmtime, strftime

def open_web_socket(alice):
  global socket_opened
  socket_opened = False
  alice.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      run_in_background=True)
  while(socket_opened==False):    # wait till socket open & then subscribe
        #print("# wait till socket open & then subscribe")
        pass
  print("Alice Blue web socket opened")


def event_handler_quote_update(message):
    #print(f"quote update {message}")
    global latest_ask_price
    global latest_bid_price
    global subscribed_scrip
    latest_ask_price=message['ask_prices'][0]
    subscribed_scrip=message['instrument'][2]
    latest_bid_price=message['bid_prices'][0]
    scrip_market_data[subscribed_scrip]={'ask':message['ask_prices'][0] , 'bid': message['bid_prices'][0]}
    print(subscribed_scrip,latest_ask_price,latest_bid_price)
    print(message)
    #print(message)
    #print(f"1 Best ask price of the scrip is {latest_ask_price}")
    #return latest_ask_price,latest_bid_price

def open_callback():
    global socket_opened
    socket_opened = True
    
open_web_socket(alice)

def unsubscribe_if_any(exchange,alice):
    print("unsubscribing if any")
    subs=alice.get_all_subscriptions()
    #subs.
    print(subs)
    sub_list=[]
    for sub in subs:
        sub_list.append(sub)
    for sub_i in sub_list:    
      alice.unsubscribe(sub,LiveFeedType.SNAPQUOTE)  
    symbols=[]
#    for sub in subs:
#      alice.unsubscribe(sub, LiveFeedType.SNAPQUOTE)  
    #if exchange == 'NSE':
    #alice.unsubscribe([alice.get_instrument_by_symbol('NSE', 'TATASTEEL'), alice.get_instrument_by_symbol('NSE', 'ACC')], LiveFeedType.MARKET_DATA)
#    while subs:
#      print("Existing subscriptions present")   
#      for sub in subs.keys():
#       symbols.append(sub.symbol)
#      for symbol in symbols: 
#       print(f"Unsubscribing from {symbol}")   
#       alice.unsubscribe(alice.get_instrument_by_symbol(exchange,symbol), LiveFeedType.SNAPQUOTE)
#     #else:
         
         

def check_the_price_for_cash_stock(alice,exchange,scrip):
 print(f"checking the market price for {scrip}")   
 unsubscribe_if_any(exchange,alice)
 global latest_ask_price
 global latest_bid_price
 global subscribed_scrip
 latest_ask_price=0
 latest_bid_price=0
 subscribed_scrip=scrip
 global socket_opened
 while(socket_opened==False):    # wait till socket open & then subscribe
        #print("# wait till socket open & then subscribe")
        pass
 print("Subscribing to the feed") 
 alice.subscribe(alice.get_instrument_by_symbol(exchange,scrip), LiveFeedType.SNAPQUOTE)
 #time.sleep(0.3)
 dt=datetime.datetime.now()
 if dt.hour > 9 and dt.hour < 16:
     time.sleep(0.1)
 else:
     time.sleep(0.1)
 return latest_ask_price,latest_bid_price
 
def check_the_price_for_fno(alice,exchange,scrip,expiry_date,is_fut,strike,is_CE):
 print(f"checking the market price for {scrip}")   
 unsubscribe_if_any(exchange,alice)
 global latest_ask_price
 global latest_bid_price
 global subscribed_scrip
 latest_ask_price=0
 latest_bid_price=0
 subscribed_scrip=scrip
 global socket_opened
 while(socket_opened==False):    # wait till socket open & then subscribe
        #print("# wait till socket open & then subscribe")
        pass
 print("Subscribing to the feed") 
 alice.subscribe(alice.get_instrument_for_fno(symbol = scrip, expiry_date=expiry_date, is_fut=is_fut, strike=strike, is_CE = is_CE), LiveFeedType.SNAPQUOTE)   
     
 print("Subscribed to the feed") 
 #time.sleep(0.3)
 dt=datetime.datetime.now()
 if dt.hour > 9 and dt.hour < 16:
     time.sleep(0.1)
 else:
     time.sleep(0.1)
 return latest_ask_price,latest_bid_price
 
 
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
    option_type = None
    price = 0.0
    sl = 0.0
    target = 0.0
    is_CE=None
    is_fut=None
    strike=0.0
    market_price=0.0
    expiry_date=[]
               
    order_duration = None
    time = None
    timezone = None

    m_id = 0
    m_timestamp=None
    message=None
    reply_m_id=0
    reply_to_message=None
    
    scan_name=None
    scan_url=None
    alert_name=None
    webhook_url=None
    
    timezone = time_zone=(strftime("%z", gmtime()))
    time = None
    cash_ask_price=0.0
    cash_bid_price=0.0
    
    nfo_ask_price=0.0
    nfo_bid_price=0.0
    
    def __init__(self,source):
        self.source = source
        if self.source == 'chartink':
            self.chartink_order= {
                "source": {"chartink" : {"scan_name":self.scan_name,"scan_url":self.scan_url,"alert_name":self.alert_name,"webhook_url":self.webhook_url,"m_timestamp":self.m_timestamp} },
                "order": { "segment":self.segment,"exchange":self.exchange,"scrip":self.scrip,"transaction_type":self.transaction_type,"order_type":self.order_type,"price":self.price,"sl":self.sl,"target":self.target },
                "order_duration" : self.order_duration ,
                "timestamp" :{"time":self.time,"timezone":self.timezone}
                }
            self.chartink_orders=[]

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
        
    def last_thursday_of_month(self,today):
        currDate, currMth, currYr = today, today.month, today.year
        for i in range(31):
            if currDate.month == currMth and currDate.year == currYr and currDate.weekday() == 3:
                #print('dt:'+ str(currDate))
                lastThuDate = currDate
            currDate += datetime.timedelta(1)
        return lastThuDate    
 
    def last_thursday_of_week(self,dt):
        print("checking for next thursday")   
        currDate, currMth, currYr = dt, dt.month, dt.year
        for i in range(7):
            if currDate.month == currMth and currDate.year == currYr and currDate.weekday() == 3:
                #print('dt:'+ str(currDate))
                lastThuDate = currDate
            currDate += datetime.timedelta(1)
        return lastThuDate 
    
    def find_CE_STRIKE(self,symbol):
     regex_expr="\d*\.?\d"
     strike=re.findall(regex_expr,symbol)
     return strike

    def check_for_option_for_fut(self,scrip,price):

     all_scripts = alice.search_instruments('NFO', scrip)

     STRIKE_DIFF=[]
     DESIRED_SYMBOL=[]
     dt = datetime.datetime.today()
     for ins in all_scripts:
         if ins.expiry.month==dt.month:
 
             if (str(ins.symbol)[-2:]=='CE'):
                
                 strike=self.find_CE_STRIKE(ins.symbol)
         
                 STRIKE_DIFF.append(abs(float(strike[0])-float(price)))
                 DESIRED_SYMBOL.append(ins)
                  
     min_strike_diff=min(STRIKE_DIFF)
     print("min:"+str(min_strike_diff))
     req_index=STRIKE_DIFF.index(min_strike_diff)
     print("req index:"+str(req_index))
     final_desired_symbol=DESIRED_SYMBOL[req_index]
     print("final symbol:"+str(final_desired_symbol))
     
     lowest_strike=self.find_CE_STRIKE(final_desired_symbol.symbol)
     print("symbol:"+str(final_desired_symbol.symbol))
     print("expiry:"+str(final_desired_symbol.expiry))
         
     self.strike=float(lowest_strike[0])
     self.is_CE=True
     #instrument = get_instrument_for_fno(self,symbol=final_desired_symbol.symbol, expiry_date=final_desired_symbol.expiry,is_CE = True, exchange = 'NFO')
     self.exchange='NFO'
     self.expiry_date = final_desired_symbol.expiry
     instrument=final_desired_symbol
     if self.expiry_date:
      self.nfo_bid_price,self.nfo_ask_price=check_the_price_for_fno(alice,self.exchange,scrip,self.expiry_date,False,self.strike,self.is_CE)
    def get_orders(self):
        pass
    
    def __dict__(self):
        #tm=dt_time.now()
        print("getting the order dict")
        print(f"getting order for {self.segment} and is_fut {self.is_fut}")
        self.time=dt_time.now().strftime("%Y-%m-%d %H:%M:%S"+self.time_zone)
        if self.source == 'telegram':
           order_eq={
                "source": {"telegram" : {"channel_type":self.channel_type,"channel":self.channel,"channel_id":self.channel_id,"m_id":self.m_id,"m_timestamp":self.m_timestamp,"message":self.message,"reply_m_id":self.reply_m_id,"reply_to_message":self.reply_to_message} },
                "order": { "segment":'EQ',"exchange":'NSE',"scrip":self.scrip,"transaction_type":self.transaction_type,"order_type":self.order_type,"price":self.price,"sl":self.sl,"target":self.target,"bid_price":self.cash_bid_price,"ask_price":self.cash_ask_price,"trade_closed":"N"},
                "order_duration" : self.order_duration ,
                "timestamp" :{"time":self.time,"timezone":self.timezone}
                }
           
           print("order_eq",order_eq)
           if self.segment=='EQ' and not self.is_fut:
                return [order_eq]
           elif self.exchange == 'NFO' and not self.is_fut:
                print(f"getting order for {self.segment} and is_fut {self.is_fut}")
                order_opt={
                "source": {"telegram" : {"channel_type":self.channel_type,"channel":self.channel,"channel_id":self.channel_id,"m_id":self.m_id,"m_timestamp":self.m_timestamp,"message":self.message,"reply_m_id":self.reply_m_id,"reply_to_message":self.reply_to_message} },
                "order": { "segment":'OPT',"exchange":self.exchange,"scrip":self.scrip,"transaction_type":self.transaction_type,"order_type":self.order_type,"price":self.price,"sl":self.sl,"target":self.target,"is_fut":self.is_fut,"strike":self.strike,"expiry_date":[self.expiry_date.year,self.expiry_date.month,self.expiry_date.day ],"is_CE":self.is_CE,"bid_price":self.nfo_bid_price,"ask_price":self.nfo_ask_price,"trade_closed":"N"},
                "order_duration" : self.order_duration ,
                "timestamp" :{"time":self.time,"timezone":self.timezone}
                }
                return [order_opt]
           elif self.exchange == 'NFO' and self.is_fut:    
                self.is_fut=False
                print(f"getting order for {self.segment} and is_fut {self.is_fut}")
                order_opt={
                "source": {"telegram" : {"channel_type":self.channel_type,"channel":self.channel,"channel_id":self.channel_id,"m_id":self.m_id,"m_timestamp":self.m_timestamp,"message":self.message,"reply_m_id":self.reply_m_id,"reply_to_message":self.reply_to_message} },
                "order": { "segment":'OPT',"exchange":self.exchange,"scrip":self.scrip,"transaction_type":self.transaction_type,"order_type":self.order_type,"price":self.price,"sl":self.sl,"target":self.target,"is_fut":self.is_fut,"strike":self.strike,"expiry_date":[self.expiry_date.year,self.expiry_date.month,self.expiry_date.day ],"is_CE":self.is_CE,"bid_price":self.nfo_bid_price,"ask_price":self.nfo_ask_price,"trade_closed":"N"},
                "order_duration" : self.order_duration ,
                "timestamp" :{"time":self.time,"timezone":self.timezone}
                }
                return [order_eq,order_opt]
           else:
                return[{
                "source": {"telegram" : {"channel_type":self.channel_type,"channel":self.channel,"channel_id":self.channel_id,"m_id":self.m_id,"m_timestamp":self.m_timestamp,"message":self.message,"reply_m_id":self.reply_m_id,"reply_to_message":self.reply_to_message} },
                "order": { "segment":self.segment,"exchange":self.exchange,"scrip":self.scrip,"transaction_type":self.transaction_type,"order_type":self.order_type,"price":self.price,"sl":self.sl,"target":self.target,"bid_price":self.bid_price,"ask_price":self.ask_price,"trade_closed":"N" },
                "order_duration" : self.order_duration ,
                "timestamp" :{"time":self.time,"timezone":self.timezone}
                }]
                    
               

        elif self.source == 'chartink':
           self.source = 'chartink'
           return   
       
        else:
            return 
           
    def check_for_chartink_alert(self,alert):
        num_of_orders=0
        #orders=[]
        #today=dt.datetime.now()
        
        scrips=alert['stocks'].split(',')
        trigger_prices = alert["trigger_prices"].split(',')
        trigger_time_s=alert['triggered_at']
        
        self.chartink_order['source']['chartink']['scan_name']=alert['scan_name']
        self.chartink_order['source']['chartink']['scan_url']=alert['scan_url']
        self.chartink_order['source']['chartink']['alert_name']=alert['alert_name']
        self.chartink_order['source']['chartink']['webhook_url']=alert['webhook_url']
        self.chartink_order['source']['chartink']['m_timestamp']=self.transform_time_string(trigger_time_s)
        
        self.chartink_order['order']['exchange']='NSE'
        scan_data=fs.get_chartink_alert_data(alert['scan_name'])
        if scan_data :
            self.chartink_order['order']['order_type']=scan_data['order_type']
        
        
        
        while num_of_orders<len(scrips):
               
               order=copy.deepcopy(self.chartink_order)
               #orders.append([scrips[num_of_orders],float(trigger_prices[num_of_orders])])
               order['order']['scrip']=scrips[num_of_orders]
               order['order']['price']=float(trigger_prices[num_of_orders])
               order['order']['sl']=round(order['order']['price']*0.99,1)
               order['order']['transaction_type']='MKT'               
               num_of_orders=num_of_orders+1
               self.chartink_orders.append(order)

            
        
        trigger_time_s=trigger_time_s.replace(' ','')
        print(trigger_time_s)


    def transform_time_string(self,trigger_time_s):
        today=dt.datetime.now()
        trigger_time_s=trigger_time_s.replace(' ','')
        if 'am' in trigger_time_s:
            trigger_time_s=trigger_time_s.replace('am','')
            trigger_time=str(trigger_time_s).split(':')
            trigger_hours=int(trigger_time[0])
        else:
            trigger_time_s=trigger_time_s.replace('pm','')
            trigger_time=str(trigger_time_s).split(':')
            trigger_hours=int(trigger_time[0]) + 12
        trigger_minutes=int(trigger_time[1])
        trigger_time=dt.datetime(today.year, today.month, today.day, trigger_hours, trigger_minutes, 0, 0)
        print("Trigger time",trigger_time)
        time_zone=(strftime("%z", gmtime()))
        time_zone_values = re.findall("(\d.)",time_zone)
        hours_added = dt.timedelta(hours = (int(time_zone_values[0]) + int(time_zone_values[1])/60))
        if time_zone=='+0530':
           hours_added = 0
           trigger_time_adjusted = trigger_time
           return trigger_time_adjusted
        else:
           #hours_added=-hours_added 
           trigger_time_adjusted = trigger_time - hours_added  
           return trigger_time_adjusted
        
    def check_for_option_order(self,regex_expr):
        params=re.findall(regex_expr,self.message)
        print("checking for option orders")
        print(params)
        if params:
               self.exchange='NFO'
               self.segment = 'OPT'
               self.is_fut=False
               self.order_type=params[0][0]
               self.transaction_type=params[0][1]
               self.scrip='BANKNIFTY'
               self.strike=float(params[0][3])
               is_CE=None
               if params[0][4] == 'CALL':
                  is_CE=True
               elif params[0][4] == 'PUT':
                  is_CE=False
                  
               self.is_CE = is_CE
               self.sl=float(params[0][6])
               self.order_found=True
               print("Order Found",self.order_found)
               print("Checking for expiry date")
               today=dt.date.today()
               print(today)
               self.expiry_date=self.last_thursday_of_week(today)
               print("expiry date successfully retrieved")
               print("Order Found",self.order_found)
               self.nfo_ask_price,self.nfo_bid_price=check_the_price_for_fno(alice,self.exchange,self.scrip,self.expiry_date,self.is_fut,self.strike,self.is_CE)
               #scrip,price,sl,qty,,is_fut,strike,is_CE
               
    def check_for_order(self,regex_expr):
        params=re.findall(regex_expr,self.message)
              #print(params)
        if params:

               self.exchange='NSE'
               self.segment = 'EQ'
               self.order_type=params[0][0]
               self.transaction_type=params[0][1]
               self.scrip=params[0][2]
               self.price=float(params[0][3])
               self.sl=float(params[0][4])


               if 'FUTURE' in self.order_type:
                   #self.segment = 'FUT'
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
                  self.cash_ask_price,self.cash_bid_price=check_the_price_for_cash_stock(alice,self.exchange,self.scrip)
               else:
                  self.order_found=False

    def extract_intents(self):
        if self.message:
           if self.channel in ['rajdattani','at_test_incoming_0901']:
              if not self.order_found:
               self.check_for_order("(.+) (BUY|SELL) ([A-Z]+ ?[A-Z]+ ?[A-Z]+ ?) @(\d*\.?\d*)-?\d*.?\d* SL (\d*\.?\d*)")
#               self.transaction_type = 'BUY'
#              if not self.order_found:
#               self.check_for_order("(.+)SELL ([A-Z]+ ?[A-Z]+ ?[A-Z]+ ?) @(\d*\.?\d*)-?\d*.?\d* SL (\d*\.?\d*)")
#               self.transaction_type = 'SELL'
                 
           elif self.channel in ['PATELWEALTH','test26021994']:
               
                if not self.order_found:
                    print("checking for buy order")
                    self.extract_from_patel_wealth("(.+) (BUY|SELL) (.+) @ ?(\d*\.?\d*)-?\d*.?\d* ?S*?L (\d*\.?\d*)")
#                    self.transaction_type = 'BUY'
#                print("order_found",self.order_found)
#                if not self.order_found:
#                    print("checking for sell order")
#                    self.extract_from_patel_wealth("(.+)SELL (.+) @ ?(\d*\.?\d*)-?\d*.?\d* ?S*?L (\d*\.?\d*)")
#                    self.transaction_type = 'SELL'
#                    print("Sell order found",self.order_found)
                if not self.order_found:  # check for bank nifty trade
                    print("checking for bank nifty option order")
                    self.check_for_option_order("(.+) (BUY|SELL) (BANK NIFTY) (\d*) (.+) @ ?(\d*\.?\d*)-?\d*.?\d* ?S*?L (\d*\.?\d*)")
                    #self.transaction_type = 'BUY' 
                    print(self.__dict__())

        else:
            print("No message found")

    def extract_from_patel_wealth(self,regex_exp):
              params=re.findall(regex_exp,self.message)
              print(params)
              print("order_found",self.order_found)
              if params:
                #print("order_found",self.order_found)
                self.exchange='NSE'
                self.segment = 'EQ'
                self.order_type=params[0][0]
                self.transaction_type = params[0][1]
                self.scrip=params[0][2]
                if 'FUT' in self.scrip:
                   self.is_fut=True
                self.scrip=self.scrip.replace('ON NSE CASH','').replace('FUT','').replace('CASH','').replace('/','').strip()
                if self.scrip:
                 nse_scrip,nse_scrip_name=self.check_for_the_scrip(self.scrip)
                self.price=float(params[0][3])
                self.sl=float(params[0][4])
                if nse_scrip:
                 self.scrip=nse_scrip
                 self.order_found=True
                 self.cash_ask_price,self.cash_bid_price=check_the_price_for_cash_stock(alice,self.exchange,self.scrip)
                 print("order_found",self.order_found)
                 if self.is_fut:
                    self.check_for_option_for_fut(self.scrip,self.price) 
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
          #print(matched_1)
          return matched_1['scrip'].item(),matched_1['scrip_name'].item()

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
     
        
    def check_for_the_scrip_new(self,string):
       scrip_list=pd.read_csv("scrip_list_nse.csv")
       string=string.strip()
       print("searching for the scrip",string)
       scrip_lower = scrip_list['scrip'].str.lower()
       scrip_lower = scrip_lower.str.replace(" ","")
       matched_1 = scrip_list.loc[(scrip_list['scrip']  == string)]
       
       
       matched=False
       #matched_record = matched.to_dict('records')
       if len(matched_1)==1:
          matched=True
          #print(matched_1)
          return matched_1['scrip'].item(),matched_1['scrip_name'].item()
       matched_2 = scrip_list.loc[(scrip_list['scrip'].str.lower() == string.lower().replace(" ",""))]
       if len(matched_2)==1 and not matched:
          matched=True
          return str(matched_2['scrip'].item()),str(matched_2['scrip_name'].item())
       matched_3 = scrip_list.loc[(scrip_list['scrip_name'].str.contains(string,case=False))]
       if len(matched_3)==1 and not matched:
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
