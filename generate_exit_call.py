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
#from alice_blue import *
import re
import platform


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
#chat_id=626127126
open_positions = fs.get_open_positions()

chat_id,scrip,qty,trade_closed,target_price = open_positions['chat_id'],open_positions['scrip'],open_positions['qty'],open_positions['trade_closed'],open_positions['target']
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
alice,alice_broker_objects=cache.get_the_alice_object(alice_blue_auto_bot,alice_broker_objects,fs,chat_id)
#alice.start_websocket(subscribe_callback=event_handler_quote_update,
#                      socket_open_callback=open_callback,
#                      run_in_background=True)

def check_for_exit_signal():
        pass
    
    
def main():
    global socket_opened
    global alice
    global EMA_CROSS_SCRIP
    #print(alice.get_balance()) # get balance / margin limits
    #print(alice.get_profile()) # get profile
    #print(alice.get_daywise_positions()) # get daywise positions
    #print(alice.get_netwise_positions()) # get netwise positions
    #print(alice.get_holding_positions()) # get holding positions

    #ins_scrip = alice.get_instrument_by_symbol('NSE', EMA_CROSS_SCRIP)
    #EMA_CROSS_SCRIP = 'MINDACORP'
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
    #target_price=65220
    #alice.unsubscribe(alice.get_instrument_by_symbol('MCX', EMA_CROSS_SCRIP), LiveFeedType.COMPACT)

    alice.subscribe(alice.get_instrument_by_symbol('NSE', scrip), LiveFeedType.COMPACT)
    print(f"subscribed to the instrument {scrip}")
    sleep(0.5)

    print(open_positions)

    while True :
     print("checking for the target price")
     sleep(1)
     if open_positions and trade_closed == 'N':
      if scrip_quotes[scrip]['ltp'] >= open_positions['target']:
         print(f"price crossed {target_price}, price : {scrip_quotes[scrip]['ltp']}")
         print(scrip_quotes[scrip]['ltp'])
         print("Target achieved, triggering the sell order")
         alice_blue_auto_bot.place_order(alice,transaction_type_,order_type_,scrip,price,sl,qty)
         fs.update_open_positions(chat_id,'Y')
         break
      sleep(1)

if(__name__ == '__main__'):
    main()
