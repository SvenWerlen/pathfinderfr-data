#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys

from libData import *

data = None
with open("../data/classfeatures.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

def getAbbr(name):
    if name == "Barbare":
        return "Brb"
    elif name == "Prêtre combattant":
        return "Prc"
    elif name == "Archer-mage":
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
    
    name = "%s %s%d : %s" % (
      getAbbr(d['Classe']),             # abréviation: Roublard => Rou
      " " if d['Niveau'] < 10 else "",  # espace supplémentaire: 1 => " 1", 10 => "10"
      d['Niveau'],                      # niveau
      d['Nom'].replace(":"," -"))       # nom
    
    description = d['DescriptionHTML'] if 'DescriptionHTML' in d else d['Description'].replace("\n", "<br/>")
    description = improveDescription(description, name)
    
    el = {
        "flags": { 'class': d['Classe'], 'archetype': 'base'},
        "name": name,
        "permission": {
            "default": 0
        },
        "type": "feat",
        "data": {
            "featType": "classFeat",
            "description": {
                "value": ("<div class=\"pf2frDescr\"><p><b>Classe: </b>{}<br/>" +
                        "<b>Niveau: </b>{}<br/>" +
                        "<b>De base? </b>{}<br/></p>" +
                        "<h2>Description</h2><p>{}</p>" +
                        "<p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p></div>").format(
                    d['Classe'],
                    d['Niveau'],
                    "oui" if 'Auto' in d and d['Auto'] else "non",
                    description,
                    d['Référence']),
                "chat": "",
                "unidentified": ""
            },
            "tags": [[ "De base" if 'Auto' in d and d['Auto'] else "À choisir", ]],
            "associations": { "classes": [ [ d['Classe'] ] ] },
            "source": d['Source'],
        }
    }
    
    level = d['Niveau']
    if level <= 5:
      el["img"] = "systems/pf1/icons/skills/nature_07.jpg"
    elif level <= 10:
      el["img"] = "systems/pf1/icons/skills/ice_13.jpg"
    elif level <= 15:
      el["img"] = "systems/pf1/icons/skills/affliction_22.jpg"
    else:
      el["img"] = "systems/pf1/icons/skills/shadow_10.jpg"
    
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/classfeaturesfr.json", False)

# écrire le résultat dans le fichier d'origine
outFile = open("data/classfeatures.json", "w")
outFile.write(json.dumps(list, indent=3))
