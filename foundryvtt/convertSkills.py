#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json

from libData import *

data = None
with open("../data/competences.yml", 'r') as stream:
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
  
    description = "<p><b>Caractéristique associée:</b> %s<br/><b>Formation nécessaire:</b> %s<br/></p>" % (c['Caractéristique associée'], c['Formation nécessaire'])
    if 'DescriptionHTML' in c:
        description += "<div class=\"pf2frDescr\">%s</div>" % c['DescriptionHTML']
    else:
        description += "<p>%s</p>" % c['Description']
        print("No description found for: %s" % c['Nom'])
  
    el = {
      "name": c['Nom'],
      "content": description,
      #"img": "systems/pf1/icons/skills/affliction_01.jpg"
    }
    list.append(el)


# écrire le résultat dans le fichier d'origine
outFile = open("data/skills.json", "w")
outFile.write(json.dumps(list, indent=3))
