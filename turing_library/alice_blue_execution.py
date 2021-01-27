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
from turing_library.alice_blue import *
#import big_query_client
import pickle

class alice_blue_execution():

 def __init__(self,fs,chat_id):
     self.chat_id = chat_id
     self.bq = big_query(chat_id)
     self.alice = ''
     self.fs = fs

 def generate_access_token(self,username,password,twoFA,api_secret,app_id):

  #print(f"generating access token for {login_data['username']}")
  access_token = AliceBlue.login_and_get_access_token(username=username, password=password, twoFA=twoFA,  api_secret=api_secret,app_id=app_id)
  print("Access token generated",access_token)
  return access_token

 def generate_client(self,username,password,twoFA,api_secret,access_token,app_id,master_contracts_to_download):
  try:
   print("generating the client with existing token")
   self.alice = AliceBlue(username=username, password=password, access_token=access_token,app_id=app_id)
#   with open("AB126971.alice", "wb") as f:
#    pickle.dump(self.alice, f, pickle.HIGHEST_PROTOCOL)
   return self.alice
  except:
   print("Unable to login using the current access token, regenerating new one")
   access_token = self.generate_access_token(username,password,twoFA,api_secret,app_id)
   self.alice = AliceBlue(username=username, password=password, access_token=access_token,app_id=app_id,master_contracts_to_download=master_contracts_to_download)
   self.fs.update_access_token(self.chat_id,access_token)
#   with open("AB126971.alice", "wb") as f:
#    pickle.dump(self.alice, f, pickle.HIGHEST_PROTOCOL)
   return self.alice

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

 def place_order(self,alice,transaction_type_,order_type_,scrip,price,sl,qty):
    
  if (transaction_type_ == 'BUY' and order_type_ == 'MKT'):
     print("Placing buy market order")
     buy_order=  alice.place_order(transaction_type = TransactionType.Buy,
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
     time.sleep(0.1)
     order_start_time = time.time()
     buy_order_hist=alice.get_order_history(buy_order['data']['oms_order_id'])
     while alice.get_order_history(buy_order['data']['oms_order_id'])['data'][0]['order_status'] != 'complete':
        time.sleep(1)
        print("Order getting filled...",end="\r")
        seconds = int(time.time() - order_start_time)
        if seconds>20:
           break 
     if sl:  
      stop_loss_order = alice.place_order(transaction_type = TransactionType.Sell,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.StopLossLimit,
                     product_type = ProductType.Delivery,
                     price = float(sl),
                     trigger_price = float(sl),
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
      print(f"Stoploss order,f{stop_loss_order}")        
        
     
  elif transaction_type_ == 'BUY' and order_type_ == 'LMT' :
    print("Placing buy Limit order") 
    buy_order=  alice.place_order(transaction_type = TransactionType.Buy,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.Limit,
                     product_type = ProductType.Delivery,
                     price = price,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
    time.sleep(0.1)
    buy_order_hist=alice.get_order_history(buy_order['data']['oms_order_id'])
    #print(buy_order_hist)
    order_start_time = time.time()
    if sl:
     stop_loss_order = alice.place_order(transaction_type = TransactionType.Sell,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.StopLossLimit,
                     product_type = ProductType.Delivery,
                         price = sl,
                     trigger_price = sl,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)

    while alice.get_order_history(buy_order['data']['oms_order_id'])['data'][0]['order_status'] != 'complete':
        time.sleep(1)
        print("Order getting filled...",end="\r")
        seconds = int(time.time() - order_start_time) - minutes * 60
        if seconds > 30:
           print("Modifying the order to market order type as order did not get filled under a minute")
           filled_qty=int(alice.get_order_history(buy_order['data']['oms_order_id'])['data'][0]['filled_quantity'])
           alice.cancel_order(int(buy_order['data']['oms_order_id']))
           print("cancelled the order which was not filled")
           buy_order=  alice.place_order(transaction_type = TransactionType.Buy,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty-filled_qty,
                     order_type = OrderType.Market,
                     product_type = ProductType.Delivery,
                     price = 0.0,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
           print("Placed market order type for the qty which did not get filled")
           time.sleep(0.3)
           break
        pass
    if alice.get_order_history(buy_order['data']['oms_order_id'])['data'][0]['order_status'] == 'complete':
       Order_Filled = True
    else:
       Order_Filled = False
    stop_loss_order={}
    if Order_Filled:
     print("Limit order got filled, placing stoploss order")
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
     stop_loss_order_hist=alice.get_order_history(stop_loss_order['data']['oms_order_id'])
     return f"Buy Order placed: Order_id: {buy_order['data']['oms_order_id']}, Status: {buy_order_hist['data'][0]['order_status']}, Rejection_Reason: {buy_order_hist['data'][0]['rejection_reason']}, Stop Loss Order placed: Order_id: {stop_loss_order['data']['oms_order_id']}, Status: {stop_loss_order_hist['data'][0]['order_status']}, Rejection_Reason: {stop_loss_order_hist['data'][0]['rejection_reason']} ",int(buy_order['data']['oms_order_id']),int(stop_loss_order['data']['oms_order_id'])
    else:
     print(f"Order did not get filled or got rejected {alice.get_order_history(buy_order['data']['oms_order_id'])['data'][0]}")
     time.sleep(0.1)
     return "Order was not filled in 1 minute, check the order status in broker's site",0,0

  elif transaction_type_ == 'SELL' and order_type_ == 'LMT' :
     sell_order=  alice.place_order(transaction_type = TransactionType.Sell,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.Limit,
                     product_type = ProductType.Intraday,
                     price = price,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
     stop_loss_order = alice.place_order(transaction_type = TransactionType.Sell,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.StopLossLimit,
                     product_type = ProductType.Delivery,
                     price = sl,
                     trigger_price = sl+0.1,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)

     return "Sell order placed",'',
 
  elif transaction_type_ == 'SELL' and order_type_ == 'MKT' :
     sell_order=  alice.place_order(transaction_type = TransactionType.Sell,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.Market,
                     product_type = ProductType.Intraday,
                     price = 0.0,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)
     stop_loss_order = alice.place_order(transaction_type = TransactionType.Sell,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.StopLossLimit,
                     product_type = ProductType.Delivery,
                     price = sl,
                     trigger_price = sl+0.1,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)

     return "Sell order placed",'',    
 
  elif transaction_type_ == 'EXIT' and order_type_ == 'MKT' :
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

  elif transaction_type_ == 'ABOVE':
     buy_order=  alice.place_order(transaction_type = TransactionType.Buy,
                     instrument = alice.get_instrument_by_symbol('NSE', scrip),
                     quantity = qty,
                     order_type = OrderType.StopLossLimit,
                     product_type = ProductType.Delivery,
                     price = price,
                     trigger_price = price-0.1,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = False)

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
     buy_order_hist=alice.get_order_history(buy_order['data']['oms_order_id'])
     stop_loss_order_hist=alice.get_order_history(stop_loss_order['data']['oms_order_id'])
     return f"Above limit Order placed: Order_id: {buy_order['data']['oms_order_id']}, Status: {buy_order_hist['data'][0]['order_status']}, Rejection_Reason: {buy_order_hist['data'][0]['rejection_reason']}, Stop Loss Order placed: Order_id: {stop_loss_order['data']['oms_order_id']}, Status: {stop_loss_order_hist['data'][0]['order_status']}, Rejection_Reason: {stop_loss_order_hist['data'][0]['rejection_reason']} ",buy_order['data']['oms_order_id'],stop_loss_order['data']['oms_order_id']


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
