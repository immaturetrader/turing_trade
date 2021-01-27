import time
from pprint import pprint
#from flask import Flask, render_template, request
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import os

#app = Flask(__name__)
credentials = GoogleCredentials.get_application_default()

service = discovery.build('compute', 'v1', credentials=credentials,cache_discovery=False)

# Project ID for this request.
project = 'boxwood-veld-298509'  # TODO: Update placeholder value.

# The name of the zone for this request.
zone = 'us-central1-a'  # TODO: Update placeholder value.

# Name of the instance resource to stop.
instance = 'debian'  # TODO: Update placeholder value.

def get_the_status_of_the_instance(project,zone,instance):
    return service.instances().get(project=project, zone=zone, instance=instance).execute()['status']

#@app.route('/start', methods=['POST'])
def start_the_instance(project,zone,instance):
  status = get_the_status_of_the_instance(project,zone,instance)
  print("Instance status ",status)
  if status == 'RUNNING':
     print("Instance is already running")
  else:
   print("Starting the instance")
   request = service.instances().start(project=project, zone=zone, instance=instance)
   response = request.execute()
   while get_the_status_of_the_instance(project,zone,instance)!='RUNNING':
     #print(response['status'])
     #request = service.instances().get(project=project, zone=zone, instance=instance)
     #response = request.execute()
     print("Current status is",get_the_status_of_the_instance(project,zone,instance))
     time.sleep(1)
   print("Instance is up and running, Current status",get_the_status_of_the_instance(project,zone,instance))
   return "Instance has started"

#@app.route('/stop', methods=['POST'])
def stop_the_instance(project,zone,instance):
  status = get_the_status_of_the_instance(project,zone,instance)
  print("Instance status ",status)
  if status == 'TERMINATED':
     print("Instance is already stopped")
  else:
   print("Stopping the instance")
   request = service.instances().stop(project=project, zone=zone, instance=instance)
   response = request.execute()
   while get_the_status_of_the_instance(project,zone,instance)!='TERMINATED':
     #print(response['status'])
     #request = service.instances().get(project=project, zone=zone, instance=instance)
     #response = request.execute()
     print("Current status is",get_the_status_of_the_instance(project,zone,instance))
     time.sleep(3)
   print("Instance is terminated successfully, Current status",get_the_status_of_the_instance(project,zone,instance))
   return "Instance has stopped"

def main():
 #server_port = os.environ.get('PORT', '8080')
 #app.run(debug=False, port=server_port, host='0.0.0.0')
 #print("starting")
 start_the_instance(project,zone,instance)

#main()
