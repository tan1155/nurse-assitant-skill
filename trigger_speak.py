import os
import subprocess
import shlex
import time
from .mqtt_pub_from_patient_client import run

subprocess.call(shlex.split('mycroft-speak "Are you alright?"'))
time.sleep(2)
subprocess.call(shlex.split('mycroft-speak "Do you need some help?"'))
time.sleep(3)
subprocess.call(shlex.split('mycroft-listen'))
time.sleep(10)
