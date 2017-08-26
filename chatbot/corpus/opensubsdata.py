# -*- coding: utf-8 -*-
# Based on code from https://github.com/AlJohri/OpenSubtitles
# by Al Johri <al.johri@gmail.com>

import xml.etree.ElementTree as ET
import datetime
import os
import sys
import json
import re
import pprint
import unidecode

from gzip import GzipFile
from tqdm import tqdm

"""
Load the opensubtitles dialog corpus.
"""

class OpensubsData:
    """

    """

    def __init__(self, dirName):
        """
        Args:
            dirName (string): directory where to load the corpus
        """

        # Hack this to filter on subset of Opensubtitles
        # dirName = "%s/en/Action" % dirName

        print("Loading OpenSubtitles conversations in %s." % dirName)
        self.conversations = []
        self.tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
        self.conversations = self.loadConversations(dirName)

    def loadConversations(self, dirName):
        """
        Args:
            dirName (str): folder to load
        Return:
            array(question, answer): the extracted QA pairs
        """
        conversations = []
        dirList = self.filesInDir(dirName)
        for filepath in tqdm(dirList, "OpenSubtitles data files"):
            if filepath.endswith('gz'):
                try:
                    doc = self.getXML(filepath)
                    conversations.extend(self.genList(doc))
                except ValueError:
                    tqdm.write("Skipping file %s with errors." % filepath)
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
        return conversations

    def getConversations(self):
        return self.conversations

    def genList(self, tree):
        root = tree.getroot()

        timeFormat = '%H:%M:%S'
        maxDelta = datetime.timedelta(seconds=1)

        startTime = datetime.datetime.min
        strbuf = ''
        sentList = []

        for child in root:
            for elem in child:
                if elem.tag == 'time':
                    elemID = elem.attrib['id']
                    elemVal = elem.attrib['value'][:-4]
                    if elemID[-1] == 'S':
                        startTime = datetime.datetime.strptime(elemVal, timeFormat)
                    else:
                        sentList.append((strbuf.strip(), startTime, datetime.datetime.strptime(elemVal, timeFormat)))
                        strbuf = ''
                else:
                    try:
                        strbuf = strbuf + " " + elem.text
                    except:
                        pass

        conversations = []
        for idx in range(0, len(sentList) - 1):
            cur = sentList[idx]
            nxt = sentList[idx + 1]
            if nxt[1] - cur[2] <= maxDelta and cur and nxt:
                tmp = {}
                tmp["lines"] = []
                tmp["lines"].append(self.getLine(cur[0]))
                tmp["lines"].append(self.getLine(nxt[0]))
                if self.filter(tmp):
                    conversations.append(tmp)

        new_conversations = []
        for i,line in enumerate(conversations):
            if i > 0 and conversations[i-1] == line:
                #print line, conversations[i-1]
                continue

            new_conversations.append(line)

        return new_conversations

    def clean(self, input_str):
        input_str = input_str.lower()
        input_str = input_str.replace(u"\"",u"")
        input_str = input_str.replace(u"ñ",u"ni")

        input_str = input_str.replace(u"¿",u"")
        input_str = input_str.replace(u"¡",u"")
        input_str = input_str.replace(u"....",u"")
        input_str = input_str.replace(u"...",u"")
        input_str = input_str.replace(u"..",u"")
        input_str = input_str.replace(u"-",u"")
        input_str = input_str.replace(u"&",u"")
        input_str = input_str.replace(u"*",u"")

        input_str = unidecode.unidecode(input_str)
        if input_str != '' and input_str[-1] == ".":
            input_str = input_str[:-1]

        return input_str

    def getLine(self, sentence):
        line = {}
        sentence = self.clean(sentence)
        line["text"] = self.tag_re.sub('', sentence).replace('\\\'','\'').strip()

        return line

    def filter(self, lines):
        first  = lines["lines"][0]["text"].replace(" ","").replace(".","")
        second = lines["lines"][1]["text"].replace(" ","").replace(".","")

        if len(set(first)) <= 1 or len(set(second)) <= 1:
            return False

        if ":" in first or ":" in second:
            return False

        if "[" in first or "[" in second:
            return False

        if "{" in first or "{" in second:
            return False

        if "traduc" in first or "traduc" in second:
            return False

        if "transla" in first or "transla" in second:
            return False

        # Use the followint to customize filtering of QA pairs
        #
        # startwords = ("what", "how", "when", "why", "where", "do", "did", "is", "are", "can", "could", "would", "will")
        # question = lines["lines"][0]["text"]
        # if not question.endswith('?'):
        #     return False
        # if not question.split(' ')[0] in startwords:
        #     return False
        #
        return True

    def getXML(self, filepath):
        fext = os.path.splitext(filepath)[1]
        if fext == '.gz':
            tmp = GzipFile(filename=filepath)
            return ET.parse(tmp)
        else:
            return ET.parse(filepath)

    def filesInDir(self, dirname):
        result = []
        for dirpath, dirs, files in os.walk(dirname):
            for filename in files:
                fname = os.path.join(dirpath, filename)
                result.append(fname)
        return result
