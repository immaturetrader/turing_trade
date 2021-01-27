# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 23:40:26 2020

@author: sravula
"""

#import sqlite3 as lite
import pandas as pd
import os
import time
import json
import telepot
from telethon.sessions import StringSession
import asyncio
from telethon.sync import TelegramClient,events
import requests
import sys
from google.cloud import bigquery
from google.oauth2 import service_account
import datetime
import time
from turing_library.firestore_client import fire_store
from turing_library.big_query_client import big_query
from turing_library.scan_telegram import scan_telegram_channel

channel=sys.argv[1]
scan_telegram_c = scan_telegram_channel(channel)         
def start_scanning():
    
    if scan_telegram_c.channel_id:
     print(f"Listening to the channnel {scan_telegram_c.channel_id}")
     loop = asyncio.get_event_loop() 
     print("Syncing the database with old telegram messages")
     loop.run_until_complete(scan_telegram_c.get_telegram_channel_data())
     print("Syncing the database done")
     new_message=loop.run_until_complete(scan_telegram_c.get_new_messages_on_events())
     print(new_message)
     print("sleeping")
     time.sleep(5)
    else:
     print("No channel to scan, existing the program")
     sys.exit()

      
if __name__ == '__main__':
    start_scanning()