#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanLabel, cleanInlineDescription, mergeYAML

## Configurations pour le lancement
MOCK_DECOUVERTE = None
#MOCK_DECOUVERTE = "mocks/decouvertes.html"       # décommenter pour tester avec les découvertes pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.d%c3%a9couvertes.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'Référence' ]
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
source = 'MJRA'
for s in section:
    for el in s.children:
        if el.name == "b":
            nom = cleanLabel(el.text)
            
            if newObj:
                decouverte['Classe'] = 'Alchimiste'
                decouverte['Description'] = cleanInlineDescription(descr)
                liste.append(decouverte)
                decouverte = {'Niveau':1}

            descr = ""
            decouverte['Nom'] = "Découverte: " + nom
            decouverte['Source'] = source
            decouverte['Référence'] = reference
            source = "MJRA"
            newObj = True
        
        elif el.name is None or el.name == 'a':
            descr += el.string
        elif el.name == 'div':
            for c in el.children:
                if c.name == 'img':
                    if('logoAPG' in c['src']):
                        source = 'MJRA'
                    elif('logoUC' in c['src']):
                        source = 'AG'
                    elif('logoMR' in c['src']):
                        source = 'MR'
                    elif('logoMCA' in c['src']):
                        source = 'MCA'
                    elif('logoUM' in c['src']):
                        source = 'AM'
                    elif('logoMC' in c['src']):
                        source = 'MC'
                    elif('logoOA' in c['src']):
                        source = 'AO'
                    else:
                        print("Invalid source: " + c['src'])
                        exit(1)
                elif c.name == 'a':
                    reference=URL + c['href']

# last element        
decouverte['Classe'] = 'Alchimiste'
decouverte['Description'] = cleanInlineDescription(descr)
liste.append(decouverte)


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
