

"""
A sample Hello World server.

"""
import os
import requests
import telepot
import telegram
from flask import Flask, render_template, request
from turing_library.gcp_pub_sub import pub_sub
#from alice_blue import *
import re
import platform

new_dir = os.getcwd()
os.chdir(new_dir)
ps=pub_sub()
def set_telegram_webhook(bot_token,url):
     print(f"Setting webhook to {url}")
     telepot.Bot(bot_token).setWebhook(url=url)

########################################Ngrok only for local#########################################
if platform.system() == 'Windowss':
 from pyngrok import ngrok
 http_tunnel = ngrok.connect(8080)
 url = http_tunnel.public_url
 url=url.replace('http','https')
 print(url)
 bot_token = '1021528417:AAGAkVTbfg11PfEYcBflltMg1vT0SiOnK4E'
 url= url + f"/{bot_token}"
 set_telegram_webhook(bot_token,url)
else:
 url='https://planetpythonbot-iz6nlikcna-el.a.run.app'
 bot_token = '1021528417:AAGAkVTbfg11PfEYcBflltMg1vT0SiOnK4E'
 url= url + f"/{bot_token}"
 set_telegram_webhook(bot_token,url)
########################################Ngrok only for local#########################################

# Importing custom libraries

from turing_library.big_query_client import big_query
from turing_library.alice_blue_execution import alice_blue_execution
from turing_library.firestore_client import fire_store
from turing_library.alice_blue import TransactionType, OrderType, ProductType, LiveFeedType, Instrument




# Initialising global variables
global chat_id
global alice_broker_objects
alice_broker_objects={}

fs=fire_store()

# pylint: disable=C0103
app = Flask(__name__)

"""
{'message_id': 538, 'date': 1608310457, 'chat': {'id': 626127126, 'type': 'private', 'username': 'sai_kiran0901', 'first_name': 'Sai Kiran'}, 'text': 'Hi', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 'from': {'id': 626127126, 'first_name': 'Sai Kiran', 'is_bot': False, 'username': 'sai_kiran0901', 'language_code': 'en'}}
"""

bot_token = '1021528417:AAGAkVTbfg11PfEYcBflltMg1vT0SiOnK4E'
TelegramBot = telepot.Bot(bot_token)
bq=big_query('626127126')

def get_the_alice_object(alice_blue_auto_bot,chat_id):
           print("Getting the alice object")
           try:
             if chat_id in alice_broker_objects.keys():
               print("alice user object present")
               alice = alice_broker_objects[chat_id]
               alice.get_profile()
               return alice
             else:
               print("alice user object not present generating")
               user_details=fs.fetch_user_creds(chat_id)
               if fs.user_registered=='Y':
                print("generating client")
                alice = alice_blue_auto_bot.generate_client(username=user_details['client_id'].upper(), password=user_details['password'], twoFA=user_details['twoFA'],  api_secret=user_details['api_secret'],access_token=user_details['access_token'],app_id=user_details['app_id'],master_contracts_to_download=['NSE'])
                alice_broker_objects[chat_id]=alice
                print("added alice user object to the dict")
                return alice
               else:
                send_chat_message("User not registered or unable to get profile details")
           except:
               print("Unable to get profile with existing alice object")
               user_details=fs.fetch_user_creds(chat_id)
               if fs.user_registered=='Y':
                print("generating client")
                alice = alice_blue_auto_bot.generate_client(username=user_details['client_id'].upper(), password=user_details['password'], twoFA=user_details['twoFA'],  api_secret=user_details['api_secret'],access_token=user_details['access_token'],app_id=user_details['app_id'],master_contracts_to_download=['NSE'])
                print("adding alice user object to the dict")
                alice_broker_objects[chat_id]=alice
                return alice
               else:
                send_chat_message("User not registered or unable to get profile details")


def send_chat_message(text):
    TelegramBot.sendMessage(chat_id=chat_id, text=text)
    return "Success"

@app.route(f'/{bot_token}', methods=['POST'])
def hello():
 #return 1
 try:
    print("Telegram message received")
    update = telegram.Update.de_json(request.get_json(force=True), TelegramBot)
    global chat_id
    chat_id = update.message.chat.id

    alice_blue_auto_bot = alice_blue_execution(fs,chat_id)
    text_message = update.message.text.encode('utf-8').decode()
    print(text_message)
    first_name = update.message.chat.first_name

    if text_message.lower() == 'hi':
     send_chat_message(f'Hi {first_name}, Welcome to the turing trades. How can I help you?')
     return "Hi"

    elif text_message.lower() == 'register':
      send_chat_message('Please provide your broker details in the format register myself telegram_username broker client_id password twofa api_secret access_token app_id')
      return "successful"

    elif 'register-myself' in text_message.lower():
        client_detail = text_message.split(' ')
        print(chat_id,client_detail[0],client_detail[1],client_detail[2],client_detail[3],client_detail[4],client_detail[5],client_detail[6],client_detail[7],client_detail[8])
        user_message = fs.register_user(chat_id,client_detail[1],client_detail[2],client_detail[3],client_detail[4],client_detail[5],client_detail[6],client_detail[7],client_detail[8])
        TelegramBot.sendMessage(chat_id=chat_id, text=user_message)
        return 'Success'

    elif text_message.lower()=='creds':
        user_details=fs.fetch_user_creds(chat_id)
        if fs.user_registered ==  'Y':
         send_chat_message(user_details)
        else:
         send_chat_message('Unable to find the user')
        return 'Success'


    elif text_message.lower()=='bal':
           alice = get_the_alice_object(alice_blue_auto_bot,chat_id)
           if alice:
            send_chat_message(f"Available balance is {float(alice.get_balance()['data']['cash_positions'][0]['net'])}")

    elif 'buy' in text_message.lower():
           alice=get_the_alice_object(alice_blue_auto_bot,chat_id)
           if alice:
            order_message = text_message.upper()
            re_s = 'BUY (.*?) (\d+)'
            order_parameters = re.findall(re_s,order_message)
            print(order_parameters)
            scrip,qty = order_parameters[0][0],int(order_parameters[0][1])
            transaction_type_='BUY'
            order_type_='MKT'
            price=None
            sl=None
            alice_blue_auto_bot.place_order(alice,transaction_type_,order_type_,scrip,price,sl,qty)
            print("Buy order placed successfully")
            send_chat_message("Buy order placed successfully")
            positions_message = alice_blue_auto_bot.get_positions(alice)
            send_chat_message(f"Positions after the buy order \n{positions_message}")

    elif 'exit' in text_message.lower():
           alice=get_the_alice_object(alice_blue_auto_bot,chat_id)
           if alice:
            #alice = alice_blue_auto_bot.generate_client(username=user_details[3].upper(), password=user_details[4], twoFA=user_details[5],  api_secret=user_details[6],access_token=user_details[7])

            order_message = text_message.upper()
            re_s = 'EXIT (.*?) (\d+)'
            order_parameters = re.findall(re_s,order_message)
            print(order_parameters)
            scrip,qty = order_parameters[0][0],int(order_parameters[0][1])
            transaction_type_='EXIT'
            order_type_='MKT'
            price=None
            sl=None
            sl_order=alice_blue_auto_bot.cancel_sl_of_scrip(alice,scrip,qty)

            if sl_order:
               send_chat_message(sl_order)

#            sell_order=  alice.place_order(transaction_type = TransactionType.Sell,
#                      instrument = alice.get_instrument_by_symbol('NSE', scrip),
#                      quantity = qty,
#                      order_type = OrderType.Market,
#                      product_type = ProductType.Delivery,
#                      price = 0.0,
#                      trigger_price = None,
#                      stop_loss = None,
#                      square_off = None,
#                      trailing_sl = None,
#                      is_amo = False)

            #alice_blue_auto_bot.modify_sl_of_scrip(alice,scrip)
            alice_blue_auto_bot.place_order(alice,transaction_type_,order_type_,scrip,price,sl,qty)
            
            print("Sell order placed successfully")
            send_chat_message("Sell order placed successfully")

            positions_message = alice_blue_auto_bot.get_positions(alice)
            send_chat_message(f"Positions after the sell order \n{positions_message}")

    elif text_message.lower() == 'poss':
           alice=get_the_alice_object(alice_blue_auto_bot,chat_id)
           if alice:
            positions_message = alice_blue_auto_bot.get_positions(alice)
            print(f"Today's positions\n{positions_message}")
            send_chat_message(f"Today's positions\n{positions_message}")

    elif text_message.lower() == 'token':
      TelegramBot.sendMessage(chat_id=chat_id, text=bq.access_token)
      
    elif text_message.lower() == 'start telegram alerts':
         ps.create_subscription_to_a_topic('telegram_alerts',chat_id)
         TelegramBot.sendMessage(chat_id,"At your command, looking for telegram alerts")
         
    elif text_message.lower() == 'stop telegram alerts':
         ps.delete_subcription_from_a_topic('telegram_alerts',chat_id)
         TelegramBot.sendMessage(chat_id,"Yes, stopped telegram alerts")
         
    elif text_message.lower() == 'start chartink alerts':
         ps.create_subscription_to_a_topic('chart_ink_alerts',chat_id)
         TelegramBot.sendMessage(chat_id,"At your command, looking for chartink alerts")
         
    elif text_message.lower() == 'stop chartink alerts':
         ps.delete_subcription_from_a_topic('chart_ink_alerts',chat_id)
         TelegramBot.sendMessage(chat_id,"Yes, stopped chartink alerts")         
         
    else:
      TelegramBot.sendMessage(chat_id=chat_id, text='Could not recognize the command')
      return 'Success'
    return "Success"
 except Exception as e:
    print(f"Exception,{e}")
    return "Exception"

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
    #hello('register-user',626127126)
