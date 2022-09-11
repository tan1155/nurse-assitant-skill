import os
import time
import wave
import json
import base64
import subprocess
from paho.mqtt import client as mqtt_client
from .mqtt_config import MqttConfig as mqconfig
from .mqtt_config import mqTopic, deviceID, audioFileDirectory, messageFileDirectory

# Setup parameters of MQTT broker/server
#broker = mqconfig.hostName
broker = mqconfig.hostIP
port = mqconfig.port
topic = mqTopic[1]
client_id = deviceID["device_010"]

# Here's the audio text string to be passed.
#request_string = "i am bleeding"

# Only use these variables if we are securing the transfer data.
# username = 'emqx'
# password = 'public'


# MQTT Connection Function
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
#    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# Publish Message Function
def publish(client, fileName, messageText):
    # Save the current working directory to reset the CWD after reading the file.
    savedCWD = os.getcwd()

    # Change directory to pick up the audio file and change back to current working directory
    os.chdir(audioFileDirectory)

    msg_count = 0
    while True:
        if msg_count == 1:
            break
        time.sleep(3)

        print("before opening audio file to read  " + fileName + " : " + messageText)

        with wave.open("{}/{}".format(audioFileDirectory, fileName), "rb") as objWavFile:    # Open WAV file in read-only mode.
            # Get basic information.
            n_channels      = objWavFile.getnchannels() # Number of channels. (1=Mono, 2=Stereo)
            sample_width    = objWavFile.getsampwidth() # Sample width in bytes
            framerate       = objWavFile.getframerate() # Frame rate
            n_frames        = objWavFile.getnframes()   # Number of frames
            comp_type       = objWavFile.getcomptype()  # Compression type (only supports "NONE")
            comp_name       = objWavFile.getcompname()  # Compression name
            
            frames          = objWavFile.readframes(n_frames)
            
            print("{} : {}".format(str(len(frames)),str(sample_width * n_frames)))
            #assert len(frames) == sample_width * n_frames

        wave.Wave_read.close

        msg =   {
                'frames': str(base64.b64encode(frames),'utf-8'),
                'client_id': client_id,
                'request_string': str(messageText),
                'n_channels': str(n_channels),
                'sample_width': str(sample_width),
                'framerate': str(framerate),
                'n_frames': str(n_frames),
                'comp_type': comp_type,
                'comp_name': comp_name,
                }

        msg_out = json.dumps(msg)

        print("before publishing to mqtt broker")
        
        result = client.publish(topic, msg_out, 0, False)
        # result: [0, 1]
        status = result[0]
#        if status == 0:
#            print(f"Send `{msg}` to topic `{topic}`")
#        else:
#            print(f"Failed to send message to topic {topic}")
        msg_count += 1

        print("after publishing to MQTT broker")

        subprocess.call(shlex.split('rm -rf example.wav'))

    os.chdir(savedCWD)

# Entry Point for Publishing
def run(paramFilepath, paramMessageText):
    client = connect_mqtt()
    client.loop_start()
    try:
        publish(client, paramFilepath, paramMessageText)
        #client.disconnect
    except Exception as e:
        print("Error: ", e)
        #client.disconnect
    return
   


#if __name__ == '__main__':
#    run()