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
MOCK_INQUISITION = None
#MOCK_INQUISITION = "mocks/inquisitions.html"       # décommenter pour tester avec les inquisitions pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.inquisitions.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (inquisitions)...")


if MOCK_INQUISITION:
    content = BeautifulSoup(open(MOCK_INQUISITION),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = content.find(id='PageContentDiv').children

inquisition = {'Niveau':1}
newObj = False
descr = ""
descrHTML = ""
source = 'AM'
for el in section:
    if el.name == "h2":
        nom = cleanSectionName(el.text)
        reference = URL + el.find_next("a")['href']

        if newObj:
            inquisition['Classe'] = 'Inquisiteur'
            inquisition['Description'] = descr.strip()
            inquisition['DescriptionHTML'] = descrHTML.strip()
            liste.append(inquisition)
            inquisition = {'Niveau':1}
            descr = ""
            descrHTML = ""

        inquisition['Nom'] = nom
        inquisition['Source'] = source
        source = 'AM'
        inquisition[u'Référence'] = reference
        newObj = True
    
    elif el.name == 'div':
        src = extractSource(el)
        if not src is None:
            source = src
    
    else:
        descr += html2text(el)
        descrHTML += html2text(el, True, 2)
    
    
        
# last element        
inquisition['Classe'] = 'Inquisiteur'
inquisition['Description'] = descr.strip()
inquisition['DescriptionHTML'] = descrHTML.strip()
liste.append(inquisition)


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)

