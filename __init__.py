from mycroft import MycroftSkill, intent_file_handler


class NurseAssitant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('assitant.nurse.intent')
    def handle_assitant_nurse(self, message):
        self.speak_dialog('assitant.nurse')


def create_skill():
    return NurseAssitant()

