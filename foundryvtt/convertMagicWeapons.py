#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import locale

from libData import *

data = None
with open("../data/magic-armes.yml", 'r') as stream:
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
  
    name = w['Nom']
  
    infos = "<p>"
    if 'Résumé' in w:
        infos += "<b>Résumé : </b> %s<br/>" % w['Résumé']
    if 'Prix' in w:
        infos += "<b>Prix : </b> %s<br/>" % "{0:n} po".format(w['Prix'])
    if 'PrixModif' in w:
        infos += "<b>Modificateur au prix : </b>%s<br/>" % w['PrixModif']
    if 'Source' in w:
        infos += "<b>Source : </b>%s<br/>" % w['Source']
    infos += "</p>"
    
    description = generateDescriptionHTML(name, w['DescriptionHTML'] if 'DescriptionHTML' in w else w['Description'], w['Référence'])
    description = "<div class=\"magic-description\">%s<h2>Description</h2>%s</div>" % (infos, description)
  
    el = {
      "name": name,
      "content": description,
      #"img": "systems/pf1/icons/skills/affliction_01.jpg"
    }
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/magic_weaponsfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/magic_weapons.json", "w")
outFile.write(json.dumps(list, indent=3))
