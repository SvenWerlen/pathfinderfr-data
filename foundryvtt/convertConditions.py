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
  
    description = "<div class=\"pf2frDescr\">%s<p><b>Référence : </b><a href=\"%s\" parent=\"_blank\">pathfinder-fr.org</a></p></div>" % (c['DescriptionHTML'] if 'DescriptionHTML' in c else c['Description'], c['Référence'])
    description = improveDescription(description, c['Nom'])
  
    el = {
      "name": c['Nom'],
      "content": description
    }
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/conditionsfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/conditions.json", "w")
outFile.write(json.dumps(list, indent=3))