#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re
import math

from libData import *

data = None
with open("../data/races.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

img = json.load(open('data/races-img.json', 'r'))

list = []
duplicates = []
for c in data:
    if c['Nom'] in duplicates:
      print("Ignoring duplicate: " + c['Nom'])
      continue
    duplicates.append(c['Nom'])
    
    descriptionHTML = "<div class=\"pf2frDescr\">"
    descriptionHTML += "<h2>Traits</h2><ul>"
    for trait in c['Traits']:
      descriptionHTML += "<li><b>%s.</b> %s</li>" % (trait['Nom'], trait['Description'])
    descriptionHTML += "</ul></div>"
    descriptionHTML = improveDescription(descriptionHTML, c['Nom'])
    
    el = {
      "name": c['Nom'],
      "type": "race",
      "data": {
        "description": {
          "value": descriptionHTML,     
          "chat": "",
          "unidentified": ""
        },
      },
      "img": img[c['Nom']] if c['Nom'] in img and "pf1-fr" not in img[c['Nom']] else "icons/svg/mystery-man.svg"
    }
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/racesfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/races.json", "w")
outFile.write(json.dumps(list, indent=3))
