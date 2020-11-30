#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json

from libData import *

data = None
with open("../data/conditions.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

list = []
duplicates = []
for c in data:
  
    if c['Nom'] in duplicates:
      print("Ignoring duplicate: " + c['Nom'])
      continue
    duplicates.append(c['Nom'])
  
    name = c['Nom']
  
    description = generateDescriptionHTML(name, c['DescriptionHTML'] if 'DescriptionHTML' in c else c['Description'], c['Référence'])
    description = "<div class=\"condition-description\">%s</div>" % (description)  
    
    el = {
      "name": name,
      "type": "buff",
      "data": {
        "description": {
          "value": description
        },
        "buffType": "temp",
        "active": True
      }
    }
    
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/conditionsfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/conditions.json", "w")
outFile.write(json.dumps(list, indent=3))
