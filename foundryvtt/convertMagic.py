#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

data = None
with open("../data/magic.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def getWeight(weight):
    m = re.search('([\d,]+?) kg', weight)
    if m:
        return float(m.group(1).replace(",","."))
    m = re.search('([\d,]+?) g', weight)
    if m:
        return float(m.group(1).replace(",","."))/1000
    return None

def getPrice(price):
    m = re.search('([\d ]+?) po', price.replace('.',''))
    if m:
        return int(m.group(1).replace(' ', ''))
    return None



def getType(type):
    if type == "Armure intermédiaire": 
        return "medium"
    elif type == "Armure légère":
        return "light"
    elif type == "Armure lourde":
        return "heavy"
    elif type == "Bouclier":
        return "shield"
    elif type == "Supplément":
        return "misc"
    else:
        return None

list = []
duplicates = []
for m in data:
    if m['Nom'] in duplicates:
        print("Ignoring duplicate: " + m['Nom'])
        continue
    duplicates.append(m['Nom'])
    
    el = {
        "name": m['Nom'],
        "type": "loot",
        "data": {
            "description": {
                "value": ("<p><b>Type: </b>{}<br/>" +
                        "<b>Prix: </b>{}<br/>" +
                        "<b>Emplacement: </b>{}<br/>" +
                        "<b>Poids: </b>{}<br/>" +
                        "<b>Aura: </b>{}<br/>" +
                        "<b>NLS: </b>{}<br/></p>" +
                        "<b>Conditions: </b>{}<br/></p>" +
                        "<h3>Description:</h3><p>{}</p>" +
                        "<p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>").format(
                    m['Type'] if 'Type' in m else '-',
                    m['Prix'] if 'Prix' in m else '-',
                    m['Emplacement'] if 'Emplacement' in m else '-',
                    m['Poids'] if 'Poids' in m else '-',
                    m['Aura'] if 'Aura' in m else "0",
                    m['NLS'] if 'NLS' in m else '-',
                    m['Conditions'] if 'Conditions' in m else '-',
                    m['Description'].replace('\n','<br/>') if 'Description' in m else "",
                    m['Référence'])
            },
            "source": m['Source'],
            "quantity": 1,
            "weight": getWeight(m['Poids']) if 'Poids' in m else 0,
            "price": getPrice(m['Prix']) if 'Prix' in m else 0,
            "identified": True,
            "carried": True,
            "equipped": False,
            "subType": "gear"
        }
    }
                        
    type = m['Type'] if 'Type' in m else '-';
    if type == "Anneau":
      el["img"] = "systems/pf1/icons/items/jewelry/ring-iron.jpg"
    elif type == "Arme":
      el["img"] = "systems/pf1/icons/items/weapons/estoc.PNG"
    elif type == "Armure/Bouclier":
      el["img"] = "systems/pf1/icons/items/armor/hide-armor.PNG"
    elif type == "Bâton":
      el["img"] = "systems/pf1/icons/items/weapons/quarterstaff.png"
    elif type == "Objet merveilleux":
      el["img"] = "systems/pf1/icons/skills/blue_01.jpg"
    elif type == "Sceptre":
      el["img"] = "systems/pf1/icons/items/weapons/sling-staff.png"
    else:
      el["img"] = "systems/pf1/icons/skills/blue_01.jpg"
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/magic.json", "w")
outFile.write(json.dumps(list, indent=3))
