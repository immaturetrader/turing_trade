# -*- coding: utf-8 -*-
"""
Created on Fri May 29 23:25:54 2020

@author: sravula
"""
import pandas as pd
from telethon.sessions import StringSession
import asyncio
import telepot
import os
from telethon.sync import TelegramClient,events
from turing_library.firestore_client import fire_store
from turing_library.big_query_client import big_query
from turing_library.extract_order_from_message import order_details
from turing_library.gcp_pub_sub import pub_sub

import json
import requests

#print("current directory",os.getcwd())
new_dir = os.getcwd()
os.chdir(new_dir)
fs=fire_store()
#print("new directory",os.getcwd())


# generate string for the session


#async with TelegramClient(StringSession(),'1339277', '5fdc451937e250be8997cd103ca4c541',) as client:
#    print(client.session.save())
    
    
ps_client=pub_sub()

bot_token = '1021528417:AAGAkVTbfg11PfEYcBflltMg1vT0SiOnK4E'
TelegramBot = telepot.Bot(bot_token)

def send_chat_message(chat_id,text):
    TelegramBot.sendMessage(chat_id=chat_id, text=text)
    return "Success"

print("running scan telegram")
class scan_telegram_channel():

 def __init__(self,channel_id):
     print("Initializing scan_telegram_channel class")
     self.bq=big_query('66127126')
     self.channel_id=channel_id


     telegram_creds=fs.fetch_telegram_admin_creds()
     self.api_id = telegram_creds['api_id']
     self.api_hash = telegram_creds['api_hash']
     self.string_session=telegram_creds['channel_strings'][self.channel_id]['session_string']
     print("session string",self.string_session)
         #self.string_session = '1BVtsOMEBu1ge7fa97xs6eWZaoxXY5eZzO3Bgvd_ULzlcMid95Wq4LoaZHM6kO2zfkuNRTGPqtA4eShUc76Cnm4GIBBPhwQM7wqodxA98a5teUEWlmNtQmHBlmxdq6Uj5kwB6oScdqwyauNtmG_gnE6d3KC4thBSmaIY-CuyoDqeO3wXYbfPnMdAiyc-44upv367GhJCA83IyIOFqGQYMUcBDKop1Ft_e3V41oA6Ta4DZmesgEqv76_mFEDd8avnJEOXnd6zS9G8pzyQMMxMESlks7cFDrpd8IL5XjRXIx7tcUsi6m1mg1jIb7kkLnjXoC70h-VJ0YfD0J4JjTXxvHm3wFHWfvos='
     self.history_messages_df=pd.DataFrame(data={'channel_id':['1'],'m_id':[1],'m_timestamp':[pd.Timestamp('2021-01-01 01:01:01+00:00')],'message':['1'],'reply_m_id':['1'],'reply_to_message':['1']})
     print(self.history_messages_df)

 async def get_telegram_channel_data(self):
   #print("Opening telegram session",self.telegram_session)
   m_id_max = self.bq.fetch_max_id_of_a_channel(self.channel_id)
   async with TelegramClient(StringSession(self.string_session), self.api_id, self.api_hash) as client:
    await client.start()
    i=0
    async for message in client.iter_messages(self.channel_id,min_id=m_id_max):
         #print(message)
         reply_to_msg_id=''
         reply_to_message=''
         reply_to_msg_id = message.reply_to_msg_id
         if reply_to_msg_id:
            ref=''
            if len(ref)==1:
             #print(ref)
             reply_to_message=ref['message'].item()

         m_message=str(message.message).replace('\n',' ')
         m_message=m_message.replace('  ',' ')
         #write_to_sqllite_db(sql_conn, channel_id,message.id,message.date.strftime("%m/%d/%Y, %H:%M:%S"),m_message,reply_to_msg_id,reply_to_message)
         self.history_messages_df.loc[i]=self.channel_id,int(message.id),pd.Timestamp(message.date.strftime("%Y-%m-%d %H:%M:%S+00:00")),m_message,reply_to_msg_id,reply_to_message
         print(pd.Timestamp(message.date.strftime("%Y-%m-%d %H:%M:%S+00:00")))
         i=i+1
    print("Dataframe schema",pd.io.json.build_table_schema(self.history_messages_df),self.history_messages_df.info())
    self.bq.insert_dataframe_into_table('table',self.history_messages_df)
    #bq.insert_into_messages(channel_id,message.id,message.date.strftime("%Y-%m-%d %H:%M:%S+00"),m_message,reply_to_msg_id,reply_to_message)
    print("Inserted the history data successfully")


 async def get_new_messages_on_events(self):
    print("starting the client")
    client = TelegramClient(StringSession(self.string_session), self.api_id, self.api_hash)
    send_chat_message(626127126,f"started listening to the events of channel {self.channel_id}")
    @client.on(events.NewMessage(self.channel_id))
    async def my_event_handler(event):
     print('message received')
     print("Processing the message")
     message = event.original_update.message
     #print(message)
     m_message = str(message.message).replace('\n',' ')
     m_message=m_message.replace('  ',' ')
     print(m_message)
     #order=order_details()
     order = order_details('telegram')
     order.channel=self.channel_id
     order.channel_type='public'

     order.message=m_message
     order.m_id=message.id
     #print(order.__dict__())
     order.clean_message()
     order.extract_intents()
     print("Processed the message")
     url = 'http://06ade21bae0b.ngrok.io/execute_alerts?chat_id=626127126'
     #url_manoj = 'http://9ad3b6c5b6fe.ngrok.io/execute_alerts?chat_id=1363529369'

     #message = message_obj.message

     reply_to_message=''
     reply_to_msg_id=''
     #write_to_bigquery(bigquery_client, channel_id,message.id,message.date.strftime("%m/%d/%Y, %H:%M:%S"),m_message,reply_to_msg_id,reply_to_message)
     print(f"Posting the request to the url {url}")
     #print(order.__dict__())
     for j_order in order.__dict__():
      print(j_order)   
      json_payload = json.dumps(j_order)
      print(type(json_payload))
      order_json=json.loads(json_payload)
      order_json['source']['telegram']['channel']=''
      order_json['source']['telegram']['channel_id']=''
      
      print(f"Broadcasting the order message to client {url}")
         #json_paylod = { f''' "telegram_message": "{m_message}"'''}
         #client_parameters={"chat_id":param}
      if order.order_found:
       #x = requests.post(url, data = json_paylod)
       send_chat_message('-1001288102699-g',order_json)       
       order_json['order_closed']='N'
       fs.insert_order(order_json)
       if order_json['order']['segment'] == 'EQ':
        print("publishing message to pub/sub")   
        ps_client.publish_message('telegram_alerts',json_payload,False)
        print("successfully published message to pub/sub")
       
      #x = requests.post(url, data = json_paylod)
      #print(f"post request successfully sent to {url}")
      else:
       print("No order found")
      
     print("Inserting the message to big query")
     self.bq.insert_into_messages(order.channel,order.m_id,pd.Timestamp(message.date.strftime("%Y-%m-%d %H:%M:%S+00:00")),m_message,reply_to_msg_id,reply_to_message)
     print("inserted the message to big query") 
     return self.channel_id,message.id,pd.Timestamp(message.date.strftime("%Y-%m-%d %H:%M:%S+00:00")),m_message,reply_to_msg_id,reply_to_message
     #print(x.text)
    await client.start()
    print("client started")
    await client.run_until_disconnected()
