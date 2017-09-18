# Copyright 2017 Gustavo Grieco. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import unidecode

def clean_spanish(input_str):

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
                    words[i-1] not in ["¿","?","¡","!","!!","!!!",".", "..", "...", ","]:
                input_str = input_str.replace(word,"<nombre>")
        
        input_str = input_str.replace("<nombre> <nombre> <nombre>","<nombre>")
        input_str = input_str.replace("<nombre> <nombre>","<nombre>")

        input_str = input_str.lower()
        input_str = input_str.replace(u"\"",u"")
        input_str = input_str.replace(u"ñ",u"ni")
        input_str = input_str.replace(u"\n",u"")
        input_str = input_str.replace(u"\t",u"")

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

def normalize_spanish(input_str):
    return clean_spanish(input_str)
