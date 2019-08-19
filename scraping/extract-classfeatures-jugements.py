#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import extractSource, html2text, cleanSectionName, cleanInlineDescription, mergeYAML

## Configurations pour le lancement
MOCK_JUGEMENT = None
#MOCK_JUGEMENT = "mocks/jugements.html"       # décommenter pour tester avec les jugements pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.jugements.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (jugements)...")


if MOCK_JUGEMENT:
    content = BeautifulSoup(open(MOCK_JUGEMENT),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = content.find(id='PageContentDiv').children

jugement = {'Niveau':1, 'Auto': True}
newObj = False
descr = ""
source = 'MJRA'
for el in section:
    if el.name == "h3":
        nom = cleanSectionName(el.text)
        reference = URL + el.find_next("a")['href']

        if newObj:
            jugement['Classe'] = 'Inquisiteur'
            jugement['Description'] = cleanInlineDescription(descr)
            liste.append(jugement)
            jugement = {'Niveau':1, 'Auto': True}
            
        descr = ""
        jugement['Nom'] = "Jugement: " + nom
        jugement['Source'] = source
        jugement['Référence'] = reference
        source = "MJRA"
        newObj = True
    
    elif el.name == 'div':
        src = extractSource(el)
        if not src is None:
            source = src
    
    else:
        descr += html2text(el)

# last element        
jugement['Classe'] = 'Inquisiteur'
jugement['Description'] = descr.replace('\n','').strip()
liste.append(jugement)


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
