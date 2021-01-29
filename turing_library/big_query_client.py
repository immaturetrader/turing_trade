from google.cloud import bigquery
#from google.cloud import storage
from google.oauth2 import service_account
import cloudstorage as gcs
#from google.appengine.api import app_identity
from pathlib import Path
import os

new_dir = os.getcwd()
os.chdir(new_dir)

class big_query():

    def __init__(self,chat_id):

        #self.service_account_key_path = 'D:\Personal\Trading\Algo Trading\python-bot-auto-orders_optimize\init_files\gcp-big-query-admin.json'
        self.service_account_key_path = Path(__file__).parent / "init_files/gcp-big-query-admin.json"
        #self.service_account_key_path = '.\init_files\gcp-big-query-admin.json'
        self.credentials = service_account.Credentials.from_service_account_file(str(self.service_account_key_path), scopes=["https://www.googleapis.com/auth/cloud-platform"],)
        #self.user_table = 'user_details'
        self.client = bigquery.Client(credentials=self.credentials, project=self.credentials.project_id)
        self.schema='turing_trades'
        self.user_table='user_details'
        self.telegram_channel_table='telegram_messages'
        self.chat_id = chat_id
        self.access_token = ''
        self.user_registered = ''

    def fetch_user_creds(self):
        sql = f'''select * from  `{self.credentials.project_id}.{self.schema}.{self.user_table}` where chat_id = '{self.chat_id}' '''
        #print(sql)
        query_job = self.client.query(sql)
        results = query_job.result()
        #print("User creds",results)
        #row_chat_id = [0]
        self.user_registered = 'N'
        details = ''
        for row in results:
            self.user_registered = 'Y'
            #print(row)
            details = details + ' ' + row.chat_id + ' ' + row.telegram_username + ' ' + row.broker + ' ' + row.client_id + ' ' + row.password + ' ' + row.twofa + ' ' + row.api_secret + ' ' + row.access_token
            self.telegram_username = row.telegram_username
            self.broker=row.broker
            self.client_id = row.client_id
            self.password = row.password
            self.twofa = row.twofa
            self.api_secret = row.api_secret
            self.access_token = row.access_token
        if self.user_registered == 'Y':
         return row.chat_id,row.telegram_username,row.broker,row.client_id,row.password,row.twofa,row.api_secret,row.access_token
        else:
         return []

    def register_user(self,telegram_username,broker,client_id,password,twofa,api_secret,access_token):
        self.fetch_user_creds()
        if(self.user_registered=='N'):
         insert_sql = f'''INSERT INTO `{self.credentials.project_id}.{self.schema}.{self.user_table}`(chat_id,telegram_username ,broker,client_id,password,twofa,api_secret,access_token)
         values ('{self.chat_id}','{telegram_username}','{broker}','{client_id}','{password}','{twofa}','{api_secret}','access_token');'''
         print(insert_sql)
         self.client.query(insert_sql)
         print("User Successfully registered")
         return "User Successfully registered"
        else:
         print("User Already registered")
         return "User Already registered"

    def update_access_token(self,access_token):
        update_sql = f''' UPDATE `{self.credentials.project_id}.{self.schema}.{self.user_table}` set access_token='{access_token}' where chat_id = '{self.chat_id}' '''
        print(update_sql)
        
        print("Access token updated successfully in the database")
        
        
    def fetch_max_id_of_a_channel(self,channel_id):    
        max_query = f''' select ifnull(max(m_id),0) as m_id_max from `{self.credentials.project_id}.{self.schema}.{self.telegram_channel_table}` where channel_id = '{channel_id}' '''
        return [row.m_id_max for row in self.client.query(max_query).result()][0]
    
    def insert_into_messages(self,channel_id,m_id,m_timestamp,message,reply_m_id,reply_to_message):
     insert_sql = f'''INSERT INTO `{self.credentials.project_id}.{self.schema}.{self.telegram_channel_table}`(channel_id,m_id,m_timestamp,message,reply_m_id,reply_to_message) values ('{channel_id}',{m_id},TIMESTAMP('{m_timestamp}'),'{message}','{reply_m_id}','{reply_to_message}');'''
     print(insert_sql)
     self.client.query(insert_sql)
     
     
    def insert_dataframe_into_table(self,table,df):
        df.to_gbq(f'{self.schema}.{self.telegram_channel_table}',self.credentials.project_id,chunksize=10000,if_exists='append')
        print("Dataframe data is inserted into big query table")
