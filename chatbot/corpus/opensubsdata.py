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

    transcript_table = { # TODO: refactor this table as an external file
        "sois":"sos", #son
        "os":"", #se le les
        "seais":"sean",
        "esteis":"esten",
        "vais":"van",
        "debeis":"deben",

        "vosotros":"ustedes",
        "vuestras":"sus",
        "vuestros":"sus",
        "vuestra":"su",
        "vuestro":"su",

        "podriais":"podrian",
        "rogareis":"rogaran",
        "llevareis":"llevaran",

        "teneis":"tenes",#tienen
        "podeis":"pueden",
        "porteis":"porten",
        "mereceis":"merecen",
        "preocupeis":"preocupen",
        "escogisteis":"escogiste",
        "veis":"ven",
        "sabeis":"saben",
        "ois":"oyen",
        "visteis":"vieron",
        "enganieis":"enganien",
        "creeis":"creen",
        "habeis":"han",
        "haceis":"hacen",
        "hicisteis":"hicieron",
        "dejeis":"dejen",
        "olvidais":"olvidan",
        "quereis":"quieren",
        "entendeis":"entienden",
        "dejasteis":"dejan",
        "hableis":"hablen",
        "alboroteis":"alboroten",
        "encontrasteis":"encontraron",
        "oleis":"huelen",
        "toqueis":"toquen",
        "ocupasteis":"ocupan",
        "fallareis":"fallaran",
        "lleveis":"lleven",
        "conocisteis":"conocieron",
        "acepteis":"acepten",
        "porteis":"porten",
        "tendreis":"tendran",
        "alejaos":"alejense",
        "mireis":"miren",
        "estuvisteis":"estuviste",
        "volvereis":"volveras",
        "salisteis":"salieron",
        "defendisteis":"defendieron",
        "baileis":"bailen",
        "busqueis":"busquen",
        "creereis":"creeras",
        "necesitareis":"necesitaran",
        "desangreis":"desangre",
        "podreis":"podran",
        "salvasteis":"salvaste",
        "hablasteis":"hablaste",
        "deciros":"decirles",
        "bajeis":"bajen",
        "escoltareis":"escoltaran",
        "custodiareis":"custodiaran",
        "caisteis":"caiste",
        "tuvisteis":"tuviste",
        "llevasteis":"llevaron",
        "jodeis":"joden",
        "recordareis":"recordaras",
        "tomareis":"tomaras",
        "viajeis":"viajen",
        "alejeis":"alejen",
        "uniros":"unirse",
        "perecereis":"pereceran",
        "sereis":"seran",
        "temeis":"temen",
        "marcheis":"marchen",
        "empeceis":"empieces",
        "salisteis":"salieron",
        "estareis":"estaran",
        "sobrevivireis":"sobreviviran",
        "conoceis":"conoces",
        "vinisteis":"viniste",
        "disculpeis":"disculpe",
        "querreis":"querran",
        "trateis":"traten",
        "perdereis":"perderan",
        "oireis":"oiras",
        "dijisteis":"dijiste",
        "contareis":"contaras",
        "juzgueis":"juzgues",
        "mostrareis":"mostraran",
        "acerqueis":"acerquen",
        "perdoneis":"perdonen",
        "coincidireis":"coincidiran",
        "aplazasteis":"aplazaron",
        "aprendereis":"aprenderas",
        "probeis":"pruebes",
        "mateis":"maten",
        "informeis":"informes",
        "atreveis":"atrevan",
        "vivais":"vivan",
        "murais":"mueran",
        "debereis":"deberan",
        "traeis":"traes",
        "hareis":"haras",
        "espereis":"esperen",
        "conoceis":"conocen",
        "guardeis":"guardes",
        "conoceis":"conoces",
        "perdereis":"perderas",
        "reireis":"reiran",
        "burlareis":"burlaran",
        "asusteis":"asusten",
        "dijisteis":"dijiste",
        "ireis":"iran",
        "espereis":"esperen",
        "dispareis":"disparen",
        "anulasteis":"anulaste",
        "atascasteis":"atascaste",
        "dareis":"daran",
        "useis":"uses",
        "encontreis":"encuentres",
        "ayudareis":"ayudaran",
        "recogeis":"recoges",
        "matasteis":"mataste",
        "sosteneis":"sostienes",
        "perdeis":"pierdes",
        "cumplis":"cumples",
        "perdonareis":"perdonen",
        "vereis":"veras",
        "compreis":"compres",
        "volveis":"vuelves",
        "topasteis":"topaste",
        "abandonasteis":"abandonaste",
        "estais":"estan",
        "desenganchasteis":"desengancharon",
        "moveis":"mueven",
        "cogeis":"toman",
        "sacasteis":"sacaste",
        "trabajasteis":"trabajaste",
        "fuisteis":"fuiste",
        "traicionasteis":"traicionaste",
        "empezareis":"empezaras",
        "tomeis":"tomes",
        "pensareis":"pensaras",
        "decis":"dices",
        "trajisteis":"trajiste",
        "entrareis":"entraran",
        "poneis":"pones",
        "completeis":"completes",
        "trabajais":"trabajan",
        "pareceis":"parecen",
        "peleasteis":"pelearon",
        "cruceis":"cruces",
        "vierais":"vieran",
        "comeis":"comen",
        "habreis":"habran",
        "poneros":"ponerse",
        "pedisteis":"pediste",
        "tardeis":"tardes",
        "limpieis":"limpien",
        "pareceis":"parecen",
        "corteis":"corten",
        "enjabonaos":"enjabonense",
        "pareceis":"pareces",
        "sabreis":"sabran",
        "olvideis":"olviden",
        "tengais":"tengas",
        "entendereis":"entenderas",
        "entreis":"entres",
        "valeis":"vales",
        "pareceis":"parecen",
        "dejaos":"dejense",
        "tomasteis":"tomaste",
        "solucioneis":"soluciones",
        "cerrad":"cierra",
        "olvideis":"olviden",
        "deis":"des",
        "enviareis":"enviaras",
        "asegureis":"aseguren",
        "fueseis":"fueras",
        "rompisteis":"rompieron",
        "volvisteis":"volvieron",
        "leeis":"leen",
        "intenteis":"intenten",
        "desveleis":"desvelen",
        "subestimeis":"subestimes",
        "llameis":"llames",
        "morireis":"",
        }

    names = set()

    def normalize(self, input_str):

        input_str = " "+input_str
        #print("normalizing")

        #parad (palabras en imperativo que terminan en -ad, -ed -id)

        #if " teneis " in input_str:
        #    print(input_str)

        words = self.transcript_table.keys()
        for word in words:
            to_replace = " "+self.transcript_table[word]+" "
            word = " "+word+" "
            if word in input_str:
                #print(input_str)
                input_str = input_str.replace(word,to_replace)
                #print(input_str)
        #if "rad " in input_str:
        #    print(input_str)
        if "ois " in input_str:
            print(input_str)
        if "eis " in input_str and " seis" not in input_str:
            print(input_str)

        return input_str[1:]

    def clean(self, input_str):

        if ":" in input_str:
            return ""

        if "'" in input_str:
            return ""

        if "\"" in input_str:
            return ""

        if "--" in input_str:
            return ""

        if "{" in input_str or "}" in input_str:
            return ""

        if "[" in input_str or "]" in input_str:
            return ""

        if "&" in input_str:
            return ""

        if "|" in input_str:
            return ""

        if " i " in input_str:
            return ""

        input_str = input_str.replace("-",".")

        words = input_str.replace("-","").split(" ")
        words = list(filter(lambda x: not (x==''), words))
        for i,word in enumerate(words):

            if i == 0:
                continue

            if word[0].isupper() and \
                    (word in self.names or words[i-1] \
                    not in ["¿","?","¡","!","!!","!!!",".", "..", "...", ","]):
                #if word == "Es":
                #    print(input_str)
                #self.names.add(word)
                input_str = input_str.replace(word,"$nombre$")
                #print(self.names)
                #print("name?",word)
        
        input_str = input_str.replace("$nombre$ $nombre$ $nombre$","$nombre$")
        input_str = input_str.replace("$nombre$ $nombre$","$nombre$")

        input_str = input_str.lower()
        input_str = input_str.replace(u"\"",u"")
        input_str = input_str.replace(u"ñ",u"ni")

        input_str = input_str.replace(u"¿",u"")
        input_str = input_str.replace(u"¡",u"")
        input_str = input_str.replace(u"....",u"")
        input_str = input_str.replace(u"...",u"")
        input_str = input_str.replace(u"..",u"")
        #input_str = input_str.replace(u"-",u"")
        #input_str = input_str.replace(u"&",u"")
        input_str = input_str.replace(u"*",u"")
        input_str = input_str.replace(u"_",u"")

        input_str = unidecode.unidecode(input_str)
        if input_str != '' and input_str[-1] == ".":
            input_str = input_str[:-1]

        #print(input_str)
        return input_str

    def getLine(self, sentence):
        line = {}
        sentence = self.clean(sentence)
        sentence = self.normalize(sentence)
       
        line["text"] = self.tag_re.sub('', sentence).replace('\\\'','\'').strip()

        return line

    def filter(self, lines):
        first  = lines["lines"][0]["text"].replace(" ","").replace(".","")
        second = lines["lines"][1]["text"].replace(" ","").replace(".","")
        assert(len(lines["lines"]) == 2)

        if len(set(first)) <= 1 or len(set(second)) <= 1:
            return False
        """
        if "/" in first or "/" in second:
            #print(first)
            #print(second)
            return False

        if ":" in first or ":" in second:
            return False

        if "[" in first or "[" in second:
            return False

        if "{" in first or "{" in second:
            return False

        if "'" in first or "'" in second:
            return False

        if "\"" in first or "\"" in second:
            return False

        if "traduc" in first or "traduc" in second:
            return False

        if "transla" in first or "transla" in second:
            return False
        """
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
