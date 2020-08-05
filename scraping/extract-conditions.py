#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, mergeYAML


## Configurations pour le lancement
URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.%c3%89tats%20pr%c3%a9judiciables.ashx"
MOCK_CF = None
#MOCK_CF = "mocks/conditions.html"       # décommenter pour tester avec les conditions pré-téléchargées

FIELDS = ['Nom', 'Source', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom']

liste = []

if MOCK_CF:
    content = BeautifulSoup(open(MOCK_CF),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(content, 'h2',{'class':'separator'}, "Liste des états préjudiciables")

SOURCE = "MJ"

condition = {'Source':SOURCE}
newObj = False
advantage = False
descr = ""
descrHTML = ""

for s in section:
    if s.name == 'h2':
        condition['Description'] = descr.strip()
        condition['DescriptionHTML'] = descrHTML.strip()
        liste.append(condition)
        
        # avantages
        SOURCE = "AM"
        condition = {'Source':SOURCE}
        newObj = False
        advantage = True
        descr = ""
        descrHTML = ""
        
    elif s.name == 'h3':
        if newObj:
            condition['Description'] = descr.strip()
            condition['DescriptionHTML'] = descrHTML.strip()
            liste.append(condition)
            condition = {'Source':SOURCE}
        descr = ""
        descrHTML = ""
        condition['Nom'] = s.text.replace('¶','').strip()
        if advantage:
            condition['Nom'] += " (avantage)"
        newObj = True
        
        condition['Référence']= URL + s.find('a')['href']
                
    else:
        descr += html2text(s)
        descrHTML += html2text(s, True, 2)

## last element
condition['Description'] = descr.strip()
condition['DescriptionHTML'] = descrHTML.strip()
liste.append(condition)
            
print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/conditions.yml", MATCH, FIELDS, HEADER, liste)
