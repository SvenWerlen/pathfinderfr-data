#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json

if len(sys.argv) <= 1:
  print("Usage: %s [path]" % sys.argv[0])
  exit(1)
  
path = sys.argv[1]

names = {}

# read all lines into data with key = name
with open(path) as f:
  lines = f.readlines()
  for l in lines:
    j = json.loads(l)
    if "img" in j:
      names[j["name"]] = j["img"]
      
# écrire le résultat dans le fichier d'origine
outFile = open("data/tmp.json", "w")
outFile.write(json.dumps(names, indent=3))

print("Résultat écrit dans data/tmp.json")
