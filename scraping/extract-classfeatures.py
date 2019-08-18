#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanSectionName, cleanInlineDescription, extractLevel, mergeYAML

## Configurations pour le lancement
MOCK_CF = None
#MOCK_CF = "mocks/classe-maitre-espion.html"       # décommenter pour tester avec les rages pré-téléchargées

FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']


classes = []
with open("../data/classes.yml", 'r') as stream:
    try:
        classes = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

liste = []

print("Extraction des aptitude...")

for cl in classes:

    print("Extraction des aptitudes de '%s' ..." % cl['Nom'])

    if MOCK_CF:
        content = BeautifulSoup(open(MOCK_CF),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(cl['Référence']).read(),features="lxml").body

    sectionNames = ["Descriptif de la classe", "Caractéristiques de la classe", "Caractéristiques de classe"]
    section = None
    for s in sectionNames:
        section = jumpTo(content, 'h2',{'class':'separator'}, s)
        if section:
            break

    classfeature = {'Auto': True }
    newObj = False
    descr = ""

    if not section:
        print("- Section Description/Caractéristiques pour la classe %s n'a pas être trouvée!!!" % cl['Nom'])
        continue

    for s in section:
        if s.name == 'h3':
            if newObj:
                classfeature['Description'] = cleanInlineDescription(descr)
                classfeature['Niveau'] = extractLevel(classfeature['Description'], 150)
                liste.append(classfeature)
                classfeature = {'Auto': True }
                descr = ""
                
            newObj = True
            classfeature['Nom'] = cleanSectionName(s.text)
            classfeature['Classe'] = cl['Nom']
            classfeature['Source'] = cl['Source']
            classfeature['Référence'] = cl['Référence'] + s.find('a')['href']
            
        else:
            descr += html2text(s)

    ## last element
    classfeature['Description'] = cleanInlineDescription(descr)
    classfeature['Niveau'] = extractLevel(classfeature['Description'], 150)
    liste.append(classfeature)
    
    if MOCK_CF:
        break

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
