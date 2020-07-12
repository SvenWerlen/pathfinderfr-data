#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import html2text, cleanSectionName, extractSource, extractLevel, cleanInlineDescription, mergeYAML

## Configurations pour le lancement
MOCK_BENE = None
#MOCK_BENE = "mocks/benedictions.html"       # décommenter pour tester avec les bénédictions pré-téléchargées

URL = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.B%c3%a9n%c3%a9diction%20de%20lair.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (bénédictions)...")

def extractClassFeature(name, liste, section, baseURL):
    newObj = False
    descr = ""
    descrHTML = ""

    altLink = []
    classfeature = None
    for s in section:
        if s.name == 'h3':
            if newObj:
                classfeature['Description'] = cleanInlineDescription(descr)
                classfeature['DescriptionHTML'] = cleanInlineDescription(descrHTML)
                classfeature['Niveau'] = extractLevel(classfeature['Description'], 150)
                liste.append(classfeature)

            classfeature = {'Auto': False }
            descr = ""
            descrHTML = ""
            newObj = True
            altLink = []
            classfeature['Nom'] = name + ": " + cleanSectionName(s.text)
            classfeature['Classe'] = "Prêtre combattant"
            classfeature['Source'] = 'MJRA'
            classfeature['Référence'] = baseURL + s.find('a')['href']

        else:
            descr += html2text(s)
            descrHTML += html2text(s, True, 2)
    
    if not classfeature:
        return
    
    ## last element
    classfeature['Description'] = cleanInlineDescription(descr)
    classfeature['DescriptionHTML'] = cleanInlineDescription(descrHTML)
    classfeature['Niveau'] = extractLevel(classfeature['Description'], 150)
    liste.append(classfeature)
    
    


if MOCK_BENE:
    content = BeautifulSoup(open(MOCK_BENE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

navigation = content.find('div', {'class':'presentation navmenu'});

URLS = []
for el in navigation.find_all('a'):
    if(el.text.startswith("Bénédiction")):
        URLS.append("https://www.pathfinder-fr.org/Wiki/" + el['href'])

liste = []
for u in URLS:
    
    if MOCK_BENE:
        content = BeautifulSoup(open(MOCK_BENE),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(u).read(),features="lxml").body
    
    name = cleanSectionName(content.find('h1', {'class':'pagetitle'}).text)
    print(" - " + name);
    
    section = content.find('div', {'class':'presentation navmenu'}).next_siblings
    
    extractClassFeature(name, liste, section, u)
    
    if MOCK_BENE:
        break
    
print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
