#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanInlineDescription, cleanSectionName, extractSource, mergeYAML

## Configurations pour le lancement
MOCK_TALENT = None
#MOCK_TALENT = "mocks/roublard-talents.html"       # décommenter pour tester avec les rages pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.talents.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (talents)...")


if MOCK_TALENT:
    content = BeautifulSoup(open(MOCK_TALENT),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(content, 'h2',{'class':'separator'}, u"Description des talents de roublard")

level = 0
for s in section:
 
    if s.name == 'div' and s.has_attr('class') and "article_2col" in s['class']:
        level = 2 if level == 0 else 10

        rage = {'Source':'MJ','Niveau':level}
        newObj = False
        brCount = 0
        descr = ""
        for e in s.children:
            if e.name == 'h3':
                if newObj:
                    rage['Classe'] = 'Roublard'
                    rage['Description'] = descr.strip()
                    liste.append(rage)
                    rage = {'Source':'MJ','Niveau':level}
                    brCount = 0
                    descr = ""
                rage['Nom'] = "Talent: " + cleanSectionName(e.text)
                rage['Référence'] = URL + e.find_next("a")['href']
                newObj = True
            elif e.name == 'br':
                brCount+=1
                if(brCount==2 and u'Prérequis' in rage):
                    descr = ""
                    
            elif e.name == 'div' and not e.has_attr('class'):
                src = extractSource(e)
                if not src is None:
                    rage['Source'] = src
            
            else:
                descr += html2text(e)
            
        
        ## last element
        rage['Classe'] = 'Roublard'
        rage['Description'] = descr.strip()
        liste.append(rage)
            
print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
