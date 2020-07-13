#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

from libData import *

CATEGORIES = {
  "Animaux, montures et leur équipement": "animals",
  "Équipement d'aventurier": "adventurer",
  "Hébergement et services": None,
  "Jeux": "games",
  "Moyens de transport": "transport",
  "Nourriture et Boissons": "food",
  "Outils alchimiques": "alchTools",
  "Remèdes alchimiques": "alchCures",
  "Substances et objets spéciaux": None,
  "Trousses d’outils et de compétences": "tools",
  "Vêtements": "clothes"
}


data = None
with open("../data/equipement.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

img = json.load(open('data/equipment-img.json', 'r'))

list = {}
duplicates = []
for m in data:
    if m['Nom'] in duplicates:
        print("Ignoring duplicate: " + m['Nom'])
        continue
    duplicates.append(m['Nom'])

    qData = extractQuantity(m['Nom'])
    name = qData[1]
    quantity = qData[0]
    weight = getWeight(m['Poids'])
    if weight:
      weight = round(weight / quantity, 3)
    
    if not m['Catégorie'] in list:
      list[m['Catégorie']] = []
    
    if "DescriptionHTML" in m:
      description = m['DescriptionHTML']
    elif "Description" in m:
      description = m['Description'].replace('\n','<br/>')
    else:
      description = ""
    
    el = {
        "name": name,
        "type": "loot",
        "data": {
            "description": {
                "value": ("<p><b>Prix: </b>{}<br/>" +
                        "<b>Poids: </b>{}<br/>" +
                        "<b>Catégorie: </b>{}<br/></p>" +
                        "<h2>Description:</h2><p>{}</p>" +
                        "<p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>").format(
                    m['Prix'] if 'Prix' in m else '-',
                    m['Poids'] if 'Poids' in m else '-',
                    m['Catégorie'],
                    "<div class=\"pf2frDescr\">%s</div>" % description,
                    m['Référence'])
            },
            "source": m['Source'],
            "quantity": quantity,
            "weight": weight,
            "price": getPrice(m['Prix']) if 'Prix' in m else 0,
            "identified": True,
            "carried": True,
            "equipped": False,
            "subType": "gear"
        },
        "sort": 100001,
        "flags": {},
        "img": img[m['Nom']] if m['Nom'] in img and "pf1-fr" not in img[m['Nom']] else "systems/pf1/icons/items/inventory/backpack.jpg"
    }
    
    list[m['Catégorie']].append(el)

for cat in list:
  if not cat in CATEGORIES or not CATEGORIES[cat]:
    continue;

  # écrire le résultat dans le fichier d'origine
  outFile = open("data/equip_%s.json" % CATEGORIES[cat], "w")
  outFile.write(json.dumps(list[cat], indent=3))
