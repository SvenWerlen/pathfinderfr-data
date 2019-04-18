#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html


## Configurations pour le lancement
URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.%c3%89tats%20pr%c3%a9judiciables.ashx"
MOCK_CF = None
MOCK_CF = "mocks/conditions.html"       # décommenter pour tester avec les conditions pré-téléchargées


#
# cette fonction extrait le texte du prochain élément après ...
#
def findAfter(html, afterTag, afterCond, searched):
    elements = html.find_next(afterTag, afterCond).next_siblings
    for el in elements:
        if el.name == searched:
            return el.text.strip()

#
# cette fonction extrait le texte pour une propriété <b>propriété</b> en prenant le texte qui suit
#
def findProperty(html, propName):
    for el in html:
        if el.name == 'b' and el.text.lower().startswith(propName.lower()):
            value = ""
            for e in el.next_siblings:
                if e.name == 'br':
                    break
                elif e.string:
                    value += e.string
                else:
                    value += e
            return value.replace('.','').strip()
    return None

#
# cette fonction permet de sauter à l'élément recherché et retourne les prochains éléments
#
def jumpTo(html, afterTag, afterCond, elementText):
    seps = content.find_all(afterTag, afterCond);
    for s in seps:
        if s.text.lower().strip().startswith(elementText.lower()):
            return s.next_siblings

liste = []


if MOCK_CF:
    content = BeautifulSoup(open(MOCK_CF),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(html, 'h2',{'class':'separator'}, u"Liste des états préjudiciables")


SOURCE = "MJ"

condition = {'4Source':SOURCE}
newObj = False
advantage = False
descr = ""

for s in section:
    if s.name == 'h2':
        condition['7Description'] = descr.replace('\n','').strip()
        condition['EMPTY'] = ""
        liste.append(condition)
        
        # avantages
        SOURCE = "AM"
        condition = {'4Source':SOURCE}
        newObj = False
        advantage = True
        descr = ""
        
    elif s.name == 'h3':
        if newObj:
            condition['7Description'] = descr.strip()
            condition['EMPTY'] = ""
            liste.append(condition)
            condition = {'4Source':SOURCE}
            brCount = 0
        descr = ""
        condition['1Nom'] = s.text.replace('¶','').strip()
        if advantage:
            condition['1Nom'] += u" (avantage)"
        newObj = True
        
        for e in s.children:
            if e.name == 'a':
                condition[u'8Référence']=URL + e['href']
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
condition['7Description'] = descr.replace('\n','').strip()
condition['EMPTY'] = ""
liste.append(condition)
            
yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace('1Nom','Nom')
yml = yml.replace('4Source','Source')
yml = yml.replace('7Description','Description')
yml = yml.replace(u'8Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)
