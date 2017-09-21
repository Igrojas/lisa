#!/usr/bin/env python3

import os
import time
import pyperclip
import urllib.request

print("Iniciando chatbot..")
from chatbot.chatbot import Chatbot

chatbot = Chatbot()
chatbot.main(["--rootDir",".","--test", "daemon", "--modelTag", "spanish", "--keepAll"])

from vision import look
from ui import say

recent_value = ""
while True:
    tmp_value = pyperclip.paste()
    if tmp_value != recent_value:
        recent_value = tmp_value

        if "http" in recent_value:
            if "png" in recent_value or \
                    "jpg" in recent_value or \
                    "jpeg" in recent_value:

                print("Link: %s" % str(recent_value))
                filename = None
                try:
                    filename, _ = urllib.request.urlretrieve(recent_value)
                except urllib.error.HTTPError:
                    pass

                if filename != None:
                    for elem in look(filename):
                        say("Puedo ver "+elem)
                    os.remove(filename)

        else:
            if chatbot is not None:
                question = str(recent_value)
                print("Pregunta: %s" % str(question))
                answer = chatbot.daemonPredict(question)
                say("Respuesta: %s" % str(answer))

    time.sleep(1)
