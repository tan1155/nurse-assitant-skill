import os
import sys
import time
import json
import subprocess
import shlex
from distutils.command.config import config
from paho.mqtt import client as mqtt_client
#from flask_mqtt import Mqtt
from mqtt_config import MqttConfig as mqconfig
from mqtt_config import mqTopic, deviceID

#from flask import Flask, json, g, request, send_file, Response
#from flask_cors import CORS
#from pathlib import Path
#app = Flask(__name__)
#CORS(app)

# Setup parameters of MQTT broker/server
#varBroker = mqconfig.hostName
varBroker = mqconfig.hostIP
varPort = mqconfig.port
varServerClientID = deviceID["heynurseServer"]
topic = mqTopic[4]
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
       
        msgData = json.loads(msg.payload)

        # event_message is sent by Homepal as a mqtt message.
        # event_message = 1 means an adverse event was detected and heynurse needs to be activated.
        if msgData["event_message"] == 1:

            subprocess.call(shlex.split('mycroft-speak "Are you alright?"'))
            time.sleep(2)
            subprocess.call(shlex.split('mycroft-speak "Do you need some help?"'))
            time.sleep(3)
            subprocess.call(shlex.split('mycroft-listen'))
            time.sleep(10)
            print("finish Topic 2")
        else:
            None

    # Loop through the topic dictionary defined in the mqtt_config.py and
    # if topic is received, it will be processed.
    client.subscribe(topic)
    client.on_message = on_message

#def run():
#time.sleep(5)
client = connect_mqtt()
subscribe(client)
client.loop_forever()


#if __name__ == '__main__':
#    run()