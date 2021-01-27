from google.cloud import bigquery
#from google.cloud import storage
from google.oauth2 import service_account
import cloudstorage as gcs
#from google.appengine.api import app_identity
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#key_path = './init_files/gcp-firestore-admin.json'
#cred = credentials.Certificate(key_path)
#firebase_admin.initialize_app(cred)
#db = firestore.client()

class fire_store():

    def __init__(self):

        #self.service_account_key_path = 'D:\Personal\Trading\Algo Trading\python-bot-auto-orders_optimize\init_files\gcp-big-query-admin.json'
        self.service_account_key_path = Path(__file__).parent / "init_files/gcp-firestore-admin.json"
        #self.service_account_key_path = 'init_files/gcp-firestore-admin.json'
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
