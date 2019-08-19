#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanSectionName, extractSource, mergeYAML

## Configurations pour le lancement
MOCK_ORDRE = None
#MOCK_ORDRE = "mocks/ordres.html"       # décommenter pour tester avec les ordres pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.ordres.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (ordres)...")



if MOCK_ORDRE:
    content = BeautifulSoup(open(MOCK_ORDRE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(content, 'h2',{'class':'separator'}, u"Ordres de chevalier")

ordre = {'Niveau':1}
newObj = False
descr = ""
source = 'MJRA'
for el in section:
    if el.name == "h2":
        break
        
    if el.name == "h3":
        nom = cleanSectionName(el.text)
        reference = URL + el.find_next("a")['href']

        if newObj:
            ordre['Classe'] = 'Chevalier'
            ordre['Description'] = descr.strip()
            liste.append(ordre)
            ordre = {'Niveau':1}
            descr = ""

        ordre['Nom'] = nom
        ordre['Source'] = source
        source = 'MJRA'
        ordre['Référence'] = reference
        newObj = True
    
    elif el.name == 'div':
        src = extractSource(el)
        if not src is None:
            source = src
    
    else:
        descr += html2text(el)
        
# last element        
ordre['Classe'] = 'Chevalier'
ordre['Description'] = descr.strip()
liste.append(ordre)

section = jumpTo(content, 'h2',{'class':'separator'}, "Ordres de Samouraï")

ordre = {'Niveau':1}
newObj = False
descr = ""
source = 'MJRA'
for el in section:
    if el.name == "h2":
        break
        
    if el.name == "h3":
        nom = cleanSectionName(el.text)
        reference = URL + el.find_next("a")['href']

        if newObj:
            ordre['Classe'] = 'Samouraï'
            ordre['Description'] = descr.strip()
            liste.append(ordre)
            ordre = {'Niveau':1}
            descr = ""

        ordre['Nom'] = nom
        ordre['Source'] = source
        source = 'MJRA'
        ordre['Référence'] = reference
        newObj = True
    
    elif el.name == 'div':
        src = extractSource(el)
        if not src is None:
            source = src
    
    else:
        descr += html2text(el)
        
# last element        
ordre['Classe'] = 'Samouraï'
ordre['Description'] = descr.strip()
liste.append(ordre)


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
