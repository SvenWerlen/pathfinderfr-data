#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import locale

from libData import *

data = None
with open("../data/magic-armures.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


list = []
duplicates = []
locale.setlocale(locale.LC_ALL, '')
for w in data:
  
    if w['Nom'] in duplicates:
      print("Ignoring duplicate: " + w['Nom'])
      continue
    duplicates.append(w['Nom'])
  
    description = "<p>"
    if 'Résumé' in w:
        description += "<b>Résumé:</b> %s<br/>" % w['Résumé']
    if 'Prix' in w:
        description += "<b>Prix:</b> %s<br/>" % "{0:n} po".format(w['Prix'])
    if 'PrixModif' in w:
        description += "<b>Modificateur au prix:</b> %s<br/>" % w['PrixModif']
    if 'Source' in w:
        description += "<b>Source:</b> %s<br/>" % w['Source']
    description += "</p>"
    
    description = "<div class=\"pf2frDescr\">%s<h2>Description</h2>%s<p><b>Référence: </b><a href=\"%s\" parent=\"_blank\">pathfinder-fr.org</a></p></div>" % (description, w['DescriptionHTML'] if 'DescriptionHTML' in w else w['Description'], w['Référence'])
    description = improveDescription(description, w['Nom'])
  
    el = {
      "name": w['Nom'],
      "content": description,
      #"img": "systems/pf1/icons/skills/affliction_01.jpg"
    }
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/magic_armorsfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/magic_armors.json", "w")
outFile.write(json.dumps(list, indent=3))
