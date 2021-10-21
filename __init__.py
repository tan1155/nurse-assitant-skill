from mycroft import MycroftSkill, intent_file_handler
from mycroft.configuration import Configuration
import requests
from mycroft.util.format import nice_duration
from mycroft.util.parse import extract_datetime
from mycroft.util.time import now_local
from datetime import timedelta
from mycroft.util import record
class NurseAssitant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.dictating = False
        self.parser = None
        self.dictation_stack = []
        self.settings.setdefault("rate", 16000)  # sample rate, hertz
        # recording channels (1 = mono)
        self.settings.setdefault("channels", 1)
        self.settings.setdefault("file_path", "/tmp/mycroft-recording.wav")
        self.settings.setdefault("duration", -1)  
            
    def read_file(self, file_name):
        with self.file_system.open(file_name, "r") as my_file:
            return my_file.read()

     
    @staticmethod
    def stop_process(process):
        if process.poll() is None:  # None means still running
            process.terminate()
            # No good reason to wait, plus it interferes with
            # how stop button on the Mark 1 operates.
            # process.wait()
            return True
        else:
            return False
    
    def write_line_to_file(self, file_name, line):
        with self.file_system.open(file_name, "w") as my_file:
            my_file.writelines("%s" % place for place in line)
        
        test_file = self.read_file(file_name)
        test_voice_file = open(self.settings["file_path"], 'rb')
        test_response = requests.post('http://localhost:4433/api/nlp', 	files={"audio_file": test_voice_file, "audio_file_name":"mycroft-recording.wav", "file_data": test_file, "file_name": file_name})
        self.log.info(test_response.text)
        
    def handle_record(self, message):
        """Handler for starting a recording."""
        utterance = message.data.get('utterance')

        # Calculate how long to record
        self.start_time = now_local()
        # Extract time, if missing default to 30 seconds
        stop_time, _ = (
            extract_datetime(utterance, lang=self.lang) or
            (now_local() + timedelta(seconds=self.settings["duration"]), None)
        )
        self.settings["duration"] = (stop_time -
                                     self.start_time).total_seconds()
        if self.settings["duration"] <= 0:
            self.settings["duration"] = 60  # default recording duration


        record_for = nice_duration(self.settings["duration"],
                                       lang=self.lang)
        self.start_time = now_local()   # recalc after speaking completes
        try:
            os.remove(self.settings["file_path"])
        except Exception:
            pass
        self.record_process = record(self.settings["file_path"],
                                         int(self.settings["duration"]),
                                         self.settings["rate"],
                                         self.settings["channels"])
        self.end_recording()
        file_name = "example.txt"
        if self.file_system.exists(file_name):
           self.file_system.open(file_name, 'r+').truncate(0)
           self.write_line_to_file(file_name,self.dictation_stack)
        else:
           self.write_line_to_file(file_name,self.dictation_stack)

    
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
            self.handle_record(message)
    
    def converse(self, utterances, lang="en-us"):
        if self.dictating:
            self.speak("", expect_response=True)
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


