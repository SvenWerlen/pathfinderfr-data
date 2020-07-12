#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanLabel, cleanInlineDescription, mergeYAML, extractSource

## Configurations pour le lancement
MOCK_DECOUVERTE = None
#MOCK_DECOUVERTE = "mocks/decouvertes.html"       # décommenter pour tester avec les découvertes pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.d%c3%a9couvertes.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (découvertes)...")


if MOCK_DECOUVERTE:
    content = BeautifulSoup(open(MOCK_DECOUVERTE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = content.find_all('td', width="49%" )

decouverte = {'Niveau':1}
newObj = False
descr = ""
descrHTML = ""
source = 'MJRA'
for s in section:
    for el in s.children:
        if el.name == "b":
            nom = cleanLabel(el.text)
            
            if newObj:
                decouverte['Classe'] = 'Alchimiste'
                decouverte['Description'] = cleanInlineDescription(descr)
                decouverte['DescriptionHTML'] = cleanInlineDescription(descrHTML)
                liste.append(decouverte)
                decouverte = {'Niveau':1}

            descr = ""
            descrHTML = ""
            decouverte['Nom'] = "Découverte: " + nom
            decouverte['Source'] = source
            decouverte['Référence'] = reference
            source = "MJRA"
            newObj = True
        
        else:
            descr += html2text(el)
            descrHTML += html2text(el, True, 2)
            if el.name == 'div' or not el.string:
                src = extractSource(el)
                if src:
                  source = src
                for c in el.children:
                    if c.name == 'a':
                        reference=URL + c['href']

# last element        
decouverte['Classe'] = 'Alchimiste'
decouverte['Description'] = cleanInlineDescription(descr)
decouverte['DescriptionHTML'] = cleanInlineDescription(descrHTML)
liste.append(decouverte)


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
