#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re

data = None
with open("../data/spells.yml", 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def getLevel(level):
    m = re.search('([0-9])', level)
    if m:
        return int(m.group(1))
    else:
        return 0

list = []
for s in data:
    el = {
        "name": s['Nom'],
        "permission": {
            "default": 0
        },
        "type": "spell",
        "data": {
            "description": {
               "value": ("<p><b>École: </b>{}<br/>" +
                        "<b>Niveau: </b>{}<br/>" +
                        "<b>Temps d'incantation: </b>{}<br/>" +
                        "<b>Composantes: </b>{}<br/>" +
                        "<b>Portée: </b>{}<br/>" +
                        "<b>Cible ou zone d'effet: </b>{}<br/>" +
                        "<b>Durée: </b>{}<br/>" +
                        "<b>Jet de sauvegarde: </b>{}<br/>" +
                        "<b>Résistance à la magie: </b>{}<br/></p>" +
                        "<h3>Description:</h3><p>{}</p>" +
                        "<p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>").format(
                    s['École'] if 'École' in s else '-',
                    s['Niveau'],
                    s['Temps d\'incantation'] if 'Temps d\'incantation' in s else '-',
                    s['Composantes'] if 'Composantes' in s else '-',
                    s['Portée'] if 'Portée' in s else '-',
                    s['Cible ou zone d\'effet'] if 'Cible ou zone d\'effet' in s else '-',
                    s['Durée'] if 'Durée' in s else '-',
                    s['Jet de sauvegarde'] if 'Jet de sauvegarde' in s else '-',
                    s['Résistance à la magie'] if 'Résistance à la magie' in s else '-',
                    s['Description'].replace('\n','<br/>'),
                    s['Référence']),
                "chat": "",
                "unidentified": ""                    
            },
            "source": s['Source'],
            "activation": {
                "cost": 1,
                "type": "standard"
            },
            "duration": {
                "value": None,
                "units": ""
            },
            "target": {
                "value": s['Cible ou zone d\'effet'] if 'Cible ou zone d\'effet' in s else '-'
            },
            "range": {
                "value": None,
                "units": "touch",
                "long": None
            },
            "uses": {
                "value": 0,
                "max": 0,
                "per": None
            },
            "actionType": None,
            "attackBonus": "",
            "critConfirmBonus": "",
            "damage": {
                "parts": []
            },
            "attackParts": [],
            "formula": "",
            "ability": {
            "attack": None,
            "damage": "",
            "damageMult": 1,
            "critRange": 20,
            "critMult": 2
            },
            "save": {
                "dc": "0",
                "description": s['Jet de sauvegarde'] if 'Jet de sauvegarde' in s else '-',
                "type": None
            },
            "effectNotes": "",
            "attackNotes": "",
            "level": getLevel(s['Niveau']),
            "clOffset": 0,
            "slOffset": 0,
            "school": "",
            "subschool": "",
            "types": "",
            "components": {
                "value": "",
                "verbal": False,
                "somatic": False,
                "material": False,
                "focus": False,
                "divineFocus": 0
            },
            "castTime": "abc",
            "materials": {
                "value": "",
                "consumed": False,
                "focus": "",
                "cost": 0,
                "supply": 0
            },
            "spellbook": "primary",
            "preparation": {
                "mode": "prepared",
                "preparedAmount": 0,
                "maxAmount": 0
            },
            "sr": False,
            "shortDescription": s['Description'].replace('\n','<br/>'),
            "spellDuration": s['Durée'] if 'Durée' in s else '-',
            "spellEffect": "",
            "spellArea": "",
            "attack": {
            "parts": []
            },
            "weaponData": {
            "critRange": 20,
            "critMult": 2
            }
        },
        "sort": 100001,
        "flags": {},
        "img": "modules/pf1-fr/icons/spell.png"
    }
    
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/spells.json", "w")
outFile.write(json.dumps(list, indent=3))
