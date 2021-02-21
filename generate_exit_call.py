import logging
import datetime
import statistics
from time import sleep
from alice_blue import *
import json
import pandas as pd
import os
import requests
import telepot
import telegram
from flask import Flask, render_template, request
import threading
import re
import platform

new_dir = os.getcwd()
os.chdir(new_dir)

from turing_library.big_query_client import big_query
from turing_library.alice_blue_execution import alice_blue_execution
from turing_library.firestore_client import fire_store
from turing_library.alice_blue import TransactionType, OrderType, ProductType, LiveFeedType, Instrument
from turing_library.cache import cache

global chat_id
global alice_broker_objects
alice_broker_objects={}
global scrip_quotes
scrip_quotes={}

cache= cache()
fs=fire_store()
chat_id=626127126
open_positions = fs.get_orders()
print(open_positions)

#scrip,qty,trade_closed,target_price = open_positions['scrip'],open_positions['qty'],open_positions['trade_closed'],open_positions['target']
alice_blue_auto_bot = alice_blue_execution(fs,chat_id)

ltp = 0

def event_handler_quote_update(message):
    global scrip_quotes
    scrip_quotes[message['instrument'][2]]={'exchange':message['instrument'][0],'time':message['exchange_time_stamp'],'ltp':float(message['ltp'])}
    print(scrip_quotes)
    check_for_exit_signal()
    #print(type(message))
    #print(message)
    #print(message['exchange_time_stamp'],message['instrument'][0],message['instrument'][2],message['ltp'])

def open_callback():
    global socket_opened
    socket_opened = True

global alice
global socket_opened
global open_orders
open_orders = [pos for pos in open_positions]
alice,alice_broker_objects=cache.get_the_alice_object(alice_blue_auto_bot,alice_broker_objects,fs,chat_id)
#alice.start_websocket(subscribe_callback=event_handler_quote_update,
#                      socket_open_callback=open_callback,
#                      run_in_background=True)

def check_for_exit_signal():
        pass
    
def get_updates_on_doc():
 callback_done = threading.Event()
 
 def on_snapshot(doc_snapshot, changes, read_time):
     for doc in doc_snapshot:
         print(f'Received document snapshot: {doc.to_dict()}')
         open_orders.append(doc.to_dict())
         print("added the doc to open orders")
     callback_done.set()
     
 doc_ref = fs.client.collection(u'orders')
 doc_watch = doc_ref.on_snapshot(on_snapshot)
 
 
def get_updates_on_collection():
    
    delete_done = threading.Event()
    print("checking for updates")
    def on_snapshot(col_snapshot, changes, read_time):
      print(u'Callback received query snapshot.')
      #print(u'Current data: ')
      for change in changes:
         if change.type.name == 'ADDED':
             print(f'New record: {change.document.to_dict()}')
         elif change.type.name == 'MODIFIED':
             print(f'Modified record: {change.document.to_dict()}')
         elif change.type.name == 'REMOVED':
             print(f'Deleted record: {change.document.to_dict()}')
             delete_done.set()
    col_query = fs.client.collection(u'orders').where(u'order.trade_closed', u'==', 'N')  
    #col_query = fs.client.collection(u'orders')
    # Watch the collection query
    query_watch = col_query.on_snapshot(on_snapshot)      
    

    
def main():
    global socket_opened
    global alice
    global EMA_CROSS_SCRIP
    global open_orders
    socket_opened = False
    alice.start_websocket(subscribe_callback=event_handler_quote_update,
                          socket_open_callback=open_callback,
                          run_in_background=True)
    while(socket_opened==False):    # wait till socket open & then subscribe

        pass
    print("websocket opened")

    transaction_type_='EXIT'
    order_type_='MKT'
    price=None
    sl=None
    get_updates_on_collection()
    #target_price=65220
    #alice.unsubscribe(alice.get_instrument_by_symbol('MCX', EMA_CROSS_SCRIP), LiveFeedType.COMPACT)
    for order in open_orders:
     print(order)   
     scrip=order['order']['scrip']   
     alice.subscribe(alice.get_instrument_by_symbol('NSE', scrip), LiveFeedType.COMPACT)
     print(f"subscribed to the instrument {scrip}")
     sleep(0.5)
    #print("document_id",open_positions.id)
    print(open_positions)

	#Instead of for loop of all the stocks, check for the bucket order
	
    while True :
     print(".")
     sleep(1)
     for order in open_orders:
      #print(order)   
      if order and order['order']['trade_closed'] == 'N':
       scrip=order['order']['scrip']
       segment=order['order']['segment']
       target_price=order['order']['bid_price']*0.99  
       print(f"target price for {scrip} is {target_price} and current price is {scrip_quotes[scrip]['ltp']}")
       if scrip_quotes[scrip]['ltp'] >= target_price:
         print(f"price crossed {target_price}, price : {scrip_quotes[scrip]['ltp']}")
         print(scrip_quotes[scrip]['ltp'])
         print("Target achieved, triggering the sell order")
         alice_blue_auto_bot.place_order(alice,transaction_type_,order_type_,scrip,price,sl,1)
         fs.update_orders(scrip,segment,'Y')
         open_orders.remove(order)
         break
       sleep(1)

if(__name__ == '__main__'):
    main()
