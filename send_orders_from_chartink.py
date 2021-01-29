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
from google.cloud import pubsub_v1

new_dir = os.getcwd()
os.chdir(new_dir)

################   pub sub ################
#project_id = 'boxwood-veld-298509'
#topic_id='test'
#publisher = pubsub_v1.PublisherClient()
#subscriber = pubsub_v1.SubscriberClient() 
#topic_path = publisher.topic_path(project_id, topic_id)

################   pub sub ################


# Importing custom libraries

from turing_library.big_query_client import big_query
from turing_library.alice_blue_execution import alice_blue_execution
from turing_library.gcp_pub_sub import pub_sub
from turing_library.extract_order_from_message import order_details
from turing_library.firestore_client import fire_store
#from scan_telegram import *


# Initialising global variables
ps_client=pub_sub()

global chat_id
chat_id = '626127126'
data='Test'
app = Flask(__name__)             # create an app instance

bot_token = '1021528417:AAGAkVTbfg11PfEYcBflltMg1vT0SiOnK4E'
TelegramBot = telepot.Bot(bot_token)

def modify_chartink_alert(alert):
    order = order_details('chartink')
    order.check_for_chartink_alert(alert)
    
@app.route(f'/publish_chartink_alerts_to_pub_sub', methods=['POST'])
def publish_chartink_alert_to_pub_sub():
    #url = 'https://a2056663f895.ngrok.io'
   try: 
    global data
    if request.method=='POST':
       data=request.data.decode('utf-8')
       print("data",data)
       print("data type",type(data))
       json_data=json.loads(data)
       print("publishing the chartink order message to pubsub")
       #data = data_str.encode("utf-8")
       #ps_client.publish_message('chart_ink_alerts',data,False)
       orders=order_details('chartink')
       orders.check_for_chartink_alert(json_data)
       for order in orders.chartink_orders:
           print(order)
       #future = publisher.publish(topic_path, data)
       #print(future.result())
       print("post request successfully sent")
       return "OK",200
   except Exception as e:
       print("Error",e)
     
    
 
           
if __name__ == "__main__":        # on running python app.py
    app.run(host='0.0.0.0', port= 8080)                     # run the flask app
    
    