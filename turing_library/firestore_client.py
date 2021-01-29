from google.cloud import bigquery
#from google.cloud import storage
from google.oauth2 import service_account
import cloudstorage as gcs
#from google.appengine.api import app_identity
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading
import os

new_dir = os.getcwd()
os.chdir(new_dir)

#key_path = './init_files/gcp-firestore-admin.json'
#cred = credentials.Certificate(key_path)
#firebase_admin.initialize_app(cred)
#db = firestore.client()
# https://firebase.google.com/docs/firestore/query-data/listen
def get_updates_on_doc(table_name,doc_id):
 callback_done = threading.Event()
 
 def on_snapshot(doc_snapshot, changes, read_time):
     for doc in doc_snapshot:
         print(f'Received document snapshot: {doc.to_dict()}')
     callback_done.set()
     
 doc_ref = fs.client.collection(u'open_positions').document(u'H0rCQpIabNfbHZ4aqVDY')
 doc_watch = doc_ref.on_snapshot(on_snapshot)
 
 
def get_updates_on_collection(table_name,query):
    delete_done = threading.Event()
    def on_snapshot(col_snapshot, changes, read_time):
      print(u'Callback received query snapshot.')
      #print(u'Current data: ')
      for change in changes:
         if change.type.name == 'ADDED':
             print(f'New record: {change.document.to_dict()}')
         elif change.type.name == 'MODIFIED':
             print(f'Modified record: {change.document.to_dict()}')
         elif change.type.name == 'REMOVED':
             print(f'Deleted record: {change.document.to_dict()}')
             delete_done.set()
    col_query = fs.client.collection(u'open_positions').where(u'trade_closed', u'==', u'N')  
    # Watch the collection query
    query_watch = col_query.on_snapshot(on_snapshot)      

class fire_store():

    def __init__(self):
        self.service_account_key_path = Path(__file__).parent / "init_files/gcp-firestore-admin.json"
        try:
         app = firebase_admin.get_app()
         #self.service_account_key_path = 'D:\Personal\Trading\Algo Trading\python-bot-auto-orders_optimize\init_files\gcp-big-query-admin.json'
        
         #self.service_account_key_path = 'init_files/gcp-firestore-admin.json'
        except ValueError as e:
         self.credentials = credentials.Certificate(str(self.service_account_key_path))
         firebase_admin.initialize_app(self.credentials)
        
        self.user_table = u'user_details'
        self.telegram_admin_table=u'telegram_admin'
        self.telegram_scan_channels=u'telegram_scan_channels'
        self.open_positions=u'open_positions'
        self.telegram_phone='+919502418868'
        self.client = firestore.client()
        self.chat_id = ''
        self.access_token = ''
        self.user_registered = ''
        self.chartink_scans=u'chartink_scans'
        self.pub_sub = u'pub_sub'
        print("Initialized firestore client")

    def fetch_user_creds(self,chat_id):
        self.chat_id=chat_id
        self.user_registered = 'N'
        details = ''
        print(f"getting users creds from db for chat {self.chat_id}")
        user_docs = self.client.collection(self.user_table).where(u'chat_id',u'==',self.chat_id).stream()
        #user_docs = self.client.collection(self.user_table).where(u'chat_id',u'==',626127126).stream()
        #print(user_docs)

        for doc in user_docs:
         print("got the user creds")
         self.user_registered = 'Y'
         print(f'{doc.id} => {doc.to_dict()}')
         details =  doc.to_dict()
        if self.user_registered == 'Y':
         return details
        else:
         return ''

    def register_user(self,chat_id,telegram_username,broker,client_id,password,twoFA,api_secret,access_token):
        self.fetch_user_creds(chat_id)
        if(self.user_registered=='N'):
#         user_docs = self.client.collection(self.user_table).where(u'chat_id',u'==',self.chat_id)
#         user_docs_stream = user_docs.stream()
#         document_id = [doc.id for doc in user_docs_stream]
#         if document_id:
#           document_id = document_id[0]
           user_docs = self.client.collection(self.user_table).add({u'chat_id':chat_id,u'telegram_username':telegram_username,u'broker':broker,u'client_id':client_id,u'password':password,u'twoFA':twoFA,u'api_secret':api_secret,u'access_token':access_token})
           print("User Successfully registered")
           return "User Successfully registered"

        else:
         print("User Already registered")
         return "User Already registered"

    def update_access_token(self,chat_id,access_token):
        self.chat_id=chat_id
        user_docs = self.client.collection(self.user_table).where(u'chat_id',u'==',self.chat_id)
        user_docs_stream = user_docs.stream()
        document_id = [doc.id for doc in user_docs_stream]
        if document_id:
            document_id = document_id[0]
            print("Updating access token")
            user_docs = self.client.collection(self.user_table).document(f'{document_id}').update({u'access_token':access_token})
            print("Access token updated successfully in the database")
        else:
            print("No record found in the database")

    def fetch_telegram_admin_creds(self):
        docs = self.client.collection(self.telegram_admin_table).where(u'phone',u'==',self.telegram_phone).stream()
        #docs = self.client.collection(self.telegram_admin_table).stream()
        #return [{'api_hash':doc.to_dict()['api_hash']} for doc in docs]
        return [doc.to_dict() for doc in docs][0]
#        for doc in docs:
#            print(doc.to_dict())

    def fetch_channel_details_to_be_scanned(self):
        docs = self.client.collection(self.telegram_scan_channels).where(u'scan',u'==','Y').stream()
        channel_docs = [doc.to_dict() for doc in docs]
        if channel_docs:
         return channel_docs[0]
        else:
         return


    def get_open_positions(self):
        poss=self.client.collection(self.open_positions).stream()
        #print(poss)
        positions= [pos.to_dict() for pos in poss ]
        #print(positions)
        return positions[0]
    
    

    def update_open_positions(self,chat_id,trade_closed_value):
        self.chat_id=chat_id
        user_docs = self.client.collection(self.open_positions).where(u'chat_id',u'==',self.chat_id)
        user_docs_stream = user_docs.stream()
        document_id = [doc.id for doc in user_docs_stream]
        if document_id:
            document_id = document_id[0]
            print("Updating open positions")
            user_docs = self.client.collection(self.open_positions).document(f'{document_id}').update({u'trade_closed':trade_closed_value})
            print("Updated successfully in the database")
        else:
            print("No record found in the database")
            
            
    def insert_open_positions(self,chat_id,execution_type,nse_scrip,execution_price,sl,qty):
         self.chat_id=chat_id
         user_docs = self.client.collection(self.user_table).add({u'chat_id':chat_id,u'telegram_username':telegram_username,u'broker':broker,u'client_id':client_id,u'password':password,u'twoFA':twoFA,u'api_secret':api_secret,u'access_token':access_token})

    def get_chartink_alert_data(self,alert_name):
        docs = self.client.collection(self.chartink_scans).stream()
        docs = [doc.to_dict() for doc in docs][0]
        if docs:
         return docs[alert_name]
        
        
    def get_end_point_of_a_topic(self,topic_id):
        docs = self.client.collection(self.pub_sub).stream()
        docs = [doc.to_dict() for doc in docs][0]
        print(docs)
        if docs:
         return docs[topic_id]['end_point']
        
        
        