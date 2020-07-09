#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import cleanLabel, cleanSectionName, cleanInlineDescription, cleanDescription, extractSource, html2text, jumpTo, findProperty, mergeYAML

## Configurations pour le lancement
MOCK_REVELATION = None
MOCK_REVELATION_SUB = None
#MOCK_REVELATION = "mocks/revelations.html"       # décommenter pour tester avec les révélations pré-téléchargées
#MOCK_REVELATION_SUB = "mocks/mysteres-hiver.html"

URL = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Myst%c3%a8re%20des%20anc%c3%aatres.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (révélations)...")


if MOCK_REVELATION:
    content = BeautifulSoup(open(MOCK_REVELATION),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body


navigation = content.find('div', {'class':'presentation navmenudroite'});

URLS = []
for el in navigation.find_all('a'):
    if(el.text.startswith("Mystère")):
        URLS.append("https://www.pathfinder-fr.org/Wiki/" + el['href'])
        

for u in URLS:

    if MOCK_REVELATION_SUB:
        content = BeautifulSoup(open(MOCK_REVELATION_SUB),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(u).read(),features="lxml").body

    name = cleanSectionName(content.find('h1', {'class':'pagetitle'}).text)
    print(" - " + name);

    # extraire informations sur mystère
    description = ""
    source = "MJ"
    for el in content.find('div', {'id': 'PageContentDiv'}):
        if el.name == "h2":
            break
        else:
            description += html2text(el)
            if el.name == "a" or el.name == "div":
              src = extractSource(el)
              if src:
                source = src
    
    benediction = {}
    benediction['Nom'] = name
    benediction['Classe'] = 'Oracle'
    benediction['Niveau'] = 1
    benediction['Auto'] = False
    benediction['Description'] = cleanDescription(description)
    benediction['Source'] = source
    benediction['Référence'] = u
    liste.append(benediction)

    section = jumpTo(content, 'h2', {'class':'separator'}, 'Révélations')
    
    if not section:
        print('Aucune section "Révélations" trouvée!');
        exit(1)
        
    descr = ""
    for el in section:
    
        if el.name == "b":
            benedictionName = cleanLabel(el.text)
            benediction = {}
            benediction['Nom'] = name + ": " + benedictionName
            benediction['Classe'] = 'Oracle'
            benediction['Niveau'] = 1
            benediction['Auto'] = False
            if benedictionName == "Révélation finale":
                benediction['Niveau'] = 20
            benediction['Description'] = cleanInlineDescription(findProperty(jumpTo(content, 'h2', {'class':'separator'}, 'Révélations'), benedictionName))
            benediction['Source'] = source
            benediction['Référence'] = u
            
            if benediction['Description'] is None:
                print("Description invalide pour: " + benediction['Nom']);
                exit(1)
            
            liste.append(benediction)
            
    if MOCK_REVELATION:
        break

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)

