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

@app.route('/execute_alerts',methods=['POST'])
def execute_orders_from_telegram():
   try: 
    chat_id=int(request.args.get('chat_id'))

    print("pub/sub Message received")
    envelope = json.loads(request.data.decode('utf-8'))
    payload = base64.b64decode(envelope['message']['data'])
    payload=payload.decode('utf-8')
    print(type(payload))
    
    global alice_broker_objects
    alice_blue_auto_bot=alice_blue_execution(fs,chat_id)
    alice,alice_broker_objects=cache.get_the_alice_object(alice_blue_auto_bot,alice_broker_objects,fs,chat_id)
    print(f"Executing the below order for the client {chat_id}")
    data_str=request.data.decode('utf-8')
    #print(data_str)
    #json_data=json.loads(data_str) # local
    json_data=json.loads(payload)     # pub/sub
    print(json_data)
    print("Placing order to aliceblue")
    #alice,transaction_type_,order_type_,scrip,price,sl,qty
    
    qty,s_l=get_trade_qty(fs,chat_id,json_data['order']['price'])
    time.sleep(s_l)
    scrip=json_data['order']['scrip']
    segment=json_data['order']['segment']
    exchange=json_data['order']['exchange']
    
    #"order": { "segment":self.segment,"exchange":self.exchange,"scrip":self.scrip,"transaction_type":self.transaction_type,"order_type":self.order_type,"price":self.price,"sl":self.sl,"target":self.target },
    print(f"Placing order with qty {qty}")
    if segment == 'EQ':
     alice_blue_auto_bot.place_order(alice,json_data['order']['transaction_type'],'MKT',scrip,0.0,json_data['order']['sl'],qty)
     send_chat_message(chat_id,f"Buy order placed successfully for the scrip {scrip}")
    elif segment == 'OPT' and scrip in ['BANKNIFTY','NIFTY']:
     expiry_date_list=json_data['order']['expiry_date']
     print(expiry_date_list)
     expiry_date=dt.date(expiry_date_list[0],expiry_date_list[1],expiry_date_list[2])
     print(expiry_date)
     qty=1
     is_fut=json_data['order']['is_fut']
     strike=json_data['order']['strike']
     is_CE=json_data['order']['is_CE']
     print("is ce",is_CE)
     #scrip,s_l,qty,expiry_date,is_fut,strike,is_CE
     alice_blue_auto_bot.place_fno_order(alice,json_data['order']['transaction_type'],'MKT',scrip,0.0,json_data['order']['sl'],qty,expiry_date,is_fut,strike,is_CE)
     send_chat_message(chat_id,f"Buy order placed successfully for the option {scrip}")   
     
    positions_message = alice_blue_auto_bot.get_positions(alice)
    send_chat_message(chat_id,f"Positions after the buy order \n{positions_message}")     
    #send_chat_message(chat_id,)
    return "OK",200
   except:
    return "OK",200   
    
@app.route('/send_alerts_to_telegram',methods=['POST'])
def execute_orders_from_chartink():
   try: 
    global data
    print("pub/sub Message received")
    envelope = json.loads(request.data.decode('utf-8'))
    payload = base64.b64decode(envelope['message']['data'])
    payload=payload.decode('utf-8')
    print(type(payload))
    #data_str=request.data.decode('utf-8')
    #print(data_str)
    payload=json.loads(payload)
    
    print("message",payload)
    chat_id=int(request.args.get('chat_id'))
    print("chat_id id received",chat_id)
    #TelegramBot.sendMessage(chat_id=channel_id,text=payload)
    TelegramBot.sendMessage(chat_id=chat_id,text=payload) 
    TelegramBot.sendMessage(chat_id=chat_id,text="Executing the order...")
    alice_blue_auto_bot = alice_blue_execution(fs,chat_id)
    alice=get_the_alice_object(alice_blue_auto_bot,chat_id)
    
    if alice:
      scrips=payload['stocks']
      scan_name=payload['scan_name']
      trigger_prices = payload["trigger_prices"]
      scan_names=['Buy on dips','Stocks turning bullish','15 minutes Bullish momentum stocks','Must Buy']
      if scan_name in scan_names:
        i=0
        orders=[]
        today=dt.datetime.now()
        
        scrips=payload['stocks'].split(',')
        trigger_prices = payload["trigger_prices"].split(',')
        trigger_time_s=payload['triggered_at']
        trigger_time_s=trigger_time_s.replace(' ','')
        print(trigger_time_s)
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
        else:
           #hours_added=-hours_added 
           trigger_time_adjusted = trigger_time - hours_added
        time_diff=round((dt.datetime.now()-trigger_time_adjusted).total_seconds(),2)               
        print("Trigger time adjusted time difference in secs",time_diff) 
              
        if (time_diff) < 240:
               
           while i<len(scrips):
               orders.append([scrips[i],float(trigger_prices[i])])
               print(orders[i])
               i=i+1
           price_threshold=5000
           print(orders)
           transaction_type_='BUY'
           order_type_='MKT'
           #price=float(payload['trigger_prices'])           
           
           for order in orders:
              print(f"Executing order {order}") 
              qty=1
              scrip,price=order[0],order[1]
              sl=price*0.99
              if price < price_threshold:
               alice_blue_auto_bot.place_order(alice,transaction_type_,order_type_,scrip,price,sl,qty)
               print(f"Buy order placed successfully for the scrip {scrip}")
               send_chat_message(chat_id,f"Buy order placed successfully for the scrip {scrip}")
               positions_message = alice_blue_auto_bot.get_positions(alice)
               send_chat_message(chat_id,f"Positions after the buy order \n{positions_message}")             
              else:
               send_chat_message(chat_id,f"unable to trigger order as scrip price is more than {price_threshold}")
        else:
           send_chat_message(chat_id,"alert older than 4 mins")                 
      else:
            send_chat_message(chat_id,f"scan {scan_name} is not registered for auto trigger")  
            
                      
    else:
        print("Unable to execute order")            
    return "OK",200
   except Exception as e:
    print("error",e)   
    return "OK",200 


        
if __name__ == "__main__":        # on running python app.py
    app.run(host='0.0.0.0', port= 8080)                     # run the flask app
    
    