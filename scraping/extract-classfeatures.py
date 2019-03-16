#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

# vérification des paramètres
if len(sys.argv) < 3:
    print("Usage: %s [URL] [NOM]" % sys.argv[0])
    print(" - URL: adresse vers la classe")
    print(" - NOM: nom de la classe")
    exit(1)


## Configurations pour le lancement
MOCK_CF = None
#MOCK_CF = "mocks/classe-ensorceleur.html"       # décommenter pour tester avec les rages pré-téléchargées


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

# vérification des paramètres
if len(sys.argv) < 1:
    print("Usage: %s" % sys.argv[0])
    exit(1)

liste = []


if MOCK_CF:
    content = BeautifulSoup(open(MOCK_CF),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(sys.argv[1]).read(),features="lxml").body

section = jumpTo(html, 'h2',{'class':'separator'}, u"Descriptif de la classe")

classfeature = {'4Source':'MJ','5Niveau':1,'6Auto':'TRUE'}
newObj = False
descr = ""

for s in section:
    if s.name == 'h3':
        if newObj:
            classfeature['2Classe'] = sys.argv[2]
            classfeature['7Description'] = descr.replace('\n','').strip()
            classfeature['EMPTY'] = ""
            liste.append(classfeature)
            classfeature = {'4Source':'MJ','5Niveau':1,'6Auto':'TRUE'}
            brCount = 0
            descr = ""
        classfeature['1Nom'] = s.text.replace('¶','').strip()
        newObj = True
        
        for e in s.children:
            if e.name == 'a':
                classfeature[u'8Référence']="http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.pouvoirs%20de%20rage.ashx" + e['href']
    elif s.name == 'br':
        descr += '\\n'
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

## last element
classfeature['2Classe'] = sys.argv[2]
classfeature['7Description'] = descr.replace('\n','').strip()
classfeature['EMPTY'] = ""
liste.append(classfeature)
            
yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace('1Nom','Nom')
yml = yml.replace('2Classe','Classe')
yml = yml.replace(u'3Prérequis',u'Prérequis')
yml = yml.replace('4Source','Source')
yml = yml.replace('5Niveau','Niveau')
yml = yml.replace('6Auto','Auto')
yml = yml.replace('\'TRUE\'','True')
yml = yml.replace('7Description','Description')
yml = yml.replace(u'8Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)
