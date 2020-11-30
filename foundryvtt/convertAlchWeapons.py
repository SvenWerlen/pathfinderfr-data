#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

from libData import *

data = None
with open("../data/armes-alchimiques.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

def getCritRange(crit):
    m = re.search('(\d\d)-20/×', crit)
    if m:
        return m.group(1)
    return "20"

def getCritMult(crit):
    m = re.search('×(\d)', crit)
    if m:
        return m.group(1)
    return "2"

def getRange(range):
    m = re.search('(\d+) m', range)
    if m:
        return int(m.group(1))
    return None

def getType(type):
    return "simple"


list = []
duplicates = []
for w in data:
    if w['Nom'] in duplicates:
        print("Ignoring duplicate: " + w['Nom'])
        continue
    duplicates.append(w['Nom'])
    
    qData = extractQuantity(w['Nom'])
    name = qData[1]
    quantity = qData[0]
    weight = getWeight(w['Poids'])
    if weight:
      weight = round(weight / quantity, 3)
    
    if "DescriptionHTML" in w:
      description = w['DescriptionHTML']
    elif "Description" in w:
      description = w['Description'].replace('\n','<br/>')
    else:
      description = ""
    description = generateDescriptionHTML(name, description, w['Référence'])
    
    el = {
      "name": name,
      "type": "weapon",
      "data": {
          "description": {
              "value": ("<div class=\"equip-description\"><p>" +
                          generateProp("Catégorie", w, 'Catégorie', "-") + 
                          generateProp("Sous-catégorie", w, 'Sous-catégorie', "-") + 
                          generateProp("Artisanat", w, 'Artisanat') + 
                          "<b>Prix : </b>{}, <b>Poids : </b>{}<br/>" +
                          generateProp("Dégâts", w, 'Dégâts') + 
                          generateProp("Critique", w, 'Critique') + 
                          generateProp("Portée", w, 'Portée') + 
                          generateProp("Type", w, 'Type') + 
                          generateProp("Spécial", w, 'Spécial') + 
                          "</p><h2>Description</h2>{}" +
                          "</div>").format(
                      w['Prix'] if 'Prix' in w else '-',
                      w['Poids'] if 'Poids' in w else '-',
                      description)
          },
          "source": w['Source'],
          "quantity": quantity,
          "weight": weight,
          "price": getPrice(w['Prix']),
          "identified": True,
          "carried": True,
          "equipped": True,
          "masterwork": False,
          "weaponType": getType(w['Catégorie']), 
          "enh": "",
          "weaponData": {
              "damageRoll": w['Dégâts'],
              "damageType": w['Type'],
              "critRange":  getCritRange(w['Critique']),
              "critMult": getCritMult(w['Critique']),
              "isMelee": (w['Portée'] == "—"),
              "range": getRange(w['Portée']),
          }
      },
#      "img": img[w['Nom']] if w['Nom'] in img and "pf1-fr" not in img[w['Nom']] else "systems/pf1/icons/items/weapons/quarterstaff.png"
    }
    
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/weaponsAlchfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/weaponsAlch.json", "w")
outFile.write(json.dumps(list, indent=3))
