#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import csv

from libBuffs import *
from libData import *

COL = 5 # number of columns in sheet for 1 feat
NUM = 3 # number of buffs

data = None
with open("../data/dons.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

buffs = {}
buffNotes = {}
countBuffs = 0
countNotes = 0

with open('data/buffs-feats.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile)
    idx = -1
    for row in spamreader:
        idx+=1
        if idx == 0:
            continue
        buffsList = []
        notesList = []
        
        name      = row[0]
        for c in range(0, NUM):
          col = 1 + c*COL
          target    = row[col]
          subtarget = row[col+1]
          type      = row[col+2]
          formula   = row[col+3]
          notes     = row[col+4]
          if name and target:
            if notes:
              notesList.append(createContextNotes(name, notes, target, subtarget))
            else:
              change = createChange(name, formula, target, subtarget, type)
              if change:
                buffsList.append(change)
          
        
        if len(buffsList) > 0:
          buffs[name] = buffsList
          countBuffs += 1
        if len(notesList) > 0:
          buffNotes[name] = notesList
          countNotes += 1
          
print("#buffs/notes = %d/%d" % (countBuffs, countNotes))


list = []
#listBuffs = []

duplicates = []
for d in data:
  if d['Nom'] in duplicates:
    print("Ignoring duplicate: " + d['Nom'])
    continue
  duplicates.append(d['Nom'])

  avantage = d['AvantageHTML'] if 'AvantageHTML' in d else None
  if not avantage:
    print("No HTML for: %s" % d['Nom'])
    avantage = d['Avantage'] if 'Avantage' in d else '-'
  
  description = "<p><i>%s</i></p><p><b>Prérequis:</b> %s<p/><p><b>Avantage: </b>%s<p/><p><b>Référence:</b><a href=\"%s\" parent=\"_blank\">pathfinder-fr.org</a></p>" \
    % (d['Résumé'] if 'Résumé' in d else "", d['Conditions'] if 'Conditions' in d else '-', avantage, d['Référence'])

  el = {
    "name": cleanTitle(d['Nom']),
    "permission": {
        "default": 0
    },
    "type": "feat",
    "data": {
      "description": {
          "value": "<div class=\"pf2frDescr\">%s</div>" % description,
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
      "contextNotes": buffNotes[d['Nom']] if d['Nom'] in buffNotes else [],
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
  #if d['Nom'] in buffsTemp:
    #elBuff = {
      #"name":  el['name'],
      #"type": "buff",
      #"data": {
        #"description": {
          #"value": el['data']['description']['value'],
        #},
        #"changes": buffsTemp[el['name']],
        #"buffType": "temp",
        #"active": False
      #},
      #"img": el["img"],
    #}
    #listBuffs.append(elBuff)        
  
  list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/feats.json", "w")
outFile.write(json.dumps(list, indent=3))

# écrire le résultat dans le fichier d'origine
#outFile = open("data/featsBuffs.json", "w")
#outFile.write(json.dumps(listBuffs, indent=3))
