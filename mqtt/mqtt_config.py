# Configuration file for MQTT connection
from paho.mqtt import client as mqtt_client
import os

# Dictionary of Topics
mqTopic = {
    0 : "/heynurse//",              # No acition action required
    1 : "/heynurse/from_client/data",
    2 : "/heynurse/sms/ack",
    3 : "/heynurse/sms/send",
    4 : "/heynurse/adv_event/broadcast"
}

deviceID = {
    "device_010"        : "10",
    "device_011"        : "11",
    "smsServer"         : "11000",
    "heynurseServer"    : "10000",
    "heynurseServer2"   : "20000"
}

# Directory where the audio file from Mycroft is stored
audioFileDirectory = "$HOME/mycroft-core/skills/nurse-assitant-skill.ramya0311"

# Connection details to connect to MQTT broker
class MqttConfig:
    # Initiator
    def __init__(self):

        self.mqTopicID = 0
    
    hostName    = "localhost"
    hostIP      = "localhost"
    #hostIP      = "192.168.1.10"
    port        = 1883
#    topic       = mqTopic[self.mqTopicID]
    username    = ""
    password    = ""

# List of mycroft commands to use.
class MycroftCommand:
    askQuestion         = "sudo mycroft-speak"
    callOutToMycroft    = "sudo mycroft-say-to Christopher"

# List of question text.
class MycroftQuestion:
    qsnHelp             = "Do you need help?"
    qsnRequest          = "Are you ok in there?"

# List of action text to send to mycroft.
#class MycroftAction     = "Action"