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
MOCK_DOMAINE = None
#MOCK_DOMAINE = "mocks/pretre-domaines.html"       # décommenter pour tester avec les rages pré-téléchargées
#MOCK_DOMAINE_PAGE = "mocks/domain-feu.html"


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
    seps = html.find_all(afterTag, afterCond);
    for s in seps:
        if s.text.lower().strip().startswith(elementText.lower()):
            return s.next_siblings

# vérification des paramètres
if len(sys.argv) < 1:
    print("Usage: %s" % sys.argv[0])
    exit(1)

liste = []


if MOCK_DOMAINE:
    content = BeautifulSoup(open(MOCK_DOMAINE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen("http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.domaines.ashx").read(),features="lxml").body

domaines = content.find("div", {'presentation navmenu'}).find_all("li");
for d in domaines:
    link = d.find("a")
    if link is None:
        break;
    
    domain = {}
    domain['1Nom'] = link.text
    domain['2Classe'] = u"Prêtre"
    domain['4Source'] = "MJ"
    domain['5Niveau'] = 1
    domain['6Description'] = ""
    domain[u'7Référence'] = "http://www.pathfinder-fr.org/Wiki/" + link["href"]
    domain['EMPTY'] = ""
    
    print("Processing: " + link["href"])
    if MOCK_DOMAINE:
        domainHTML = BeautifulSoup(open(MOCK_DOMAINE_PAGE),features="lxml").body
    else:
        domainHTML = BeautifulSoup(urllib.request.urlopen(domain[u'7Référence']).read(),features="lxml").body
    
    pouvoirs = jumpTo(domainHTML, 'h2',{'class':'separator'}, u"Pouvoirs accordés")
    if pouvoirs is None:
        pouvoirs = jumpTo(domainHTML, 'b',{}, u"Pouvoirs accordés")
    if pouvoirs is None:
        print("NOT FOUND!!")
        continue
    for p in pouvoirs:
        if p.name is None or p.name == 'a' or p.name == 'b':
            domain['6Description'] += p.string
        elif(p.name == 'br'):
            domain['6Description'] += '\\n'
        elif(p.name == 'h2'):
            break
    
    domain['6Description'] = domain['6Description'].replace('\n','').strip()
    liste.append(domain)

#exit(1)

yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace('1Nom','Nom')
yml = yml.replace('2Classe','Classe')
yml = yml.replace('4Source','Source')
yml = yml.replace('5Niveau','Niveau')
yml = yml.replace('6Description','Description')
yml = yml.replace(u'7Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)
