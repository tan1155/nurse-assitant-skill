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
from .mqtt_pub_from_patient_client import run as publish_data
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

        self.utteranceLoopCount = 1
        self.alreadySpokenCount = False
        
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
        
        print("I got here.")

        try:
            # Publish the data to mqtt
            publish_data("example.wav",line,1)
            print("I got out of publish_data function.")
        except Exception as e:
            print("Error: ", e)
        
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
        print("Entered call_nurse().")
        if self.dictating:
            self.dictating = False
            file_name = "example.txt"
            if self.file_system.exists(file_name):
                self.file_system.open(file_name, 'r+').truncate(0)
                self.write_line_to_file(file_name,self.dictation_stack)
            else:
            	self.write_line_to_file(file_name,self.dictation_stack)

    def converse(self, utterances, lang="en-us"):
        print("Entered converse()")
        if self.dictating:
            print("self.dictating == True and utteranceLoopCount = {}".format(str(self.utteranceLoopCount)))
            print("Spoken Count = {}".format(self.alreadySpokenCount))
            self.alreadySpokenCount = False
            self.log.info("Dictating: " + utterances)
            self.dictation_stack.append(utterances)
            self.cancel_all_repeating_events()
            self.alreadySpokenCount = True # Set this flag to indicate that already spoken and no need to repeat
            return True
        else:
            print("self.dictating == False and utteranceLoopCount = {}".format(str(self.utteranceLoopCount)))
            self.remove_context("DictationKeyword")
            if self.utteranceLoopCount < 4 and not self.alreadySpokenCount: # Only trigger repeat if not user not already spoken
                print("Spoken Count Repeat = {}".format(self.alreadySpokenCount))
                #publish_data(None,None,4)
                self.utteranceLoopCount += 1
            else:
                print("Spoken Count No Repeat= {}".format(self.alreadySpokenCount))
                self.utteranceLoopCount = 1
            self.cancel_all_repeating_events()
            print("Spoken Count Before Reseet = {}".format(self.alreadySpokenCount))
            self.alreadySpokenCount = True
            print("Spoken Count After Reset= {}".format(self.alreadySpokenCount))
            return False

    @intent_file_handler('assitant.nurse.intent')
    def handle_assitant_nurse(self, message):
        self.dictation_stack = []
        self.dictating = True
        print("Before speak_dialog")
        self.speak_dialog('assitant.nurse')
        print("Before entering converse().")
        if self.converse(message.data.get('utterance')):
            print("converse() returned True")
            self.call_nurse(message)
        else:
            print("converse() returned False")
            publish_data(None,None,4)
            self.alreadySpokenCount = True
            pass

def create_skill():
    return NurseAssitant()


