# -*- coding: utf-8 -*-
import unicodedata
from naoqi import ALProxy


stop = False


### USING NAOQI API
class Robot():
    def __init__(self, ip, port, name):
        ip = unicodedata.normalize('NFKD', ip).encode('ascii', 'ignore')
        PORT = int(port)
        self.name = name
        try:
            self.tts = ALProxy("ALTextToSpeech", ip, PORT)
            self.pos = ALProxy("ALRobotPosture", ip, PORT)
            self.mot = ALProxy("ALMotion", ip, PORT)
            self.memory = ALProxy("ALMemory",ip, PORT)
            self.sonar = ALProxy("ALSonar", ip , PORT)
            self.motion = ALProxy("ALMotion", ip, PORT)
        except Exception, e:
            print "Could not init robot"
            print "Error was: ", e
            raise Exception
