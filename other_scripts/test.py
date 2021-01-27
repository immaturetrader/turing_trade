# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 15:16:29 2020

@author: sravula
"""

import asyncio
import time,sys
import pandas as pd
from scan_telegram import *
from scan_telegram import send_message_to_a_channel,get_channel_data
from Extract_trade_intents import check_for_orders,pre_process_data
import alice_blue_execution
from alice_blue_execution import *
from nsetools import Nse
import datetime
import os
import json
from alice_blue import *
global telegram_bot_data,alice_blue_bot_data
global socket_opened,alice
import math
import sys
json_data_dir=''
global incoming_channel_id,outgoing_channel_id
global subscribed_scrip
from urllib3.exceptions import ReadTimeoutError
import logging
logging.basicConfig(level=logging.ERROR,filemode='w',filename='Logs/send_auto_orders_log.log',format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%d-%b-%y %H:%M:%S')
global latest_ask_price,latest_bid_price
latest_ask_price=0
latest_bid_price=0 

subscribed_scrip=''
with open(json_data_dir+'alice_blue_bot_data.json') as json_data:
     alice_blue_bot_data = json.load(json_data)
with open(json_data_dir+'telegram_bot_data.json') as json_data:
     telegram_bot_data = json.load(json_data)
with open(json_data_dir+'Trade_parameters.json') as json_data:
     trade_parameters = json.load(json_data)
     
working_dir=telegram_bot_data['working_directory']  
incoming_channel_id=telegram_bot_data['read_channel']
outgoing_channel_id=telegram_bot_data['write_channel']

def update_order_sheet_with_pl(alice):
    orders=pd.read_csv('Orders/Order_Book_2020_7_30.csv')
    pos=alice.get_daywise_positions()['data']['positions']
    message_l=''
    i=0
    buy_qty=0
    sell_qty=0
    p_l=0    
    while i < len(pos): 
     p=round(float(pos[i]['unrealised_pnl'])+float(pos[i]['realised_pnl']),2)
     segment='EQ'
     symbol=pos[i]['trading_symbol']
     orders.loc[orders['nse_scrip']+'-'+segment==symbol,'total_buy_quantity']=pos[i]['total_buy_quantity']
     orders.loc[orders['nse_scrip']+'-'+segment==symbol,'total_sell_qty']=pos[i]['total_sell_quantity']
     orders.loc[orders['nse_scrip']+'-'+segment==symbol,'avg_buy_price']=pos[i]['average_buy_price']
     orders.loc[orders['nse_scrip']+'-'+segment==symbol,'avg_sell_price']=pos[i]['average_buy_price']
     orders.loc[orders['nse_scrip']+'-'+segment==symbol,'amount_in_trade']=pos[i]['buy_amount_mtm']
     orders.loc[orders['nse_scrip']+'-'+segment==symbol,'p/l']=p
     orders.loc[orders['nse_scrip']+'-'+segment==symbol,'p/l_percent']=(p/float(pos[i]['buy_amount_mtm']))*100
     message= f"{pos[i]['trading_symbol']},qty: {pos[i]['net_quantity']}, ltp: {pos[i]['ltp']}, P/L: {p}"            											
     p_l=p_l+p
     print(message)    
     #print(orders['total_buy_quantity'])
     message_l=message_l + "\n" + message
     i+=1 
     
    orders.to_csv('Orders/Order_Book_2020_7_30_n.csv',index=False)  
    
alice=init_alice_blue()
update_order_sheet_with_pl(alice)
