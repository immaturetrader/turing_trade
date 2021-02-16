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

alice_broker_objects={}

orders=fs.get_orders()

for order in orders:
    print(order)

users = fs.get_all_user_chats()    

users=[(user['chat_id'],user['trigger_orders']) for user in users if 'trigger_orders' in user.keys()]

for user in users:
    chat_id=user[0]
    if user[1]=='Y':
     alice_blue_auto_bot=alice_blue_execution(fs,chat_id)
     alice,alice_broker_objects[chat_id]=cache.get_the_alice_object(alice_blue_auto_bot,alice_broker_objects,fs,chat_id)
     poss=alice_blue_auto_bot.get_positions_json(alice)
     rec={}
     #print(poss)
     for pos in poss:
      rec['chat_id']=chat_id
      rec['chat_id']['positions']=pos      
      fs.client.collection('orders').add(rec)
     
    
    