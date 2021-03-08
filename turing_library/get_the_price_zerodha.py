
import json
import pandas as pd
import logging
from time import sleep
from datetime import datetime as dt
from datetime import timedelta as td
import dill

#user = json.loads(open('userzerodha.json', 'r').read().rstrip())
#userid=user['user_id']
#password=user['password']
#twofa=user['twofa']

from turing_library.big_query_client import big_query
from turing_library.alice_blue_execution import alice_blue_execution
from turing_library.firestore_client import fire_store
from turing_library.kiteext import KiteExt
from google.cloud import storage



fs=fire_store()

   

def get_broker_details(broker):
    table='broker_admin'
    docs = fs.client.collection(table).where(u'broker',u'==','zerodha').stream()
    return [doc.to_dict() for doc in docs][0]
    
def update_broker_admin_access_token(broker,access_token):
        broker='zerodha'
        table='broker_admin'
        user_docs = fs.client.collection(table).where(u'broker',u'==',broker)
        user_docs_stream = user_docs.stream()
        document_id = [doc.id for doc in user_docs_stream]
        if document_id:
            document_id = document_id[0]
            print("Updating access token")
            user_docs = fs.client.collection(table).document(f'{document_id}').update({u'enctoken':access_token})
            print("Access token updated successfully in the database")
        else:
            print("No record found in the database")
            
            
user=get_broker_details('zerodha')
kite = KiteExt()
kite.login_with_credentials(
    userid=user['client_id'], password=user['password'], twofa=user['twofa'])
print(kite.profile())
#with open(f'{userid}.kite', 'rb') as kite_file:
#   kite=dill.load(kite_file)
#   kite_file.close()
#   print(kite.profile())
#   
#with open(f'{userid}.kite', 'wb') as kite_file:
#  print("dumping the alice dill object")
#  dill.dump(kite, kite_file)
#  print("dumped the alice dill object successfully")
#  kite_file.close()
  
#print(kite.positions())
#print(kite.orders())
scrip='MCX:GOLDPETAL21MARFUT'
print(kite.ltp(scrip)['data'][scrip]['last_price'])
print(kite.ltp('NSE:HDFC'))
print(kite.ohlc("NSE:SBIN"))

# NOTE Token for AXISBANK EQ 1510401

data = kite.historical_data(1510401,dt.today() - td(days=4), dt.today(),'5minute')
df = pd.DataFrame(kite.historical_data(
    1510401, '2021-01-01', '2021-02-01', '5minute'))
print(df)
df = pd.DataFrame(kite.historical_data(
    1510401, '2020-02-01 09:15:00', '2020-02-01 15:30:00', '15minute'))
print(df)
df = pd.DataFrame(kite.historical_data(
    1510401, '2018-02-11 09:15:00', '2018-08-21 15:30:00', '30minute'))
print(df)


order_id = kite.place_order(tradingsymbol="GOLDPETAL21MARFUT",
                                exchange=kite.EXCHANGE_MCX,
                                transaction_type=kite.TRANSACTION_TYPE_BUY,
                                quantity=1,
                                order_type=kite.ORDER_TYPE_MARKET,
                                product=kite.PRODUCT_NRML,
                                variety=kite.VARIETY_REGULAR)

order_id = kite.place_order(tradingsymbol="GOLDPETAL21MARFUT",
                                exchange=kite.EXCHANGE_MCX,
                                transaction_type=kite.TRANSACTION_TYPE_SELL,
                                quantity=1,
                                order_type=kite.ORDER_TYPE_MARKET,
                                product=kite.PRODUCT_NRML,
                                variety=kite.VARIETY_REGULAR)

# KiteTicker example
'''
kws = kite.kws()


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    print("Ticks: {}".format(ticks))


def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    # Subscribe to a list of instrument_tokens (SILVERMIC 55555847 and GOLM 56513031 here).
    ws.subscribe([55555847, 56513031])

    # Set RELIANCE to tick in `full` mode.
    # Set SILVERMIC to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, [55555847])
    ws.set_mode(ws.MODE_LTP, [56513031])
    ws.set_mode(ws.MODE_QUOTE, [779521])

def on_error(ws, code, reason):
    logging.error('Ticker errored out. code = %d, reason = %s', code, reason)

def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

def on_order_update(ws, data):
    logging.info('Ticker: order update %s', data)

def stop_ticker():
    logging.info('Ticker: stopping..')
    kws.close(1000, "Manual close")

def on_max_reconnect_attempts(ws):
    logging.error('Ticker max auto reconnects attempted and giving up..')

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_order_update = on_order_update
kws.on_connect = on_connect
kws.on_close = on_close

logging.info('Ticker: Going to connect.. with threaded=True')
# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect(threaded=True)
sleep(20)
logging.info('Going to stop ticker')
stop_ticker()
'''
