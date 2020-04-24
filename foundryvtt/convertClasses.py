#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys

data = None
with open("../data/classes.yml", 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

#
# retourne True si c'est une compétence de classe
#
def isClassSkill(cl, name):
    for sk in cl['CompétencesDeClasse']:
        if sk['Compétence'] == name:
            return True
    return False


list = []
for c in data:
    el = {
        'name': c['Nom'],
        'permission': { "default": 0 },
        'type': "class",
        'data': {
            'source': c['Source'],
            'description': {
                "value": ("<p>{}</p>" +
                        "<p><b>Référence: </b><a href=\"{}\" parent=\"_blank\">pathfinder-fr.org</a></p>").format(
                    c['Description'].replace('\n','<br/>'),
                    c['Référence']),
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
            "classType": "base",
            "levels": 1,
            "hd": 8, #c['DésDeVie'], # valeur numérique??
            "hp": 8, #c['DésDeVie'], # valeur numérique??
            "bab": "med",
            "skillsPerLevel": c['RangsParNiveau'],
            "savingThrows": { 
                "fort": { "value":"low" }, 
                "ref":{ "value":"high" },
                "will":{"value":"low" } 
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
        #'img': "systems/pf1/icons/items/weapons/throwingknives.jpg"
    }
    list.append(el)


# écrire le résultat dans le fichier d'origine
outFile = open("classes.json", "w")
outFile.write(json.dumps(list, indent=3))
