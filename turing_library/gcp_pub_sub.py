# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 14:20:18 2020

@author: sravula
"""
import os
from google.cloud import pubsub_v1
from turing_library.firestore_client import fire_store


new_dir = os.getcwd()
os.chdir(new_dir)

fs=fire_store()

class pub_sub():
    def __init__(self):
        self.project_id = 'boxwood-veld-298509'
        #self.topic_id='test'
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient() 

    def create_topic(self,topic_id): 
        return self.publisher.create_topic(request={"name": self.publisher.topic_path(self.project_id, topic_id)})
    
    def create_subscription_to_a_topic(self,topic_id,chat_id):
        end_point=fs.get_end_point_of_a_topic(topic_id)
        end_point=end_point+str(chat_id)
        topic_path = self.publisher.topic_path(self.project_id, topic_id)
        subscription_path = self.subscriber.subscription_path(self.project_id, topic_id + '-' + str(chat_id))
        push_config=pubsub_v1.types.PushConfig(push_endpoint=end_point)
        self.subscriber.create_subscription(
                        request={"name": subscription_path, "topic": topic_path, "push_config":push_config,"ack_deadline_seconds":240 }
                        )

        print(f"Subscription created: {subscription_path}")
        
        
    def delete_subcription_from_a_topic(self,topic_id,chat_id):
        subscription_path = self.subscriber.subscription_path(self.project_id, topic_id + '-' + str(chat_id))
        self.subscriber.delete_subscription(request={"subscription":subscription_path})
        print(f"Subscription deleted: {subscription_path}.")
 
    def publish_message(self,topic_id,message,bytes_message):
        topic_path = self.publisher.topic_path(self.project_id, topic_id)
        # Data must be a bytestring
        if not bytes_message:
         data = message.encode("utf-8")
        else:
         data = message   
        # When you publish a message, the client returns a future.
        future = self.publisher.publish(topic_path, data)
        print(future.result())
        
        
    def update_subscriptions_end_point(self,subscription_id,topic_id,endpoint) :             
        push_config = pubsub_v1.types.PushConfig(push_endpoint=endpoint) 
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(self.project_id, subscription_id)
        subscription = pubsub_v1.types.Subscription(
                name=subscription_path, topic=topic_id, push_config=push_config
                )
        update_mask = {"paths": {"push_config"}}
        with subscriber:
            result = subscriber.update_subscription(
                    request={"subscription": subscription, "update_mask": update_mask}
                    )
            print(result)
            
            



