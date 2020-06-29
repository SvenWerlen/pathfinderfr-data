#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import csv

from libBuffs import *

data = None
with open("../data/dons.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

buffs = {}
buffsTemp = {}

with open('data/buffs-feats.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile)
    idx = -1
    for row in spamreader:
        idx+=1
        if idx == 0:
            continue
        bList = []
        if row[0] and row[5]:
          bList.append(createChange(row[5], row[2], row[3], row[4]))
        if row[0] and row[9]:
          bList.append(createChange(row[9], row[6], row[7], row[8]))
        if len(bList) > 0:
          if row[1] == "TRUE":
            buffsTemp[row[0]] = bList
          else:
            buffs[row[0]] = bList


list = []
listBuffs = []

duplicates = []
for d in data:
  if d['Nom'] in duplicates:
    print("Ignoring duplicate: " + d['Nom'])
    continue
  duplicates.append(d['Nom'])


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
      "changes": buffs[d['Nom']] if d['Nom'] in buffs else [],
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
    "flags": {}
  }
  
  category = d['Catégorie'].lower() if 'Catégorie' in d else '-',
  if "équipe" in category:
    el["img"] = "systems/pf1/icons/feats/quick-draw.jpg"
  elif "création" in category:
    el["img"] = "systems/pf1/icons/feats/master-craftsman.jpg"
  elif "métamagie" in category:
    el["img"] = "systems/pf1/icons/feats/empower-spell.jpg"
  elif "monstre" in category:
    el["img"] = "systems/pf1/icons/feats/natural-spell.jpg"
  elif "héroïques" in category:
    el["img"] = "systems/pf1/icons/feats/extra-mercy.jpg"
  elif "combat" in category:
    el["img"] = "systems/pf1/icons/feats/improved-two-weapon-fighting.jpg"
  else:
    el["img"] = "systems/pf1/icons/feats/athletic.jpg"
    
  # Independent buff
  if d['Nom'] in buffsTemp:
    elBuff = {
      "name":  el['name'],
      "type": "buff",
      "data": {
        "description": {
          "value": el['data']['description']['value'],
        },
        "changes": buffsTemp[el['name']],
        "buffType": "temp",
        "active": False
      },
      "img": el["img"],
    }
    listBuffs.append(elBuff)        
  
  list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/feats.json", "w")
outFile.write(json.dumps(list, indent=3))

# écrire le résultat dans le fichier d'origine
outFile = open("data/featsBuffs.json", "w")
outFile.write(json.dumps(listBuffs, indent=3))
