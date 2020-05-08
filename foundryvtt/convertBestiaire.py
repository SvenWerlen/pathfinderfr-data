#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import re
import math

data = None
print("Opening and parsing file...")
with open("../data/bestiaire.yml", 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
print("File parsed!")

KEYS = ['Nom', 'For', 'Dex', 'Con', 'Int', 'Sag', 'Cha', 'PV', 'CA', 'BBA', 'DMD', 'Réf', 'Vig', 'Vol', 'Description']

# vérifie que la créature est complète pour être importée
def isValid(obj, keys):
  for key in keys:
    if not key in obj:
      print("Créature '%s' imcomplète (%s)" % (obj['Nom'], key))
      return False
  return True

# extrait le nombre de DV
def getDV(calcul):
  num = re.search('^(\d+)d', calcul)
  if num:
    return int(num.group(1))
  
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
            "hd": { "total": getDV(b['PV']['calcul']) },
            "ac": {
              "normal": { "total": b['CA']['valeur'] },
              "touch": { "total": b['CA']['contact'] },
              "flatFooted": { "total": b['CA']['dépourvu'] }
            },
            "naturalAC": getNaturalBonus(b['CA']['calcul']),
            "acNotes": b['CA']['calcul'],
            "cmdNotes": b['DMDSpécial'] if 'DMDSpécial' in b else '',
            "cmbNotes": b['BMOSpécial'] if 'BMOSpécial' in b else '',
            "saveNotes": getSavesNotes(b),
            "cmd": { "total": b['DMD'], "flatFootedTotal": b['DMD'] - max(0, getMod(b['Dex'])) },
            "cmb": { "total": b['BBA'] },
            "hp": { 
              "value": b['PV']['valeur'],
              "max": b['PV']['valeur'] 
            },
            "savingThrows": { 
              "fort": { "total": b['Vig'] },
              "ref": { "total": b['Réf'] },
              "will": { "total": b['Vol'] }
            },
          },
          "details": {
            "notes": { "value": '<div class="pf1notes">' + b['Description'] + '</div>' }
          }
        },
    }
    
    list.append(el)

# écrire le résultat dans le fichier d'origine
outFile = open("data/beastiary.json", "w")
outFile.write(json.dumps(list, indent=3))

print("%s creatures ignored!" % ignored)
