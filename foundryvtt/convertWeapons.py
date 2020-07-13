#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

from libData import *

data = None
with open("../data/armes.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

img = json.load(open('data/weapons-img.json', 'r'))

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
    if type == "Arme courante": 
        return "simple"
    elif type == "Arme de guerre":
        return "martial"
    elif type == "Arme exotique":
        return "exotic"
    else:
        return None


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
    
    el = {
      "name": name,
      "type": "weapon",
      "data": {
          "description": {
              "value": ("<p><b>Catégorie: </b>{}<br/>" +
                          "<b>Sous-catégorie: </b>{}<br/>" +
                          "<b>Prix: </b>{}<br/>" +
                          "<b>Dégâts (P): </b>{}<br/>" +
                          "<b>Dégâts (M): </b>{}<br/>" +
                          "<b>Critique: </b>{}<br/>" +
                          "<b>Portée: </b>{}<br/>" +
                          "<b>Poids: </b>{}<br/>" +
                          "<b>Type: </b>{}<br/>" +
                          "<b>Spécial: </b>{}<br/></p>" +
                          "<h2>Description:</h2><p>{}</p>" +
                          "<p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>").format(
                      w['Catégorie'] if 'Catégorie' in w else '-',
                      w['Sous-catégorie'] if 'Sous-catégorie' in w else '-',
                      w['Prix'] if 'Prix' in w else '-',
                      w['DégâtsP'] if 'DégâtsP' in w else '-',
                      w['DégâtsM'] if 'DégâtsM' in w else '-',
                      w['Critique'] if 'Critique' in w else '-',
                      w['Portée'] if 'Portée' in w else '-',
                      w['Poids'] if 'Poids' in w else '-',
                      w['Type'] if 'Type' in w else '-',
                      w['Spécial'] if 'Spécial' in w else '-',
                      description,
                      w['Référence'])
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
              "damageRoll": w['DégâtsM'],
              "damageType": w['Type'],
              "critRange":  getCritRange(w['Critique']),
              "critMult": getCritMult(w['Critique']),
              "isMelee": (w['Portée'] == "—"),
              "range": getRange(w['Portée']),
          }
      },
      "img": img[w['Nom']] if w['Nom'] in img and "pf1-fr" not in img[w['Nom']] else "systems/pf1/icons/items/weapons/quarterstaff.png"
    }
    
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/weapons.json", "w")
outFile.write(json.dumps(list, indent=3))
