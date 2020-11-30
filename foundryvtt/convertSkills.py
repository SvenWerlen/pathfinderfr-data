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
  
    name = c['Nom']
    
    infos = "<p><b>Caractéristique associée : </b>%s<br/><b>Formation nécessaire : </b>%s<br/></p>" % (c['Caractéristique associée'], c['Formation nécessaire'])  
    description = generateDescriptionHTML(name, c['DescriptionHTML'] if 'DescriptionHTML' in c else c['Description'], c['Référence'])
    description = "<div class=\"skill-description\">%s<h2>Description</h2>%s</div>" % (infos, description)
    
    el = {
      "name": name,
      "content": description,
    }
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/skillsfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/skills.json", "w")
outFile.write(json.dumps(list, indent=3))
