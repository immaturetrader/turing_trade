# -*- coding: utf-8 -*-
"""
Created on Fri May 29 23:25:54 2020

@author: sravula
"""

#Install protlib,websocket_client,requests,bs4


import json
import time
import datetime
import os
from turing_library.big_query_client import big_query
from turing_library.firestore_client import fire_store
from turing_library.alice_blue_execution import alice_blue_execution
from turing_library.angel_broking_execution import angel_broking_execution

#import big_query_client
import pickle
from smartapi import SmartConnect
obj=SmartConnect(api_key="X4iDD8xI")
username='R381604'
pwd='497666124153$Ai'
data = obj.generateSession(username,pwd)


new_dir = os.getcwd()
os.chdir(new_dir)

class broker_execution():

 def __init__(self,fs,chat_id):
     self.chat_id = chat_id
     self.bq = big_query(chat_id)
     self.broker_creds=self.get_creds_for_broker()
     self.broker_object = self.generate_client()
     self.fs = fs
     
     
 def get_creds_for_broker(self):    
     self.broker_creds=self.fs.fetch_user_creds(self.chat_id)
     return self.broker_creds

 def generate_client(self):
  self.get_creds_for_broker()   
  try:
   if self.broker_creds['broker']=='angelbroking':   
    print("generating the client with existing token")    
    obj=SmartConnect(api_key=self.broker_creds['api_key'])    
    self.session = obj.generateSession(self.broker_creds['client_id'],self.broker_creds['password'])
    self.broker_object = obj
    return self.broker_object
  except:
   print("Unable to login using the current credentials,Please check")
   return self.broker_object

 def get_positions(self,alice):
    poss=alice.get_daywise_positions()['data']['positions']
    p=0
    p_l=0
    message=''
    message_l=''
    for pos in poss:
     p=round(float(pos['unrealised_pnl'])+float(pos['realised_pnl']),2)
     message= f"{pos['trading_symbol']},qty: {pos['net_quantity']}, ltp: {pos['ltp']}, P/L: {p}"
     p_l=p_l+p
     print(message)
     message_l=message_l + "\n" + message
    return message_l

 def get_positions_json(self,alice):
    poss=alice.get_daywise_positions()['data']['positions']
    return poss

 def get_pending_order_of_a_scrip(self,alice,scrip):
     pending_orders=alice.get_order_history()['data']['pending_orders']
     print(pending_orders)
     if pending_orders:
      print("Pending orders present")
      for pending_order in pending_orders:
         if pending_order['trading_symbol'] == scrip+'-EQ':
            print(f"Pending order for {scrip} is {pending_order['oms_order_id']}")
            return pending_order['oms_order_id'],pending_order['trigger_price'],pending_order['quantity']
     else:
         return '','',''
     
        
 def modify_sl_of_scrip(self,alice,sl_order,scrip,sl,qty):
     alice.cancel_order(order_id=sl_order)
     print("modifying stoploss order for the remaining quantity")
     stop_loss_order = alice.place_order(transaction_type = TransactionType.Sell,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.StopLossLimit,
                     product_type = ProductType.Delivery,
                         price = sl-0.1,
                     trigger_price = sl,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
     print(stop_loss_order)
     print("modified stoploss order for the remaining quantity")

 def cancel_sl_of_scrip(self,alice,scrip,o_qty):
     print("cancelling sl order if present")
     sl_order,sl,po_qty= self.get_pending_order_of_a_scrip(alice,scrip)
     if sl_order:
      m_qty=po_qty-o_qty
      if m_qty ==0:
       alice.cancel_order(sl_order)
       print("Stop loss order cancelled")
       return "Stop loss order cancelled"
      else:
       self.modify_sl_of_scrip(alice,sl_order,scrip,sl,m_qty)

 def place_fno_order(self,alice,transaction_type_,order_type_,scrip,price,sl,qty,expiry_date,is_fut,strike,is_CE):
     fno_instrument=alice.get_instrument_for_fno(symbol = scrip, expiry_date=expiry_date, is_fut=is_fut, strike=strike, is_CE = is_CE)
     print("Placing option order")
     if transaction_type_ == 'BUY':
         order_transaction_type = TransactionType.Buy
         sl_order_transaction_type = TransactionType.Sell 
     elif transaction_type_ == 'SELL':
         order_transaction_type = TransactionType.Sell
         sl_order_transaction_type = TransactionType.Buy          
         
     order=alice.place_order(transaction_type = order_transaction_type,
                     instrument = fno_instrument,
                     quantity = qty*int(fno_instrument.lot_size),
                     order_type = OrderType.Market,
                     product_type = ProductType.Delivery,
                     price = 0.0,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
     
     time.sleep(0.1)
     order_start_time = time.time()
     buy_order_hist=alice.get_order_history(order['data']['oms_order_id'])
     while alice.get_order_history(order['data']['oms_order_id'])['data'][0]['order_status'] != 'complete':
        time.sleep(1)
        print("Order getting filled...",end="\r")
        seconds = int(time.time() - order_start_time)
        if seconds>20:
           break 
     if sl:  
      stop_loss_order = alice.place_order(transaction_type = sl_order_transaction_type,
                     instrument = fno_instrument,
                     quantity = qty*int(fno_instrument.lot_size),
                     order_type = OrderType.StopLossLimit,
                     product_type = ProductType.Delivery,
                     price = float(sl),
                     trigger_price = float(sl),
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
      print(f"Stoploss order,f{stop_loss_order}")
     
 def place_order(self,transaction_type_,order_type_,scrip,token,price,sl,qty):
    
  orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": scrip+"-"+"EQ",
        "symboltoken": token,
        "transactiontype": transaction_type_,
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": price,
        "squareoff": "0",
        "stoploss": "0",
        "quantity": qty
        }
     
  if (order_type_ == 'MKT'):   
     orderparams['ordertype'] = "MARKET"
     
  elif order_type_ == 'LMT' :    
     orderparams['ordertype'] = "LIMIT"
      
     
  order_id=  self.broker_object.placeOrder(orderparams)
  order_book=self.broker_object.orderBook()['data']
  order_status = ''
  for order in order_book:
     if order['orderid'] == order_id:
             order_status= order
     
  order_start_time = time.time()
     
  if order_status['orderstatus'] not in ('rejected'):  
       while order_status != 'complete':           
        time.sleep(0.1)
        seconds = int(time.time() - order_start_time)
        if seconds>20:
           break 
       if sl: 
        if transaction_type_ == 'BUY':
          sl_transaction_type_ = 'SELL'
        else:
          sl_transaction_type_ = 'BUY'
          
        stop_loss_order_params = orderparams = {
        "variety": "STOPLOSS",
        "tradingsymbol": scrip+"-"+"EQ",
        "symboltoken": token,
        "transactiontype": sl_transaction_type_,
        "exchange": "NSE",
        "ordertype": "STOPLOSS_MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "0",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": qty
        }
      
        stop_loss_order=obj.placeOrder(stop_loss_order_params)
        print(f"Stoploss order,f{stop_loss_order}")  
  else:  
        print("Order rejected","Status",order_status['status'],"Error code",order_status['text'])
                
 
  if transaction_type_ == 'EXIT' and order_type_ == 'MKT' :
     sell_order=  alice.place_order(transaction_type = TransactionType.Sell,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.Market,
                     product_type = ProductType.Delivery,
                     price = 0.0,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
     print(f"Sell order placed, exited from {scrip}")


 def place_bracket_order(alice,scrip,qty,price,sl_price,tg_price):
     print(
   alice.place_order(transaction_type = TransactionType.Buy,
                     instrument = alice.get_instrument_by_symbol('NSE', 'SBIN'),
                     quantity = 1,
                     order_type = OrderType.Market,
                     product_type = ProductType.BracketOrder,
                     price = 1000.0,
                     trigger_price = None,
                     stop_loss = 980.0,
                     square_off = 1020.0,
                     trailing_sl = None,
                     is_amo = False)
       )

def check_for_price_difference(extracted_price,scrip_price):
    difference=round(scrip_price-extracted_price,2)
    if scrip_price>0:
     difference_pct=round((((scrip_price-extracted_price)/scrip_price)*100),2)
    else:
     difference_pct=99999
    return difference,difference_pct

def get_position_of_a_scrip(alice,scrip):
    print("Getting position of the scrip")
    segment='EQ'
    pos=alice.get_daywise_positions()['data']['positions']
    #print(pos)
    qty=0
    ltp=0.0
    p_l=0
    i=0
    while i < len(pos):
        if pos[i]['trading_symbol']==scrip +'-' + segment:
           qty= pos[i]['net_quantity']
           ltp = float(pos[i]['ltp'])
           p_l = float(pos[i]['unrealised_pnl'])+float(pos[i]['realised_pnl'])
           i+=1
           break
        else:
           i+=1
    return  qty, ltp,  p_l

def unsubscribe_if_any(alice):
    subs=alice.get_all_subscriptions()
    symbols=[]
    while subs:
     print("Existing subscriptions present")
     for sub in subs.keys():
      symbols.append(sub.symbol)
     for symbol in symbols:
      print(f"Unsubscribing from {symbol}")
      alice.unsubscribe(alice.get_instrument_by_symbol('NSE',symbol), LiveFeedType.SNAPQUOTE)

def stopwatch(count):
    global minutes
    global time_start
    seconds = int(time.time() - time_start) - minutes * 60
    if seconds >= 60:
       minutes += 1
       seconds = 0
    if minutes>=count:
       time_start=time.time()
       minutes=0
       return 1
    elif minutes<count:
       return 0

def get_the_minute():
    now = datetime.datetime.now()
    current_min=now.strftime("%M")
    return int(current_min)

def check_for_the_balance_and_adjust_qty(alice):
    cash=float(alice.get_balance()['data']['cash_positions'][0]['net'])
    print(f"cash available with the broker is {cash}")
    return cash
