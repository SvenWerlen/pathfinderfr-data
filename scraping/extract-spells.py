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
MOCK_LIST = "mocks/sorts-chaman.html" # décommenter pour tester avec une liste pré-téléchargée
#MOCK_SORT = "mocks/sort1.html"       # décommenter pour tester avec un sort pré-téléchargé

URLs = [#{'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts.ashx", 'list': False},
        #{'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts%20(suite).ashx", 'list': False},
        #{'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts%20(fin).ashx", 'list': False},
        {'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.liste%20des%20sorts%20de%20chaman.ashx", 'list': True}]

FIELDS = ['Nom', 'École', 'Niveau', 'Portée', 'Cible ou zone d\'effet', 'Temps d\'incantation', 'Composantes', 'Durée', 'Jet de sauvegarde', 'Résistance à la magie', 'Description', 'Source', 'Référence' ]
MATCH = ['Référence']
IGNORE = ['Source']



liste = []

print("Extraction des sorts...")

listSorts = []    
for u in URLs:
    if MOCK_LIST:
        parsed_html = BeautifulSoup(open(MOCK_LIST),features="lxml").find(id='PageContentDiv')
    else:
        parsed_html = BeautifulSoup(urllib.request.urlopen(u['URL']).read(),features="lxml").find(id='PageContentDiv')
    
    if u['list']:
        for el in parsed_html.children:
            if el.name == "ul":
                listSorts += el.find_all('li')
    else:
        listSorts += parsed_html.find_all('li')

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
for l in listSorts:
    sort = {}
    
    element = l.find_next('a')
    title = element.get('title')
    link  = element.get('href')
    
    linkText = element.text
    restText = l.text[len(linkText):]
    
    source = "MJ"
    source_search = re.search('\(([a-zA-Z-]+?)\)', restText, re.IGNORECASE)
    if source_search:
        source = getValidSource(source_search.group(1))
    
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
    
    #if MOCK_SORT:
    #    break

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/spells.yml", MATCH, FIELDS, HEADER, liste, IGNORE)
