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
        data = yaml.load(stream)
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
        "permission": {
            "default": 0
        },
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
                    m['Référence']),
                "chat": "",
                "unidentified": ""
            },
            "source": m['Source'],
            "quantity": 1,
            "weight": getWeight(m['Poids']) if 'Poids' in m else 0,
            "price": getPrice(m['Prix']) if 'Prix' in m else 0,
            "identified": True,
            #"hp": {
            #    "max": 10,
            #    "value": 10
            #},
            #"hardness": 0,
            "carried": False,
            #"changes": [
            #[
            #    "1",
            #    "ac",
            #    "ac",
            #    "deflection"
            #]
            #],
            "changeFlags": {
                "loseDexToAC": False,
                "noStr": False,
                "noDex": False,
                "oneInt": False,
                "oneWis": False,
                "oneCha": False
            },
            "contextNotes": [],
            "equipped": False,
            #"armor": {
            #    "type": "misc",
            #    "value": 0,
            #    "dex": null,
            #    "acp": 0,
            #    "enh": 0
            #},
            #"spellFailure": 0,
            #"slot": "ring",
            "activation": {
                "cost": "",
                "type": ""
            },
            "damage": {
                "parts": []
            },
            "attack": {
                "parts": []
            }
        },
        "sort": 100001,
        "flags": {},
        "img": "modules/pf1-fr/icons/magic.png"
    }
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/magic.json", "w")
outFile.write(json.dumps(list, indent=3))
