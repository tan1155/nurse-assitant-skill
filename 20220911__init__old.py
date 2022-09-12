from mycroft import MycroftSkill, intent_file_handler
from mycroft.configuration import Configuration
import requests
import os
import subprocess
import time
from mycroft.util.format import nice_duration
from mycroft.util.parse import extract_datetime
from mycroft.util.time import now_local
from datetime import timedelta
from mycroft.util import record,play_wav
from os.path import exists
class NurseAssitant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.dictating = False
        self.parser = None
        self.dictation_stack = []
        self.settings.setdefault("rate", 16000)  # sample rate, hertz
        # recording channels (1 = mono)
        self.settings.setdefault("channels", 1)
        self.settings.setdefault("file_path", 'mycroft-recording.wav')
        self.settings.setdefault("duration", -1)
        
    def initialize(self):
        self.add_event('recognizer_loop:record_begin',self.handle_record)
                    
    def read_file(self, file_name):
        with self.file_system.open(file_name, "r") as my_file:
            return my_file.read()

     
    @staticmethod
    def stop_process(process):
        if process.poll() is None:  # None means still running
            process.terminate()
            return True
        else:
            return False
    
    def write_line_to_file(self, file_name, line):
        with self.file_system.open(file_name, "w") as my_file:
            my_file.writelines("%s" % place for place in line)
        
        test_file = self.read_file(file_name)
        if exists(self.settings["file_path"]):
        	test_voice_file = open(self.settings["file_path"], 'rb')
        	test_response = requests.post('http://172.24.158.178:4433/api/nlp', files={"audio_file": test_voice_file, "audio_file_name":"mycroft-recording.wav", "file_data": test_file,"file_name": file_name})
        	self.log.info(test_response.text)
        
    def handle_record(self):
        """Handler for starting a recording."""
        # Calculate how long to record
        self.start_time = now_local()
        # Extract time, if missing default to 30 seconds
        if int(self.settings["duration"]) <= 0:
            self.settings["duration"] = 60  # default recording duration


        record_for = nice_duration(self.settings["duration"],
                                       lang=self.lang)
        self.start_time = now_local()   # recalc after speaking completes
        try:
            os.remove(self.settings["file_path"])
        except Exception:
            pass
        print('record_for',int(self.settings["duration"]))
        dirname = os.getcwd()
        print('cwd',dirname)
        self.settings['file_path'] = os.path.join(dirname, 'example.wav')
        print('mycroft_recording_path',self.settings['file_path'],int(self.settings["duration"]),self.settings["rate"],self.settings["channels"])
        self.record_process = record(self.settings['file_path'],
                                         int(self.settings["duration"]),
                                         self.settings["rate"],
                                         self.settings["channels"])
        time.sleep(15)
        self.end_recording()
        print('self.record_process',self.record_process)
        
    	
    def end_recording(self):
        self.cancel_scheduled_event('RecordingFeedback')

        if self.record_process:
            # Stop recording
            self.stop_process(self.record_process)
            self.record_process = None
            # Calc actual recording duration
            self.settings["duration"] = (now_local() -
                                         self.start_time).total_seconds()

    def call_nurse(self,message):
        if self.dictating:
            self.dictating = False
            file_name = "example.txt"
            if self.file_system.exists(file_name):
            	self.file_system.open(file_name, 'r+').truncate(0)
            	self.write_line_to_file(file_name,self.dictation_stack)
            else:
            	self.write_line_to_file(file_name,self.dictation_stack)
    
    def converse(self, utterances, lang="en-us"):
        if self.dictating:
            self.log.info("Dictating: " + utterances)
            self.dictation_stack.append(utterances)
            return True
        else:
            self.remove_context("DictationKeyword")
            return False

    @intent_file_handler('assitant.nurse.intent')
    def handle_assitant_nurse(self, message):
        self.dictation_stack = []
        self.dictating = True
        self.speak_dialog('assitant.nurse')
        self.converse(message.data.get('utterance'))
        self.call_nurse(message)
def create_skill():
    return NurseAssitant()


