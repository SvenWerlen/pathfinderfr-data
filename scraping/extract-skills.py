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
MOCK_LIST = None
MOCK_COMP = None
#MOCK_LIST = "mocks/compsListe.html" # décommenter pour tester avec une liste pré-téléchargée
#MOCK_COMP = "mocks/comp2.html"       # décommenter pour tester avec un sort pré-téléchargé

URLs = ["http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tableau%20r%c3%a9capitulatif%20des%20comp%c3%a9tences.ashx"]

PROPERTIES = [ u"Caractéristique associée", u"caractéristique associée", u"Formation nécessaire", u"Formation nécesssaire", u"Malus d’armure"]

# vérification des paramètres
if len(sys.argv) < 2:
    print "Usage: %s [HTML|TEXT]" % sys.argv[0]
    print " - HTML: contenu extrait en tant que HTML"
    print " - TEXT: contenu extrait en tant que TEXT"
    exit(1)

# message d'accueil
html = sys.argv[1].lower() == "html"
if html:
    print "Génération du fichier YAML pour les compétences en mode HTML"
else:
    print "Génération du fichier YAML pour les compétences en mode TEXT"



liste = []


list = []
if MOCK_LIST:
    parsed_html = BeautifulSoup(open(MOCK_LIST),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_next('table',class_="tablo").find_all('tr')
else:
    list = []
    for u in URLs:
        parsed_html = BeautifulSoup(urllib.urlopen(u).read(),features="lxml")
        list += parsed_html.body.find(id='PageContentDiv').find_next('table',class_="tablo").find_all('tr')

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
        elif el.name == 'i':
            text += el.text
        elif el.name == 'b':
            if el.string:
                text += ' ' + el.string.strip().upper()
            else:
                text += ' ' + extractText(el.contents).upper()
        elif el.name in ('h2','h3'):
            break
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
    title = element.text
    link  = element.get('href')
    
    if element.next_sibling != None:
        title += element.next_sibling
    
    # ugly fix to ignore "headers"
    if title == "Barb":
        continue

    
    print "Processing %s" % title
    pageURL = "http://www.pathfinder-fr.org/Wiki/" + link
    
    sort['Nom']=title
    sort['Référence']=pageURL
    
    if MOCK_COMP:
        content = BeautifulSoup(open(MOCK_COMP),features="lxml").body.find(id='PageContentDiv')
    else:
        content = BeautifulSoup(urllib.urlopen(pageURL).read(),features="lxml").body.find(id='PageContentDiv')
    
    # lire les attributs
    text = ""
    descr = ""
    for attr in content.find_all('b'):
        key = attr.text.strip()
        
        for s in attr.next_siblings:
            #print "%s %s" % (key,s.name)
            if s.name == 'b' or  s.name == 'br':
                break
            elif s.string:
                text += s.string

        # clean text
        text = text.strip()
        if text.startswith(": "):
            text = text[2:]

        if key in PROPERTIES:
            # merge properties with almost the same name
            if key == u"Formation nécesssaire":
                key = u"Formation nécessaire"
            elif key == u"caractéristique associée":
                key = u"Caractéristique associée"
            
            sort[key]=text
            descr = s.next_siblings
            text = ""
        #else:
        #    print "- Skipping unknown property %s" % key

    # lire la description
    text = extractText(descr)
    
    sort['Description']=text.strip()
    
    # ajouter sort
    liste.append(sort)
    
    if MOCK_COMP:
        break

if MOCK_COMP:
    print yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
    exit(1)

with open("competences.yml", "w") as f:
    yaml.safe_dump(liste, f, default_flow_style=False, allow_unicode=True)
