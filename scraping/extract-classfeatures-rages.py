#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, extractLevel, html2text, cleanSectionName, extractSource, mergeYAML

## Configurations pour le lancement
MOCK_RAGE = None
#MOCK_RAGE = "mocks/barbare-rages.html"       # décommenter pour tester avec les rages pré-téléchargées

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.pouvoirs%20de%20rage.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (rages)...")

if MOCK_RAGE:
    content = BeautifulSoup(open(MOCK_RAGE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(content, 'h2',{'class':'separator'}, u"Description des pouvoirs de rage")

source = None
sourceNext = None
for s in section:
    if s.name == 'div':
        rage = {'Source':'MJ','Niveau':1}
        newObj = False
        brCount = 0
        descr = ""
        descrHTML = ""
        for e in s.children:
            if e.name == 'h3':
                if newObj:
                    rage['Classe'] = 'Barbare'
                    rage['Description'] = descr.strip()
                    rage['DescriptionHTML'] = descrHTML
                    if not sourceNext is None:
                        rage['Source'] = sourceNext
                    liste.append(rage)
                    sourceNext = source
                    source = None
                    rage = {'Source':'MJ','Niveau':1}
                    brCount = 0
                    descr = ""
                    descrHTML = ""
                else:
                    sourceNext = source
                rage['Nom'] = "Rage: " + cleanSectionName(e.text)
                rage['Référence'] = URL + e.find_next("a")['href']
                newObj = True
            elif e.name == 'b' and e.text == 'Prérequis':
                prerequis = str(e.next_sibling)
                if prerequis.startswith("'"):
                    prerequis = prerequis[1:]
                m = re.search(',? ?niveau (\d+)', prerequis)
                rage['Niveau'] = extractLevel(prerequis, 300)
                rage['Prérequis']=prerequis.replace(':','').strip()
            elif e.name == 'br':
                brCount+=1
                if(brCount==2 and 'Prérequis' in rage):
                    descr = ""
                    descrHTML = ""
            else:
                descr += html2text(e)
                descrHTML += html2text(e, True, 2)
                if e.name == 'a':
                    src = extractSource(e)
                    if src:
                        source = src
            
        ## last element
        rage['Classe'] = 'Barbare'
        rage['Description'] = descr.strip()
        rage['DescriptionHTML'] = descrHTML
        if not sourceNext is None:
            rage['Source'] = sourceNext
        liste.append(rage)
            

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
