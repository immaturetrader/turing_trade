import dill
import json
import requests
import os.path
from os import path
from turing_library.big_query_client import big_query
from turing_library.alice_blue_execution import alice_blue_execution
from turing_library.firestore_client import fire_store
from google.cloud import storage

new_dir = os.getcwd()
os.chdir(new_dir)

storage_client = storage.Client()
bucket_name='turing-trades'
source_folder='cache/broker-objects'
bucket = storage_client.bucket(bucket_name)
#source_blob_name='cache/broker-objects/626127126.alice'
destination_file_name = "cache/626127126.alice"


 


#file=open('AB126971.alice','rb')
#obj=dill.load(file)
#file.close()
alice_broker_objects={}

#fs=fire_store()
chat_id=626127126


    
class cache():
    def __init__(self):
        #bucket_name = os.environ.get('BUCKET_NAME',                               app_identity.get_default_gcs_bucket_name())
        pass

    def get_the_alice_object(self,alice_blue_auto_bot,alice_broker_objects,fs,chat_id):
           print("Getting the alice object")
           source_blob_name=f'{source_folder}/{chat_id}.alice'
           self.fs=fs
           try:   
               
             if chat_id in alice_broker_objects.keys():
               print("alice user object present")
               alice = alice_broker_objects[chat_id]
               alice.get_profile()
               return alice,alice_broker_objects
           
             #check in the gcp storage
             elif bucket.blob(source_blob_name).exists():
                alice_gcp_bytes=bucket.blob(source_blob_name).download_as_bytes() 
                alice_gcp=dill.loads(alice_gcp_bytes)
                print("trying to get profile from existing alice dill object in gcp storage")
                alice_gcp.get_profile()
                print("able to get profile from existing alice dill object in gcp storage")
                alice_broker_objects[chat_id]=alice_gcp
                return alice_gcp,alice_broker_objects            
            
#             elif path.exists(f"{chat_id}.alice"):
#                alice_file=open(f'{chat_id}.alice','rb')
#                
#                alice_dill=dill.load(alice_file)
#                alice_file.close()
#                print("trying to get profile from existing alice dill object")
#                alice_dill.get_profile()
#                print("able to get profile from existing alice dill object")
#                alice_broker_objects[chat_id]=alice_dill
#                return alice_dill,alice_broker_objects
            
             else:
               print("alice user object not present generating")
               user_details=self.fs.fetch_user_creds(chat_id)
               if self.fs.user_registered=='Y':
                print("generating client")
                alice = alice_blue_auto_bot.generate_client(username=user_details['client_id'].upper(), password=user_details['password'], twoFA=user_details['twoFA'],  api_secret=user_details['api_secret'],access_token=user_details['access_token'],app_id=user_details['app_id'],master_contracts_to_download=['NSE','NFO'])
                alice_broker_objects[chat_id]=alice
                print("added alice user object to the dict")
#                with open(f'{chat_id}.alice', 'wb') as alice_file:
#                    print("dumping the alice dill object")
#                    dill.dump(alice, alice_file)
#                    print("dumped the alice dill object successfully")
                print("adding alice user object to the dict and dumping the object to gcp")
                bucket.blob(source_blob_name).upload_from_string(data=dill.dumps(alice),content_type='application/octet-stream')        
                print("dumped alice user object to gcp")
                return alice,alice_broker_objects
               else:
                pass   
                #send_chat_message("User not registered or unable to get profile details")
           except:
               print("Unable to get profile with existing alice object")
               user_details=self.fs.fetch_user_creds(chat_id)
               if self.fs.user_registered=='Y':
                print("generating client")
                alice = alice_blue_auto_bot.generate_client(username=user_details['client_id'].upper(), password=user_details['password'], twoFA=user_details['twoFA'],  api_secret=user_details['api_secret'],access_token=user_details['access_token'],app_id=user_details['app_id'],master_contracts_to_download=['NSE','NFO'])
                print("adding alice user object to the dict and dumping the object to gcp")
#                with open(f'{chat_id}.alice', 'wb') as alice_file:
#                    print("dumping the alice dill object")
#                    dill.dump(alice, alice_file)
#                    print("dumped the alice dill object successfully")                 
                    
                bucket.blob(source_blob_name).upload_from_string(data=dill.dumps(alice),content_type='application/octet-stream')    
                print("dumped alice user object to gcp")
                alice_broker_objects[chat_id]=alice
                return alice,alice_broker_objects
               else:
                pass   
                #send_chat_message("User not registered or unable to get profile details")

#try:
#    obj.get_profile()
#except requests.exceptions.HTTPError as e:
#    err=json.loads(e.args[0])
#    print()
#    if err['message'] =='Request Unauthorised':
#        print("generating new alice object")
