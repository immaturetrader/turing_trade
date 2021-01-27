import telepot
import telegram
from flask import Flask           # import flask
import asyncio
from telethon.sync import TelegramClient,utils,events
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetChannelsRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel,InputChannel,InputPeerChannel
from telepot.aio.loop import MessageLoop
from telethon.sessions import StringSession

json_data_dir=''
# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.

global api_id
global api_hash
global phone

with open(json_data_dir+'Telegram_bot_data.json') as json_data:
     telegram_bot_data = json.load(json_data)

api_id = telegram_bot_data['api_id']  #number
api_hash = telegram_bot_data['api_hash']#string
phone = telegram_bot_data['phone']
session_string = telegram_bot_data['session_string']
token = telegram_bot_data['token']
working_dir=telegram_bot_data['working_directory']
TelegramBot = telepot.Bot(token)

async def get_channel_details():
  async with TelegramClient('sai_kiran0901_1', api_id, api_hash) as client:
   await client.connect()
   entity=await client.get_input_entity('at_test_incoming_0901')
   print(f"Channel_id: {entity.channel_id}")
   print(f"access_hash: {entity.access_hash}")
   
   


loop = asyncio.get_event_loop() 
loop.run_until_complete(get_channel_details())