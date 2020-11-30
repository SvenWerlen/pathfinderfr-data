#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import json
import typing
import sys
import csv

from libData import *

data = None
with open("../data/traits.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

list = []

duplicates = []
for d in data:
  key = d['Race'] + d['Nom'] if 'Race' in d else d['Nom']
  if key in duplicates:
    print("Ignoring duplicate: " + d['Nom'])
    continue
  duplicates.append(key)

  subtype = None
  name = cleanTitle(d['Nom'])
  m = re.search('Trait (de )?(.+): (.*)', name)
  if m:
    subtype = m.group(2).split(' ')[0]
    subtype = subtype[0].upper() + subtype[1:]
    name = m.group(3)
  
  replace = ""
  if 'Remplace' in d:
    for r in d['Remplace']:
      replace += r + ", "
    replace = replace[:-2]
      
  description = d['Description'].strip()
  if description.startswith("."):
    description = description[1:].strip()
  
  props = ""
  if "Race" in d:
    name = "%s (%s)" % (name, d['Race'])
    props = "<b>Race :</b> ##racesfr|%s##<br/><b>Remplace :</b> %s<p/>" \
      % (d['Race'], replace if 'Remplace' in d else "-")
  description = generateDescriptionHTML(name, description, d['Référence'])

  el = {
    "name": name,
    "type": "feat",
    "data": {
      "description": {
        "value": ("<div class=\"trait-description\"><p>{}</p> {}</div>").format(
                      props,
                      description),
      },
      "featType": "racial" if "Race" in d or subtype == "Race" else "trait",
      "tags": [[d['Race']]] if "Race" in d else [],
    },
    "flags": {},
    "img": "icons/svg/mystery-man.svg"
  }
  if subtype and subtype != "Race":
    el["data"]["tags"].append([subtype])
      
  list.append(el)


list = mergeWithLetContribute(list, "letscontribute/traitsfr.json", False)

# écrire le résultat dans le fichier d'origine
outFile = open("data/traits.json", "w")
outFile.write(json.dumps(list, indent=3))
