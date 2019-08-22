#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, getValidSource, mergeYAML

## Configurations pour le lancement
MOCK_LIST = None
MOCK_SORT = None
#MOCK_LIST = "mocks/sortsListeA.html" # décommenter pour tester avec une liste pré-téléchargée
#MOCK_SORT = "mocks/sort1.html"       # décommenter pour tester avec un sort pré-téléchargé

URLs = ["http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts.ashx",
       "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts%20(suite).ashx",
       "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts%20(fin).ashx"]

FIELDS = ['Nom', 'École', 'Niveau', 'Portée', 'Cible ou zone d\'effet', 'Temps d\'incantation', 'Composantes', 'Durée', 'Jet de sauvegarde', 'Résistance à la magie', 'Description', 'Source', 'Référence' ]
MATCH = ['Nom']



liste = []

print("Extraction des sorts...")

list = []
if MOCK_LIST:
    parsed_html = BeautifulSoup(open(MOCK_LIST),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_all('li')
else:
    list = []
    for u in URLs:
        parsed_html = BeautifulSoup(urllib.request.urlopen(u).read(),features="lxml")
        list += parsed_html.body.find(id='PageContentDiv').find_all('li')

#
# cette fonction se charge d'extraire le texte de la partie HTML
# en explorant certaines balises. Malheureusement, le format des
# pages peut différer d'une fois à l'autre.
#
def extractText(list):
    text = ""
    for el in list:
        text += html2text(el)
    return text

# itération sur chaque page
for l in list:
    sort = {}
    
    element = l.find_next('a')
    title = element.get('title')
    link  = element.get('href')
    
    source = None
    sourceEl = element.find_next('i')
    if sourceEl.string:
        source_search = re.search('\((.*)\)', sourceEl.string, re.IGNORECASE)
        if source_search:
            source = getValidSource(source_search.group(1))
    
    if not source:
        source = "MJ"
    
    print("Sort %s (%s)" % (title, source))
    pageURL = "http://www.pathfinder-fr.org/Wiki/" + link
    
    sort[u'Nom']=title
    sort[u'Référence']=pageURL
    sort[u'Source']=source
    
    if MOCK_SORT:
        content = BeautifulSoup(open(MOCK_SORT),features="lxml").body.find(id='PageContentDiv')
    else:
        content = BeautifulSoup(urllib.request.urlopen(pageURL).read(),features="lxml").body.find(id='PageContentDiv')
    
    # lire les attributs
    text = ""
    for attr in content.find_all('b'):
        key = attr.text.strip()
        
        for s in attr.next_siblings:
            #print "%s %s" % (key,s.name)
            if s.name == 'b' or  s.name == 'br':
                break
            elif s.string:
                text += s.string

        # convertir les propriétés qui sont similaires
        if "cible" in key.lower() or "effet" in key.lower() or "cible" in key.lower() or "zone" in key.lower():
            key = "Cible ou zone d'effet"
        key = key.replace("’","'")

        if key in FIELDS:
            sort[key]=text.strip()
            descr = s.next_siblings
            text = ""
        else:
            print("- Skipping unknown property %s" % key)

    # lire la description
    text = extractText(descr)
    sort['Description']=text.strip()
    
    # ajouter sort
    liste.append(sort)
    
    if MOCK_SORT:
        break

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/spells.yml", MATCH, FIELDS, HEADER, liste)
