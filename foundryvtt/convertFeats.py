#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys

data = None
with open("../data/dons.yml", 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)


list = []
for d in data:
    el = {
        "name": d['Nom'],
        "permission": {
            "default": 0
        },
        "type": "feat",
        "data": {
            "description": {
                "value": "<p><i> {}</i></p><p><b>Prérequis: </b>{}<p/><p><b>Avantage: </b>{}<p/><p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>".format(
                    d['Résumé'] if 'Résumé' in d else "",
                    d['Conditions'] if 'Conditions' in d else '-',
                    d['Avantage'],
                    d['Référence']),
                "chat": "",
                "unidentified": ""
            },
            "source": d['Source'],
            "activation": {
                "cost": 1,
                "type": ""
            },
            "duration": {
                "value": None,
                "units": ""
            },
            "target": {
                "value": ""
            },
            "range": {
                "value": None,
                "units": "",
                "long": None
            },
            "uses": {
                "value": 0,
                "max": 0,
                "per": None
            },
            "actionType": "",
            "attackBonus": "",
            "critConfirmBonus": "",
            "damage": {
                "parts": []
            },
            "attackParts": [],
            "formula": "",
            "ability": {
                "attack": None,
                "damage": None,
                "damageMult": 1,
                "critRange": 20,
                "critMult": 2
            },
            "save": {
                "dc": 0,
                "type": ""
            },
            "effectNotes": "",
            "attackNotes": "",
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
            "featType": "feat",
            "requirements": d['Catégorie'] if 'Catégorie' in d else '-',
            "attack": {
            "parts": []
            }
        },
        "sort": 1300000,
        "flags": {},
        "img": "systems/pf1/icons/feat.png"
    }
    
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("feats.json", "w")
outFile.write(json.dumps(list, indent=3))
