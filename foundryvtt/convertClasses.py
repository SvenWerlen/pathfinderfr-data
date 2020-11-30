#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re
import math

from libData import *

data = None
with open("../data/classes.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

img = json.load(open('data/classes-img.json', 'r'))

#
# retourne True si c'est une compétence de classe
#
def isClassSkill(cl, name):
    for sk in cl['CompétencesDeClasse']:
        if sk['Compétence'] == name:
            return True
    return False


#
# retourne le tableau des niveaux
#
def generateTable(data):
    buf = "<table><tr><th>Niveau</th><th>BBA</th><th>Ref</th><th>Vig</th><th>Vol</th></tr>"
    for lvl in data:
        buf = buf + "<tr><td>" + str(lvl['Niveau']) + "</td><td>" + lvl['BBA'] + "</td><td>" + lvl['Réflexes'] + "</td><td>" + lvl['Vigueur'] + "</td><td>" + lvl['Volonté'] + "</td></tr>"
    buf = buf + "</table>"
    return buf

def getSavingThrows(data, key):
    return "low" if int(data[0][key]) == 0 else "high"

def getBAB(data):
    if int(data[0]["BBA"]) == 0 and int(data[2]["BBA"]) == 1:
        return "low"
    elif int(data[0]["BBA"]) == 0:
        return "med"
    else:
        return "high"

list = []
duplicates = []
for c in data:
    if c['Nom'] in duplicates:
      print("Ignoring duplicate: " + c['Nom'])
      continue
    duplicates.append(c['Nom'])
    
    if "DescriptionHTML" in c:
      description = c['DescriptionHTML']
    elif "Description" in c:
      description = c['Description'].replace('\n','<br/>')
    else:
      description = ""
    
    name = c['Nom']
    
    description += generateTable(c['Progression'])
    description = generateDescriptionHTML(name, description, c['Référence'])
    
    el = {
        'name': name,
        'permission': { "default": 0 },
        'type': "class",
        'data': {
            'source': c['Source'],
            'description': {
                "value": ("<div class=\"class-description\">"+
                        "<p><b>Dé de vie : </b>{}<br/>" +
                        "<b>Alignement : </b>{}<br/>" +
                        "<b>Rangs/niveau : </b>{}</p>" +
                        "<h2>Description</h2>{}"
                        "</div>").format(
                    c['DésDeVie'],
                    c['Alignement'],
                    c['RangsParNiveau'],
                    description),       
                "chat":"",
                "unidentified":""
            },
            'changes': [],
            'changeFlags': {
                "loseDexToAC": False,
                "noStr": False,
                "noDex": False,
                "oneInt": False,
                "oneWis": False,
                "oneCha": False,
                "noEncumbrance": False,
                "mediumArmorFullSpeed": False,
                "heavyArmorFullSpeed": False 
            },
            "classType": "base" if not 'Prestige' in c else 'prestige',
            "levels": 1,
            "hd": int(c['DésDeVie'][1:]), 
            "hp": int(c['DésDeVie'][1:]), 
            "bab": getBAB(c['Progression']),
            "skillsPerLevel": c['RangsParNiveau'],
            "savingThrows": { 
                "fort": { "value": getSavingThrows(c['Progression'], 'Vigueur') }, 
                "ref": { "value": getSavingThrows(c['Progression'], 'Réflexes') }, 
                "will": { "value": getSavingThrows(c['Progression'], 'Volonté') }
            },
            "fc":{
                "hp":{ "value":0 },
                "skill":{ "value":0 },
                "alt":{ "value":0 }
            },
            "classSkills":{
                "acr": isClassSkill(c, 'Acrobaties'),
                "apr": isClassSkill(c, 'Estimation'),
                #"art": isClassSkill(c, ''),
                "blf": isClassSkill(c, 'Bluff'),
                "clm": isClassSkill(c, 'Escalade'),
                "crf": isClassSkill(c, 'Artisanat'),
                "dip": isClassSkill(c, 'Diplomatie'),
                "dev": isClassSkill(c, 'Sabotage'),
                "dis": isClassSkill(c, 'Déguisement'),
                "esc": isClassSkill(c, 'Évasion'),
                "fly": isClassSkill(c, 'Vol'),
                "han": isClassSkill(c, 'Dressage'),
                "hea": isClassSkill(c, 'Premiers secours'),
                "int": isClassSkill(c, 'Intimidation'),
                "kar": isClassSkill(c, 'Connaissances (mystères)'),
                "kdu": isClassSkill(c, 'Connaissances (exploration souterraine)'),
                "ken": isClassSkill(c, 'Connaissances (ingénierie)'),
                "kge": isClassSkill(c, 'Connaissances (géographie)'),
                "khi": isClassSkill(c, 'Connaissances (histoire)'),
                "klo": isClassSkill(c, 'Connaissances (folklore local)'),
                "kna": isClassSkill(c, 'Connaissances (nature)'),
                "kno": isClassSkill(c, 'Connaissances (noblesse)'),
                "kpl": isClassSkill(c, 'Connaissances (plans)'),
                "kre": isClassSkill(c, 'Connaissances (religion)'),
                "lin": isClassSkill(c, 'Linguistique'),
                #"lor": isClassSkill(c, ''),
                "per": isClassSkill(c, 'Perception'),
                "prf": isClassSkill(c, 'Représentation'),
                "pro": isClassSkill(c, 'Profession'),
                "rid": isClassSkill(c, 'Équitation'),
                "sen": isClassSkill(c, 'Psychologie'),
                "slt": isClassSkill(c, 'Escamotage'),
                "spl": isClassSkill(c, 'Art de la magie'),
                "ste": isClassSkill(c, 'Discrétion'),
                "sur": isClassSkill(c, 'Survie'),
                "swm": isClassSkill(c, 'Natation'),
                "umd": isClassSkill(c, 'Utilisation d\'objets magiques'),
            },
            "damage": { "parts":[] },
            "preparation": { "maxAmount":0 },
            "weaponData": {
                "critRange":20,
                "critMult":2   
            }
        },
        'sort': 100001,
        'flags':  {},
        "img": img[name] if name in img and "pf1-fr" not in img[name] else "icons/svg/mystery-man.svg"
    }
    list.append(el)

list = mergeWithLetContribute(list, "letscontribute/classesfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/classes.json", "w")
outFile.write(json.dumps(list, indent=3))
