from mycroft import MycroftSkill, intent_file_handler
from mycroft.configuration import Configuration
import requests

class NurseAssitant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.dictating = False
        self.parser = None
        self.dictation_stack = []
            
    def read_file(self, file_name):
        with self.file_system.open(file_name, "r") as my_file:
            return my_file.read()

     
    def write_line_to_file(self, file_name, line):
        with self.file_system.open(file_name, "w") as my_file:
            my_file.writelines("%s" % place for place in line)
        
        test_file = self.read_file(file_name)
        test_response = requests.post('http://localhost:4433/api/nlp', files={"file_data": test_file, "file_name":file_name})
        self.log.info(test_response.text)
    
    def call_nurse(self):
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
        self.call_nurse()
def create_skill():
    return NurseAssitant()


