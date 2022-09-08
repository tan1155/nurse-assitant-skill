import os
import sys
import time
import json
from distutils.command.config import config
import random
from paho.mqtt import client as mqtt_client
#from flask_mqtt import Mqtt
from pip import main
from .mqtt_config import MqttConfig as mqconfig
from .mqtt_config import mqTopic, deviceID
from .mqtt_pub_to_client import run as publish_msg
from .main import Main
from .messages import ErrorMessage
from .endpoints import receive_file
from .dbquery import doUpdateRequest

from flask import Flask, json, g, request, send_file, Response
from flask_cors import CORS
from pathlib import Path
app = Flask(__name__)
CORS(app)

# Setup parameters of MQTT broker/server
#varBroker = mqconfig.hostName
varBroker = mqconfig.hostIP
varPort = mqconfig.port
varServerClientID = deviceID["heynurseServer"]
# username = mqconfig.username
# password = mqconfig.password

# MQTT Connection Function
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(varServerClientID)
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(varBroker, varPort)
    return client

# Subscribe Function
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        
        # Store message into a local variable.
        # varTmpMsg = msg.payload
        print("Subscription called" + " : " + os.getcwd())
        objMain = Main()
        objErrMsg = ErrorMessage()

        # This section will handle the action the topic that was received.
        
        msgData = json.loads(msg.payload)

        if msg.topic == mqTopic[4] & msgData["ask_question"] == 1:
        # Call the functions to activate Mycroft to ask a question and then wake up Mycroft to record the reply.
            # call function in another file trigger Mycroft to ask a question and record the reply.
            # The returned status will be either:
            # 0 = Successfully recorded the message and published,
            # 1 = Failed to activate Mycroft, or failed to record the message.
            
            status = None # call the function to trigger Mycroft and replace the None with the function call

            # Publish the status in a message to be picked up by Homepal.
            print("Publish Message to Homepal")

        elif msg.topic == mqTopic[4]:
            msgData = json.loads(msg.payload)
            #print(msgData["record_objectID"])
            #print("enter topic 2")
            argUpdateString = {
                "_id" : msgData["record_objectID"],
                "req_sendSMS_status" : int(msgData["msgString"]),
                "others" : 1
            }
            #print(argUpdateString["_id"])
            varReturnUpdate = doUpdateRequest(**argUpdateString)
            print("finish Topic 2")
        else:
            None

    # Loop through the topic dictionary defined in the mqtt_config.py and
    # if topic is received, it will be processed.
    for j in mqTopic.values():
        client.subscribe(j)
        client.on_message = on_message

#def run():
#time.sleep(5)
client = connect_mqtt()
subscribe(client)
client.loop_forever()


#if __name__ == '__main__':
#    run()