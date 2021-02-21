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
listArch = []

for d in data:
    
    name = "%s %s%d : %s" % (
      getAbbr(d['Classe']),             # abréviation: Roublard => Rou
      " " if d['Niveau'] < 10 else "",  # espace supplémentaire: 1 => " 1", 10 => "10"
      d['Niveau'],                      # niveau
      d['Nom'].replace(":"," -"))       # nom
    
    description = d['DescriptionHTML'] if 'DescriptionHTML' in d else d['Description'].replace("\n", "<br/>")
    description = generateDescriptionHTML(name, description, d['Référence'])
    
    className = "%s (%s)" % (d['Classe'], d["Archétype"]) if "Archétype" in d else d['Classe']
    
    el = {
        "flags": { 'class': d['Classe'], 'archetype': d["Archétype"] if "Archétype" in d else 'base'},
        "name": name,
        "permission": {
            "default": 0
        },
        "type": "feat",
        "data": {
            "featType": "classFeat",
            "description": {
                "value": ("<div class=\"feature-description\"><p><b>Classe : </b>{}<br/>" +
                        "<b>Niveau : </b>{}<br/>" +
                        "<b>De base : </b>{}<br/></p>" +
                        "<h2>Description</h2>{}" +
                        "</div>").format(
                    className,
                    d['Niveau'],
                    "oui" if 'Auto' in d and d['Auto'] else "non",
                    description),
                "chat": "",
                "unidentified": ""
            },
            "tags": [[ "De base" if 'Auto' in d and d['Auto'] else "À choisir", ]],
            "associations": { "classes": [ [ className ] ] },
            "source": d['Source'],
        }
    }
                        
    abilityType = None
    if "(sur)" in name.lower():
      abilityType = "su"
    elif "(mag)" in name.lower():
      abilityType = "sp"
    elif "(ext)" in name.lower():
      abilityType = "ex"
    if abilityType:
      el["data"]["abilityType"] = abilityType
    
    level = d['Niveau']
    if level <= 5:
      el["img"] = "systems/pf1/icons/skills/nature_07.jpg"
    elif level <= 10:
      el["img"] = "systems/pf1/icons/skills/ice_13.jpg"
    elif level <= 15:
      el["img"] = "systems/pf1/icons/skills/affliction_22.jpg"
    else:
      el["img"] = "systems/pf1/icons/skills/shadow_10.jpg"
    
    if "Archétype" in d:
        el["data"]["tags"].append([ "Archétype" ])
        listArch.append(el)
    else:
        list.append(el)

list = mergeWithLetContribute(list, "letscontribute/classfeaturesfr.json", False)
listArch = mergeWithLetContribute(listArch, "letscontribute/classfeaturesarchfr.json", False)

# écrire le résultat dans le fichier d'origine
outFile = open("data/classfeatures.json", "w")
outFile.write(json.dumps(list, indent=3))
outFile = open("data/classfeaturesarch.json", "w")
outFile.write(json.dumps(listArch, indent=3))
