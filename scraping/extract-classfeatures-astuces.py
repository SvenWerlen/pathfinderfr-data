#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanSectionName, mergeYAML

## Configurations pour le lancement
MOCK_ASTUCE = None
#MOCK_ASTUCE = "mocks/astuces.html"       # décommenter pour tester avec les astuces pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.astuces.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (astuces)...")

if MOCK_ASTUCE:
    content = BeautifulSoup(open(MOCK_ASTUCE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(content, 'h2',{'class':'separator'}, "Description des astuces de ninja")

LVL = 2
astuce = {'Niveau':LVL}
newObj = False
descr = ""
source = 'AG'
for s in section:
    if s.name == 'h2' and "Description des astuces de maître" in s.text:
        LVL = 10
    elif s.name == "table":
        for td in s.find_all('td'):
            for el in td.children:
                if el.name == "h3":
                    nom = cleanSectionName(el.text)
                    reference = URL + el.find_next("a")['href']
                    
                    if newObj:
                        astuce['Classe'] = 'Ninja'
                        astuce['Description'] = descr.strip()
                        liste.append(astuce)
                        astuce = {'Niveau':LVL}
                        
                    descr = ""
                    astuce['Nom'] = u"Astuce: " + nom
                    astuce['Source'] = source
                    astuce['Référence'] = reference
                    source = "AG"
                    newObj = True
                
                else:
                    descr += html2text(el)
    

# last element        
astuce['Classe'] = 'Ninja'
astuce['Description'] = descr.strip()
liste.append(astuce)



print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
