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

img = json.load(open('data/skills-img.json', 'r'))

list = []
duplicates = []
for c in data:
  
    if c['Nom'] in duplicates:
      print("Ignoring duplicate: " + c['Nom'])
      continue
    duplicates.append(c['Nom'])
  
    description = "<p><b>Caractéristique associée:</b> %s<br/><b>Formation nécessaire:</b> %s<br/></p>" % (c['Caractéristique associée'], c['Formation nécessaire'])    
    description = "<div class=\"pf2frDescr\">%s<h2>Description</h2>%s<p><b>Référence: </b><a href=\"%s\" parent=\"_blank\">pathfinder-fr.org</a></p></div>" % (description, c['DescriptionHTML'] if 'DescriptionHTML' in c else c['Description'], c['Référence'])
  
    el = {
      "name": c['Nom'],
      "content": description,
      "img": img[c['Nom']] if c['Nom'] in img and "pf1-fr" not in img[c['Nom']] else "icons/svg/mystery-man.svg"
    }
    list.append(el)


# écrire le résultat dans le fichier d'origine
outFile = open("data/skills.json", "w")
outFile.write(json.dumps(list, indent=3))
