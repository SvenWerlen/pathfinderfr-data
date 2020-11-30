#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

from libData import *

data = None
with open("../data/armures.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

img = json.load(open('data/armors-img.json', 'r'))

def getBonus(bonus):
    m = re.search('\+(\d+)', bonus)
    if m:
        return int(m.group(1))
    return None

def getMalus(malus):
    m = re.search('-(\d+)', malus)
    if m:
        return int(m.group(1))
    return 0

def getSpellFailure(failure):
    m = re.search('(\d+)%', failure)
    if m:
        return int(m.group(1))
    return None

def getType(type):
    if type == "Armure intermédiaire": 
        return "mediumArmor"
    elif type == "Armure légère":
        return "lightArmor"
    elif type == "Armure lourde":
        return "heavyArmor"
    elif type == "Bouclier":
        return "lightShield"
    elif type == "Supplément":
        return "other"
    else:
        return None

list = []
duplicates = []
for a in data:
    if a['Nom'] in duplicates:
        print("Ignoring duplicate: " + a['Nom'])
        continue
    duplicates.append(a['Nom'])
    
    name = a['Nom']
    
    if "DescriptionHTML" in a:
      description = a['DescriptionHTML']
    elif "Description" in a:
      description = a['Description'].replace('\n','<br/>')
    else:
      description = ""
    description = generateDescriptionHTML(name, description, a['Référence'])
    
    el = {
        "name": name,
        "type": "equipment",
        "data": {
            "description": {
                "value": ("<div class=\"armor-description\"><p>" +
                        generateProp("Catégorie", a, 'Catégorie', "-") + 
                        "<b>Prix : </b>{}, <b>Poids : </b>{}<br/>" +
                        generateProp("Bonus", a, 'Bonus') + 
                        generateProp("Dex maximale", a, 'BonusDexMax') + 
                        generateProp("Malus", a, 'Malus') + 
                        generateProp("Échec", a, 'ÉchecProfane') + 
                        "</p><h2>Description</h2>{}" +
                        "</div>").format(
                    a['Prix'] if 'Prix' in a else '-',
                    a['Poids'] if 'Poids' in a else '-',
                    description)
            },
            "source": a['Source'],
            "quantity": 1,
            "weight": getWeight(a['Poids']),
            "price": getPrice(a['Prix']),
            "identified": True,
            "carried": True,
            "equipped": False,
            "equipmentType": "shield" if getType(a['Catégorie']) in ["lightShield", "other"] else "armor",
            "equipmentSubtype": getType(a['Catégorie']),
            "armor": {
                "value": getBonus(a['Bonus']),
                "dex": getBonus(a['BonusDexMax']),
                "acp": getMalus(a['Malus']),
                "enh": 0
            },
            "spellFailure": getSpellFailure(a['ÉchecProfane']),
            "slot": "slotless"
        },
        "img": img[name] if name in img and "pf1-fr" not in img[name] else "systems/pf1/icons/items/armor/banded-mail.PNG"
    }
    
    list.append(el)
    
list = mergeWithLetContribute(list, "letscontribute/armorsfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/armors.json", "w")
outFile.write(json.dumps(list, indent=3))
