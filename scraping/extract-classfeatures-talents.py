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
#MOCK_TALENT = "mocks/roublard-talents.html"       # décommenter pour tester avec les talents pré-téléchargées

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

        talent = {'Source':'MJ','Niveau':level}
        newObj = False
        brCount = 0
        descr = ""
        for e in s.children:
            if e.name == 'h3':
                if newObj:
                    talent['Classe'] = 'Roublard'
                    talent['Description'] = descr.strip()
                    liste.append(talent)
                    talent = {'Source':'MJ','Niveau':level}
                    brCount = 0
                    descr = ""
                talent['Nom'] = "Talent: " + cleanSectionName(e.text)
                talent['Référence'] = URL + e.find_next("a")['href']
                newObj = True
            elif e.name == 'br':
                brCount+=1
                if(brCount==2 and u'Prérequis' in talent):
                    descr = ""
                    
            else:
                descr += html2text(e, False)
                if e.name == 'div' or e.name == 'a':
                    src = extractSource(e)
                    if not src is None:
                        talent['Source'] = src            
        
        ## last element
        talent['Classe'] = 'Roublard'
        talent['Description'] = descr.strip()
        liste.append(talent)
            
print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
