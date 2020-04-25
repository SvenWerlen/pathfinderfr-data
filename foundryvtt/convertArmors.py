#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

data = None
with open("../data/armures.yml", 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def getWeight(weight):
    m = re.search('(.*) kg', weight)
    if m:
        return float(m.group(1).replace(",","."))
    m = re.search('(.*) g', weight)
    if m:
        return float(m.group(1).replace(",","."))/1000
    return None

def getPrice(price):
    m = re.search('(.*) po', price)
    if m:
        return int(m.group(1))
    return None

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
for a in data:
    el = {
        "name": a['Nom'],
        "permission": {
            "default": 0
        },
        "type": "equipment",
        "data": {
            "description": {
                "value": ("<p><b>Catégorie: </b>{}<br/>" +
                        "<b>Prix: </b>{}<br/>" +
                        "<b>Bonus: </b>{}<br/>" +
                        "<b>Dex maximal: </b>{}<br/>" +
                        "<b>Malus: </b>{}<br/>" +
                        "<b>Échec: </b>{}<br/>" +
                        "<b>Poids: </b>{}<br/>" +
                        "<h3>Description:</h3><p>{}</p>" +
                        "<p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>").format(
                    a['Catégorie'] if 'Catégorie' in a else '-',
                    a['Prix'] if 'Prix' in a else '-',
                    a['Bonus'] if 'Bonus' in a else '-',
                    a['BonusDexMax'] if 'BonusDexMax' in a else '-',
                    a['Malus'] if 'Malus' in a else "0",
                    a['ÉchecProfane'] if 'ÉchecProfane' in a else '-',
                    a['Poids'] if 'Poids' in a else '-',
                    a['Description'].replace('\n','<br/>') if 'Description' in a else "",
                    a['Référence']),
                "chat": "",
                "unidentified": ""
            },
            "source": a['Source'],
            "quantity": 1,
            "weight": getWeight(a['Poids']),
            "price": getPrice(a['Prix']),
            "identified": True,
            #"hp": {
            #    "max": 5,
            #    "value": 5
            #},
            #"hardness": 10,
            "carried": False,
            "changes": [],
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
            "armor": {
                "type": getType(a['Catégorie']),
                "value": getBonus(a['Bonus']),
                "dex": getBonus(a['BonusDexMax']),
                "acp": getMalus(a['Malus']),
                "enh": 0
            },
            "spellFailure": getSpellFailure(a['ÉchecProfane']),
            "slot": "armor" if getType(a['Catégorie']) in ["medium", "light", "heavy"] else "slotless",
            "activation": {
                "cost": None,
                "type": ""
            },
            "damage": {
                "parts": []
            },
            "attack": {
                "parts": []
            }
        },
        "sort": 1200001,
        "flags": {},
        "img": "systems/pf1/icons/shield.png" if getType(a['Catégorie']) == "shield" else "systems/pf1/icons/armor.png"
    }
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("armors.json", "w")
outFile.write(json.dumps(list, indent=3))
