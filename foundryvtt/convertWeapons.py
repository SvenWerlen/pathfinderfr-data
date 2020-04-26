#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

data = None
with open("../data/armes.yml", 'r') as stream:
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
    
    el = {
    "name": w['Nom'],
    "permission": {
        "default": 0
    },
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
                        "<h3>Description:</h3><p>{}</p>" +
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
                    w['Description'].replace('\n','<br/>') if 'Description' in w else "",
                    w['Référence']),
            "chat": "",
            "unidentified": ""
        },
        "source": w['Source'],
        "quantity": 1,
        "weight": getWeight(w['Poids']),
        "price": getPrice(w['Prix']),
        "identified": True,
        #"hp": {
        #    "max": 2,
        #    "value": 2
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
        "equipped": True,
        "masterwork": False,
        "weaponType": getType(w['Catégorie']), 
        "properties": {
            "blc": False,
            "brc": False,
            "dbl": False,
            "dis": False,
            "fin": False,
            "frg": False,
            "imp": False,
            "lgt": False,
            "mnk": False,
            "prf": False,
            "rch": False,
            "thr": False,
            "trp": False,
            "two": False
        },
        "enh": "",
        "weaponData": {
            "damageRoll": w['DégâtsM'],
            "damageType": w['Type'],
            "critRange":  getCritRange(w['Critique']),
            "critMult": getCritMult(w['Critique']),
            "isMelee": (w['Portée'] == "—"),
            "range": getRange(w['Portée']),
        },
        "damage": {
            "parts": []
        }
    },
    "sort": 300001,
    "flags": {},
    "img": "modules/pf1-fr/icons/weapon.png"
    }
    
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/weapons.json", "w")
outFile.write(json.dumps(list, indent=3))
