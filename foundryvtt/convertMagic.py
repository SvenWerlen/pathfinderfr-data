#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

from libData import *

data = None
with open("../data/magic.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

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
    
    name = m['Nom'][0].upper() + m['Nom'][1:].lower()
    if "DescriptionHTML" in m:
      description = m['DescriptionHTML']
    elif "Description" in m:
      description = m['Description'].replace('\n','<br/>')
    else:
      description = ""

    description = improveDescription(description, name)
    
    el = {
        "name": name,
        "type": "equipment",
        "data": {
            "description": {
                "value": ("<div class=\"pf2frDescr\"><p>"+
                        "<b>Type : </b>{}<br/>" +
                        "<b>Prix : </b>{}<br/>" +
                        "<b>Emplacement : </b>{}<br/>" +
                        "<b>Poids : </b>{}<br/>" +
                        "<b>Aura : </b>{}<br/>" +
                        "<b>NLS : </b>{}<br/></p>" +
                        "<h2>Description</h2><p>{}</p>" +
                        "<p><b>Référence : </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>" +
                        "<h2>Fabrication</h2><p>" +
                        "<b>Conditions : </b>{}<br/>" +
                        "<b>Coût : </b>{}<br/></p>" +
                        "</div>").format(
                    m['Type'] if 'Type' in m else '-',
                    m['Prix'] if 'Prix' in m else '-',
                    m['Emplacement'] if 'Emplacement' in m else '-',
                    m['Poids'] if 'Poids' in m else '-',
                    m['Aura'] if 'Aura' in m else "0",
                    m['NLS'] if 'NLS' in m else '-',
                    description,
                    m['Référence'],
                    m['Conditions'] if 'Conditions' in m else '?',
                    m['Coût'] if 'Coût' in m else '?')
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
    if type == "Anneaux magiques":
      el["img"] = "systems/pf1/icons/items/jewelry/ring-iron.jpg"
    elif type == "Armes magiques spécifiques":
      el["img"] = "systems/pf1/icons/items/weapons/estoc.PNG"
    elif type == "Armures magiques spécifiques":
      el["img"] = "systems/pf1/icons/items/armor/hide-armor.PNG"
    elif type == "Boucliers magiques spécifiques":
      el["img"] = "systems/pf1/icons/items/armor/shield-heavy-metal.png"
    elif type == "Bâtons magiques":
      el["img"] = "systems/pf1/icons/items/weapons/quarterstaff.png"
    elif type == "Objets merveilleux":
      el["img"] = "systems/pf1/icons/skills/blue_01.jpg"
    elif type == "Sceptres magiques":
      el["img"] = "systems/pf1/icons/items/weapons/sling-staff.png"
    else:
      el["img"] = "systems/pf1/icons/skills/blue_01.jpg"

    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/magicfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/magic.json", "w")
outFile.write(json.dumps(list, indent=3))
