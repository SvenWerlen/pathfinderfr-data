#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanSectionName, cleanInlineDescription, mergeYAML

## Configurations pour le lancement
MOCK_MALEFICE = None
#MOCK_MALEFICE = "mocks/malefices.html"       # décommenter pour tester avec les maléfices pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.mal%c3%a9fices.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (maléfices)...")

if MOCK_MALEFICE:
    content = BeautifulSoup(open(MOCK_MALEFICE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(content, 'h2',{'class':'separator'}, u"Maléfices")

LVL = 1
malefice = {'Niveau':LVL}
newObj = False
descr = ""
descrHTML = ""
source = 'MJRA'
for s in section:
    if s.name == 'h2' and "Maléfices majeurs" in s.text:
        LVL = 10
    elif s.name == 'h2' and "Grands maléfices" in s.text:
        LVL = 18
    elif s.name == "table":
        for td in s.find_all('td'):
            for el in td.children:
                if el.name == "h3":
                    nom = cleanSectionName(el.text)
                    reference = URL + el.find_next("a")['href']

                    if newObj:
                        malefice['Classe'] = 'Sorcière'
                        malefice['Description'] = descr.strip()
                        malefice['DescriptionHTML'] = descrHTML
                        liste.append(malefice)
                        malefice = {'Niveau':LVL}
                        
                    descr = ""
                    descrHTML = ""
                    malefice['Nom'] = "Maléfice: " + nom
                    malefice['Source'] = source
                    malefice['Référence'] = reference
                    source = "MJRA"
                    newObj = True
                
                else:
                    descr += html2text(el)
                    descrHTML += html2text(el, True, 2)
    

# last element        
malefice['Classe'] = 'Sorcière'
malefice['Description'] = descr.strip()
malefice['DescriptionHTML'] = descrHTML
liste.append(malefice)



print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
