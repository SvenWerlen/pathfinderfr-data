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
    
    name = c['Nom']
    
    traits = "<ul>"
    for trait in c['Traits']:
      traits += "<li><b>%s.</b> %s</li>" % (trait['Nom'], trait['Description'])
    traits += "</ul>"
    
    el = {
      "name": name,
      "type": "race",
      "data": {
        "description": {
          "value": "<div class=\"race-description\"><h2>Traits</h2>%s</div>" % 
              generateDescriptionHTML(name, traits, c['Référence']),     
          "chat": "",
          "unidentified": ""
        },
      },
      "img": img[name] if name in img and "pf1-fr" not in img[name] else "icons/svg/mystery-man.svg"
    }
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/racesfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/races.json", "w")
outFile.write(json.dumps(list, indent=3))
