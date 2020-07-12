#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import html2text, cleanSectionName, cleanInlineDescription, mergeYAML

## Configurations pour le lancement
MOCK_ARCANE = None
#MOCK_ARCANE = "mocks/arcanes.html"       # décommenter pour tester avec les arcanes pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.arcanes.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (arcanes)...")

if MOCK_ARCANE:
    content = BeautifulSoup(open(MOCK_ARCANE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = content.find_all("div",{'class':['article_2col']})

LVL = 3
arcane = {'Niveau':LVL}
newObj = False
descr = ""
descrHTML = ""
source = 'AM'

for s in section:
    for el in s.children:
        if el.name == "h3":
            nom = cleanSectionName(el.text)
            reference = URL + el.find_next("a")['href']

            if newObj:
                arcane['Classe'] = 'Magus'
                arcane['Description'] = cleanInlineDescription(descr)
                arcane['DescriptionHTML'] = cleanInlineDescription(descrHTML)
                liste.append(arcane)
                arcane = {'Niveau':LVL}
                
            descr = ""
            descrHTML = ""
            arcane['Nom'] = "Arcane: " + nom
            arcane['Source'] = source
            arcane['Référence'] = reference
            source = "AM"
            newObj = True
        
        else:
            descr += html2text(el)
            descrHTML += html2text(el, True, 2)
    

# last element        
arcane['Classe'] = 'Magus'
arcane['Description'] = cleanInlineDescription(descr)
liste.append(arcane)


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
