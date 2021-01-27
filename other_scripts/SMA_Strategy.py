yesimport logging
import datetime
import statistics
from time import sleep
from alice_blue import *
import json
import pandas as pd

# Config
username = 'username'
password = 'password'
api_secret = 'api_secret'
twoFA = 'twoFA'
EMA_CROSS_SCRIP = 'SBIN'
logging.basicConfig(level=logging.ERROR)        # Optional for getting debug messages.
# Config

ltp = 0
socket_opened = False
alice = None
json_data_dir=''

def event_handler_quote_update(message):
    global ltp
    ltp = message['ltp']
    print(message)

def open_callback():
    global socket_opened
    socket_opened = True

def buy_signal(ins_scrip):
    global alice
    alice.place_order(transaction_type = TransactionType.Buy,
                         instrument = ins_scrip,
                         quantity = 1,
                         order_type = OrderType.Market,
                         product_type = ProductType.Intraday,
                         price = 0.0,
                         trigger_price = None,
                         stop_loss = None,
                         square_off = None,
                         trailing_sl = None,
                         is_amo = False)

def sell_signal(ins_scrip):
    global alice
    alice.place_order(transaction_type = TransactionType.Sell,
                         instrument = ins_scrip,
                         quantity = 1,
                         order_type = OrderType.Market,
                         product_type = ProductType.Intraday,
                         price = 0.0,
                         trigger_price = None,
                         stop_loss = None,
                         square_off = None,
                         trailing_sl = None,
                         is_amo = False)

def init_alice_blue():
 with open(json_data_dir+'alice_blue_bot_data.json') as json_data:
     alice_blue_bot_data = json.load(json_data)    
 global alice
 global socket_opened
 try:
  alice = AliceBlue(username=alice_blue_bot_data['username'], password=alice_blue_bot_data['password'], access_token=alice_blue_bot_data['access_token'])
  socket_opened = False
  alice.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      run_in_background=True)
 except: 
  print("Unable to login using the current access token, regenerating new one")   
  generate_access_token()
  with open(json_data_dir+'alice_blue_bot_data.json') as json_data:
     alice_blue_bot_data = json.load(json_data)  
     alice = AliceBlue(username=alice_blue_bot_data['username'], password=alice_blue_bot_data['password'], access_token=alice_blue_bot_data['access_token'])
  print("Alice blue object",alice)
  socket_opened = False
  alice.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      run_in_background=True)

    
def main():
    global socket_opened
    global alice
    global username
    global password
    global twoFA
    global api_secret
    global EMA_CROSS_SCRIP
    init_alice_blue()
    minute_close = []
    df=pd.DataFrame(columns=['timestamp','price'])
    csv=pd.read_csv('SBIN_1_min_tick_data.csv')
    df=df.append(csv)
    print(alice.get_balance()) # get balance / margin limits
    print(alice.get_profile()) # get profile
    print(alice.get_daywise_positions()) # get daywise positions
    print(alice.get_netwise_positions()) # get netwise positions
    print(alice.get_holding_positions()) # get holding positions
    
    ins_scrip = alice.get_instrument_by_symbol('NSE', EMA_CROSS_SCRIP)
    
    socket_opened = False
    alice.start_websocket(subscribe_callback=event_handler_quote_update,
                          socket_open_callback=open_callback,
                          run_in_background=True)
    while(socket_opened==False):    # wait till socket open & then subscribe
        pass
    alice.subscribe(alice.get_instrument_by_symbol('NSE', EMA_CROSS_SCRIP), LiveFeedType.COMPACT)
    write_index=0
    while True:
        if(datetime.datetime.now().second == 0):
            minute_close.append(ltp)
            print("minute end close price",ltp) #Just added this line so that you know that it is fetching the LTP.
            df.loc[write_index]= datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),ltp
            write_index+=1
            if(len(minute_close) > 20):
                sma_5 = statistics.mean(minute_close[-5:])
                sma_20 = statistics.mean(minute_close[-20:])
                if(sma_5 > sma_20):
                    buy_signal(ins_scrip)
                elif(sma_5 < sma_20):
                    sell_signal(ins_scrip)
            sleep(1)
            df.to_csv('SBIN_1_min_tick_data.csv',index=None)
        sleep(0.2)  # sleep for 200ms
    
if(__name__ == '__main__'):
    main()