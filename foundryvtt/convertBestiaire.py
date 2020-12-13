#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re
import math
import uuid

from libData import *

data = None
print("Opening and parsing file...")
#with open("../data/bestiaire-mini.yml", 'r') as stream:
with open("../data/bestiaire.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
print("File parsed!")

KEYS = ['Nom', 'For', 'Dex', 'Con', 'Int', 'Sag', 'Cha', 'PV', 'CA', 'BBA', 'BMO', 'DMD', 'Réf', 'Vig', 'Vol', 'Init', 'Description']

# vérifie que la créature est complète pour être importée
def isValid(obj, keys):
  for key in keys:
    if not key in obj:
      print("Créature '%s' incomplète (%s)" % (obj['Nom'], key))
      return False
  return True

# extrait le nombre de Niv/DV
def getNivDV(calcul):
  num = re.search('^(\d+)d(\d+)', calcul)
  if num:
    return (int(num.group(1)),int(num.group(2)))
  
  print("Error: invalid format for DV: %s" % calcul)
  
# calcule le bonus de caractéristique
def getMod(value):
  return math.floor((value-10)/2)

# regroupe les notes pour les jets de sauvegarde
def getSavesNotes(b):
  value = ""
  if 'RéfSpécial' in b:
    value += b['RéfSpécial'] + ", "
  if 'VigSpécial' in b:
    value += b['VigSpécial'] + ", "
  if 'VolSpécial' in b:
    value += b['VolSpécial'] + ", "
  if len(value) > 2:
    value = value[:-2]
  return value

# tente d'extraire le bonus naturel
def getNaturalBonus(calcul):
  num = re.search('naturelle \+(\d+)', calcul.lower())
  if num:
    return int(num.group(1))
  return 0  

# calcule le type de BBA
def getBBAStrength(name, value, level):
  if value == level:
    return "high"
  elif value == math.floor(0.75*level):
    return "med"
  elif value == math.floor(0.5*level):
    return "low"
  else:
    print("Unable to compute BBA for %s " % name)
    return ""

# génère un JSON pour modification
def newBuff(formula, target, subTarget, modifier):
  return {
    "_id": uuid.uuid4().hex[:8],
    "formula": formula,
    "operator": "add",
    "target": target,
    "subTarget": subTarget,
    "modifier": modifier,
    "priority": 0,
    "value": 0
  }

# génère les attaques
def fillAttacks(liste, b):
  if "AttaqueCàC" in b:
    for a in b["AttaqueCàC"]:
      att = re.search('^\+(\d+)', a["bonus"]) if "bonus" in a else False # Nuée n'ont pas d'attaque
      dmg = re.search('^([\d\+d-]+)', a["dommages"])
      if att and dmg:
        liste.append({
          "name": "%s, %s (%s)" % (a["attaque"], a["bonus"], a["dommages"]),
          "type": "attack",
          "data": {
            "attackBonus": str(int(att.group(1)) - b["BBA"]),
            "damage": {
              "parts": [[ dmg.group(1), ""]]
            },
            "activation": { "cost": 1, "type": "standard" },
            "actionType": "mwak",
            "attackType": "weapon",
          },
          "img": "/modules/pf1-fr/icons/actions/melee-attack.svg"
        });
  if "AttaqueDistance" in b:
    for a in b["AttaqueDistance"]:
      att = re.search('^\+(\d+)', a["bonus"]) if "bonus" in a else False # Nuée n'ont pas d'attaque
      dmg = re.search('^([\d\+d-]+)', a["dommages"])
      if att and dmg:
        liste.append({
          "name": "%s, %s (%s)" % (a["attaque"], a["bonus"], a["dommages"]),
          "type": "attack",
          "data": {
            "attackBonus": str(int(att.group(1)) - b["BBA"]),
            "damage": {
              "parts": [[ dmg.group(1), ""]]
            },
            "activation": { "cost": 1, "type": "standard" },
            "actionType": "rwak",
            "attackType": "weapon",
          },
          "img": "/modules/pf1-fr/icons/actions/ranged-attack.svg"
        });

list = []
duplicates = []
ignored = 0

for b in data:
  
  if b['Nom'] in duplicates:
      print("Ignoring duplicate: " + b['Nom'])
      continue
  duplicates.append(b['Nom'])
  
  # check validity
  if not isValid(b, KEYS):
    ignored += 1
    continue;
  
  hp = getNivDV(b['PV']['calcul'])
  naturalAC = getNaturalBonus(b['CA']['calcul'])
  bbaStrength = getBBAStrength(b['Nom'], b['BBA'], hp[0])
  
  # différence d'initiative (à ajouter en tant que modif)
  diffInit   = b['Init'] - getMod(b['Dex']) 
  diffPV     = b['PV']['valeur'] - hp[0] * getMod(b['Con'])
  diffCASize = b['CA']['contact'] - getMod(b['Dex']) - 10
  diffCA     = b['CA']['valeur'] - getMod(b['Dex']) - naturalAC - diffCASize - 10
  diffFort   = b['Vig'] - getMod(b['Con'])
  diffRef    = b['Réf'] - getMod(b['Dex'])
  diffWill   = b['Vol'] - getMod(b['Sag'])
  diffBMO    = b['BMO'] - b['BBA'] - getMod(b['For'])
  diffDMD    = b['DMD'] - b['BBA'] - getMod(b['For']) - getMod(b['Dex']) -10
  if len(bbaStrength) == 0:
    diffBMO += b['BBA']
    diffDMD += b['BBA']
  
  el = {
    "name": b['Nom'],
    "type": "npc",
    "data": {
      "abilities": {
        "str": { "value": b['For'], "mod": getMod(b['For']), "total": b['For'] },
        "dex": { "value": b['Dex'], "mod": getMod(b['Dex']), "total": b['Dex'] },
        "con": { "value": b['Con'], "mod": getMod(b['Con']), "total": b['Con'] },
        "int": { "value": b['Int'], "mod": getMod(b['Int']), "total": b['Int'] },
        "wis": { "value": b['Sag'], "mod": getMod(b['Sag']), "total": b['Sag'] },
        "cha": { "value": b['Cha'], "mod": getMod(b['Cha']), "total": b['Cha'] }
      },
      "attributes": {
        "ac": {
          "normal": { "total": b['CA']['valeur'] },
          "touch": { "total": b['CA']['contact'] },
          "flatFooted": { "total": b['CA']['dépourvu'] }
        },
        "naturalAC": naturalAC,
        "acNotes": b['CA']['calcul'],
        "cmdNotes": b['DMDSpécial'] if 'DMDSpécial' in b else '',
        "cmbNotes": b['BMOSpécial'] if 'BMOSpécial' in b else '',
        "saveNotes": getSavesNotes(b),
        "cmd": { "total": b['DMD'], "flatFootedTotal": b['DMD'] - max(0, getMod(b['Dex'])) },
        "cmb": { "total": b['BMO'] },
        "bab": { "total": b['BBA'] },
        "init": { "total": b['Init'] },
        "hp": { 
          "value": b['PV']['valeur'],
          "max": b['PV']['valeur'] 
        },
        "hd": { "total": hp[0] },
        "savingThrows": { 
          "fort": { "total": b['Vig'] },
          "ref": { "total": b['Réf'] },
          "will": { "total": b['Vol'] }
        },
        "speed": { "land": { "base": b['VD']['cases']*5 if 'VD' in b else 0, "total": b['VD']['cases']*5 if 'VD' in b else 0 } }
      },
      "details": {
        "cr": { "base": b['FP'] if 'FP' in b else 0, "total": b['FP'] if 'FP' in b else 0 },
        "xp": { "value": b['PX'] if 'PX' in b else 0 },
        "notes": { "value": '<div class="pf1notes">' + b['Description'] + '</div>' }
      },
      #"skills": { "per": { "value":  } } // TODO!!!!
    },
    "items": []
  }

  buffs = {
    "name": "ajustements",
    "type": "buff",
    "data": { 
      "description": { "value": "Ajustements pour que les valeurs d'Initiative, CA, etc. correspondent aux valeurs de la créature" },
      "changes": [],
      "buffType": "perm",
      "hideFromToken": True,
      "active": True
    },
  }
  
  bClass = {
    "name": "Classe générique (bestiaire)",
    "type": "class",
    "data": { 
      "description": { "value": "Classe générique pour configurer PV" },
      "classType": "racial",
      "level": hp[0],
      "hd": hp[1],
      "hp": diffPV,
      "bab": bbaStrength,
      "savingThrows": { 
        "fort": { "value": "" },
        "ref": { "value": "" },
        "will": { "value": "" }
      },
    }
  }
  el["items"].append(bClass)
  
  if diffInit != 0:
    buffs["data"]["changes"].append(newBuff(str(diffInit), "misc", "init", "racial"))
  if diffCA != 0:
    buffs["data"]["changes"].append(newBuff(str(diffCA), "ac", "aac", "racial"))
  if diffCASize != 0:
    buffs["data"]["changes"].append(newBuff(str(diffCASize), "ac", "ac", "racial"))
  if len(bbaStrength) == 0:
    buffs["data"]["changes"].append(newBuff(str(b['BBA']), "attack", "attack", "racial"))
  if diffFort != 0:
    buffs["data"]["changes"].append(newBuff(str(diffFort), "savingThrows", "fort", "racial"))
  if diffRef != 0:
    buffs["data"]["changes"].append(newBuff(str(diffRef), "savingThrows", "ref", "racial"))
  if diffWill != 0:
    buffs["data"]["changes"].append(newBuff(str(diffWill), "savingThrows", "will", "racial"))
  if diffBMO != 0:
    buffs["data"]["changes"].append(newBuff(str(diffBMO), "misc", "cmb", "racial"))
  if diffDMD != 0:
    buffs["data"]["changes"].append(newBuff(str(diffDMD), "misc", "cmd", "racial"))
  
  fillAttacks(el["items"],b)
  el["items"].append(buffs)
  
  list.append(el)
  
list = mergeWithLetContribute(list, "letscontribute/bestiaryfr.json")

# écrire le résultat dans le fichier d'origine
outFile = open("data/bestiary.json", "w")
outFile.write(json.dumps(list, indent=3))

print("%s creatures ignored!" % ignored)
print("%s creatures added!" % (len(data)-ignored))
