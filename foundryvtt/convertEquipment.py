#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

data = None
with open("../data/equipement.yml", 'r') as stream:
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
                "value": ("<p><b>Prix: </b>{}<br/>" +
                        "<b>Poids: </b>{}<br/>" +
                        "<b>Catégorie: </b>{}<br/></p>" +
                        "<h3>Description:</h3><p>{}</p>" +
                        "<p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>").format(
                    m['Prix'] if 'Prix' in m else '-',
                    m['Poids'] if 'Poids' in m else '-',
                    m['Catégorie'] if 'Catégorie' in m else "0",
                    m['Description'].replace('\n','<br/>') if 'Description' in m else "",
                    m['Référence'])
            },
            "source": m['Source'],
            "quantity": 1,
            "weight": getWeight(m['Poids']) if 'Poids' in m else 0,
            "price": getPrice(m['Prix']) if 'Prix' in m else 0,
            "identified": True,
            "carried": True,
            "equipped": False
        },
        "sort": 100001,
        "flags": {},
        "img": "modules/pf1-fr/icons/equipment.png"
    }
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/equipment.json", "w")
outFile.write(json.dumps(list, indent=3))
