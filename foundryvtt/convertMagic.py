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



def getEmplacement(emplacement):
    m = re.search('(\w+)', emplacement)
    if not m:
      return "slotless"
    emplacement = m.group(1).lower()
    
    if emplacement == "anneau": 
        return "ring"
    elif emplacement == "armure":
        return "body"
    elif emplacement == "bouclier":
        return "hands"
    elif emplacement == "ceinture":
        return "belt"
    elif emplacement == "corps":
        return "body"
    elif emplacement == "cou":
        return "neck"
    elif emplacement == "épaules":
        return "shoulders"
    elif emplacement == "front":
        return "headband"
    elif emplacement == "mains":
        return "hands"
    elif emplacement == "pied" or emplacement == "pieds" or emplacement == "sabots":
        return "feet"
    elif emplacement == "poignets":
        return "wrists"
    elif emplacement == "taille":
        return "belt"
    elif emplacement == "tête":
        return "head"
    elif emplacement == "torse":
        return "chest"
    elif emplacement == "yeux":
        return "eyes"
    elif emplacement == "aucun" or emplacement == "aucune":
        return "slotless"
    else:
        print("Non-supported slot: %s" % emplacement)
        exit(1)
      

list = []
duplicates = []
for m in data:
    if m['Nom'] in duplicates:
        print("Ignoring duplicate: " + m['Nom'])
        continue
    duplicates.append(m['Nom'])
    
    el = {
        "name": m['Nom'],
        "type": "equipment",
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
            "equipped": True,
            "equipmentType": "misc",
            "equipmentSubtype": "wondrous",
            "slot": getEmplacement(m['Emplacement']) if 'Emplacement' in m else 'slotless'
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
