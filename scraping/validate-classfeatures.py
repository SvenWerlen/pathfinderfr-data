#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import typing
import sys

data = None
with open("../data/classfeatures.yml", 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

hashmap = {}

for clf in data:
    archetype = "-"
    if 'Archétype' in clf:
        archetype = clf['Archétype']
        
    key = clf['Nom'].strip() + "#" + clf['Classe'].strip() + "#" + archetype.strip()
    if key in hashmap:
        print("Doublon détecté!")
        print(clf)
        exit(1)
    
    hashmap[key]=None
    
    #print("Processing %s" % d['Nom'])
    
