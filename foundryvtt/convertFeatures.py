#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys

data = None
with open("../data/classfeatures.yml", 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

def getAbbr(name):
    if name == "Barbare":
        return "Brb"
    elif name == "Prêtre combattant":
        return "Prc"
    elif name == "Archer mage":
        return "ArM"
    elif name == "Champion occultiste":
        return "Chp"
    elif name == "Magus":
        return "Mgs"
    elif name == "Chaman":
        return "Chm"
    else:
        return name[0:3]


list = []
for d in data:
    if "Archétype" in d:
        continue;
    
    el = {
        "flags": { 'class': d['Classe'], 'archetype': 'base'},
        "name": getAbbr(d['Classe']) + " " + str(d['Niveau']) + ": " + d['Nom'],
        "permission": {
            "default": 0
        },
        "type": "feat",
        "data": {
            "featType": "classFeat",
            "description": {
                "value": ("<p><b>Classe: </b>{}<br/>" +
                        "<b>Niveau: </b>{}<br/>" +
                        "<b>De base? </b>{}<br/></p>" +
                        "<h3>Description:</h3><p>{}</p>" +
                        "<p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>").format(
                    d['Classe'],
                    d['Niveau'],
                    "oui" if 'Auto' in d and d['Auto'] else "non",
                    d['Description'],
                    d['Référence']),
                "chat": "",
                "unidentified": ""
            },
            "source": d['Source'],
        },
        "img": "modules/pf1-fr/icons/features.png"
    }
    
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/classfeatures.json", "w")
outFile.write(json.dumps(list, indent=3))
