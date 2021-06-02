import os
import requests
import telepot
import telegram
from flask import Flask, render_template, request
from alice_blue import *
import re,json
import time
from pathlib import Path
import base64
import platform
from datetime import datetime
import datetime as dt
from time import gmtime, strftime

# Importing custom libraries
new_dir = os.getcwd()
os.chdir(new_dir)
   
from turing_library.big_query_client import big_query
from turing_library.alice_blue_execution import alice_blue_execution
from turing_library.firestore_client import fire_store
from turing_library.cache import cache
#from scan_telegram import *

########################################Ngrok only for local#########################################
#if platform.system() == 'Windows':
# from pyngrok import ngrok
# http_tunnel = ngrok.connect(8080)
# url = http_tunnel.public_url
# url=url.replace('http','https')
# print(url)
#else:
# url='https://execute-alerts-iz6nlikcna-el.a.run.app'   
########################################Ngrok only for local#########################################


fs=fire_store()
cache=cache()
# Initialising global variables
global chat_id
chat_id = 626127126
data='Test'
app = Flask(__name__)             # create an app instance

bot_token = '1021528417:AAGAkVTbfg11PfEYcBflltMg1vT0SiOnK4E'
TelegramBot = telepot.Bot(bot_token)
#channel_id='-436542169'
channel_id='-1001392962142'
global alice_broker_objects
alice_broker_objects={}


def send_chat_message(chat_id,text):
    TelegramBot.sendMessage(chat_id=chat_id, text=text)
    return "Success"

#Initializing big query and alice objects
#bq=big_query(chat_id)
#alice_blue_auto_bot = alice_blue_execution(fs,chat_id)


def get_trade_qty(fs,chat_id,price):
        docs = fs.client.collection('user_details').where(u'chat_id',u'==',chat_id).stream()
        docs = [doc.to_dict() for doc in docs]
        if docs:
         amount=docs[0]['trade_amount']
         s_l=docs[0]['s_l']
         return round(amount/float(price)),s_l
        else:
         return None 
#user_details=bq.fetch_user_creds()
#alice = alice_blue_auto_bot.generate_client(username=user_details[3].upper(), password=user_details[4], twoFA=user_details[5],  api_secret=user_details[6],access_token=user_details[7])
     
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
    #print(message)
    #print(f"1 Best ask price of the scrip is {latest_ask_price}")
    #return latest_ask_price,latest_bid_price

def open_callback():
    global socket_opened
    socket_opened = True

##print("Initialized Alice Blue Broker")
#open_web_socket(alice)
alice_blue_auto_bot=alice_blue_execution(fs,chat_id)

alice,alice_broker_objects=cache.get_the_alice_object(alice_blue_auto_bot,alice_broker_objects,fs,chat_id)

alice_blue_auto_bot.place_fno_order(alice,json_data['order']['transaction_type'],'MKT',scrip,0.0,json_data['order']['sl'],qty,expiry_date,is_fut,strike,is_CE)
     send_chat_message(chat_id,f"Buy order placed successfully for the option {scrip}")   
     

    
    qty,s_l=get_trade_qty(fs,chat_id,json_data['order']['price'])


                 # run the flask app
    
    