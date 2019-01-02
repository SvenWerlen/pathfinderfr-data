#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import yaml
import sys
from lxml import html
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
    from bs4 import NavigableString

## Configurations pour le lancement
MOCK_LIST = "mocks/sortsListeA.html" # décommenter pour tester avec une liste pré-téléchargée
MOCK_SORT = "mocks/sort1.html"       # décommenter pour tester avec un sort pré-téléchargé

URLs = ["http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts.ashx",
       "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts%20(suite).ashx",
       "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts%20(fin).ashx"]

PROPERTIES = [ u"Nom", u"École", u"Niveau", u"Portée", u"Cibles", u"Zone", u"Zone d'effet", u"Effet", u"Temps d’incantation", u"Temps d'incantation", u"Composantes", u"Cible", u"Durée", u"Jet de sauvegarde", u"Résistance à la magie", u"Description"]

# vérification des paramètres
if len(sys.argv) < 2:
    print "Usage: %s [HTML|TEXT]" % sys.argv[0]
    print " - HTML: contenu extrait en tant que HTML"
    print " - TEXT: contenu extrait en tant que TEXT"
    exit(1)

# message d'accueil
html = sys.argv[1].lower() == "html"
if html:
    print "Génération du fichier YAML pour les sorts en mode HTML"
else:
    print "Génération du fichier YAML pour les sorts en mode TEXT"



liste = []


list = []
if MOCK_LIST:
    parsed_html = BeautifulSoup(open(MOCK_LIST),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_all('li')
else:
    list = []
    for u in URLs:
        parsed_html = BeautifulSoup(urllib.urlopen(u).read(),features="lxml")
        list += parsed_html.body.find(id='PageContentDiv').find_all('li')

#
# cette fonction se charge d'extraire le texte de la partie HTML
# en explorant certaines balises. Malheureusement, le format des
# pages peut différer d'une fois à l'autre.
#
def extractText(list):
    text = ""
    
    for el in list:
        
        if html:
            text += repr(el)
            continue
        
        if el.name == 'br':
            if text[-2:] != '\n\n':
                text += '\n'
        elif el.name in ('b','h2','h3'):
            if el.string:
                text += ' ' + el.string.strip().upper()
            else:
                text += ' ' + extractText(el.contents).upper()
        elif el.string:
            text += ' ' + el.string.strip()
        elif el.name in ('div','ul','li','i','a'):
            if el.name == 'li':
                text += '\n *'
            text += ' ' + extractText(el.contents)
        elif el.name in ('img'):
            # do nothing
            text
        else:
            print " - HTML element %s ignored!" % el.name

    return text.strip(' ').replace(u'¶','')


# itération sur chaque page
for l in list:
    sort = {}
    
    element = l.find_next('a')
    title = element.get('title')
    link  = element.get('href')
    
    print "Processing %s" % title
    pageURL = "http://www.pathfinder-fr.org/Wiki/" + link
    
    sort['Nom']=title
    sort['Reference']=pageURL
    
    if MOCK_SORT:
        content = BeautifulSoup(open(MOCK_SORT),features="lxml").body.find(id='PageContentDiv')
    else:
        content = BeautifulSoup(urllib.urlopen(pageURL).read(),features="lxml").body.find(id='PageContentDiv')
    
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

        if key in PROPERTIES:
            sort[key]=text.strip()
            descr = s.next_siblings
            text = ""
        else:
            print "- Skipping unknown property %s" % key

    # lire la description
    text = extractText(descr)
    
    sort['Description']=text.strip()
    
    # ajouter sort
    liste.append(sort)
    
    if MOCK_SORT:
        break

if MOCK_SORT:
    print yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
    exit(1)

with open("sorts.yml", "w") as f:
    yaml.safe_dump(liste, f, default_flow_style=False, allow_unicode=True)
