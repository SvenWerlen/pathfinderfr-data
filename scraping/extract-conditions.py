#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, mergeYAML


## Configurations pour le lancement
URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.%c3%89tats%20pr%c3%a9judiciables.ashx"
MOCK_CF = None
#MOCK_CF = "mocks/conditions.html"       # décommenter pour tester avec les conditions pré-téléchargées

FIELDS = ['Nom', 'Source', 'Description', 'Référence' ]
MATCH = ['Nom']

liste = []

if MOCK_CF:
    content = BeautifulSoup(open(MOCK_CF),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(content, 'h2',{'class':'separator'}, "Liste des états préjudiciables")

SOURCE = "MJ"

condition = {'Source':SOURCE}
newObj = False
advantage = False
descr = ""

for s in section:
    if s.name == 'h2':
        condition['Description'] = descr.replace('\n','').strip()
        liste.append(condition)
        
        # avantages
        SOURCE = "AM"
        condition = {'Source':SOURCE}
        newObj = False
        advantage = True
        descr = ""
        
    elif s.name == 'h3':
        if newObj:
            condition['Description'] = descr.strip()
            liste.append(condition)
            condition = {'Source':SOURCE}
            brCount = 0
        descr = ""
        condition['Nom'] = s.text.replace('¶','').strip()
        if advantage:
            condition['Nom'] += " (avantage)"
        newObj = True
        
        for e in s.children:
            if e.name == 'a':
                condition['Référence']=URL + e['href']
    elif s.name == 'br':
        descr += '\n'
    elif s.name is None or s.name == 'a' or s.name == 'i' or s.name == 'b':
        if s.string is None:
            for s2 in s.children:
                if s2.name is None or s2.name == 'a' or s2.name == 'b' or s2.name == 'i':
                    descr += s2.string
        else:
            descr += s.string
    elif s.name == 'div':
        for s2 in s.children:
            if s2.name is None or s2.name == 'a' or s2.name == 'b' or s2.name == 'i':
                if not s2.string is None:
                    descr += s2.string
    elif s.name == 'ul':
        for s2 in s.children:
            if s2.name == 'li':
                descr += "- " + s2.text + "\n"
    elif s.name == 'center':
        for s2 in s.children:
            if s2.name == 'table':
                for s3 in s2.children:
                    if s3.name == 'tr':
                        descr += "\n- "
                        for s4 in s3.children:
                            if s4.name == 'td':
                                descr += s4.text + " "
        descr += "\n\n"


## last element
condition['Description'] = descr.replace('\n','').strip()
liste.append(condition)
            
print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/conditions.yml", MATCH, FIELDS, HEADER, liste)
