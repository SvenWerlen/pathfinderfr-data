#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
from bs4 import BeautifulSoup
from lxml import html

from libhtml import html2text, mergeYAML

## Configurations pour le lancement
MOCK_LIST = None
MOCK_COMP = None
#MOCK_LIST = "mocks/compsListe.html" # décommenter pour tester avec une liste pré-téléchargée
#MOCK_COMP = "mocks/comp2.html"       # décommenter pour tester avec un sort pré-téléchargé

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tableau%20r%c3%a9capitulatif%20des%20comp%c3%a9tences.ashx"

PROPERTIES = [ "Caractéristique associée", "caractéristique associée", "Formation nécessaire", "Formation nécesssaire", "Malus d’armure"]

FIELDS = ['Nom', 'Caractéristique associée', 'Malus d’armure', 'Formation nécessaire', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom']


liste = []


list = []
if MOCK_LIST:
    parsed_html = BeautifulSoup(open(MOCK_LIST),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_next('table',class_="tablo").find_all('tr')
else:
    parsed_html = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml")
    list += parsed_html.body.find(id='PageContentDiv').find_next('table',class_="tablo").find_all('tr')

#
# cette fonction se charge d'extraire le texte de la partie HTML
# en explorant certaines balises. Malheureusement, le format des
# pages peut différer d'une fois à l'autre.
#
def extractText(list):
    text = ""
    html = ""
    for el in list:
        text += html2text(el, True, 1)
        html += html2text(el, True, 2)
    return { 'text': text, 'html': html }


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

    
    print("Processing %s" % title)
    pageURL = "http://www.pathfinder-fr.org/Wiki/" + link
    
    sort['Nom']=title
    sort['Référence']=pageURL
    
    if MOCK_COMP:
        content = BeautifulSoup(open(MOCK_COMP),features="lxml").body.find(id='PageContentDiv')
    else:
        content = BeautifulSoup(urllib.request.urlopen(pageURL).read(),features="lxml").body.find(id='PageContentDiv')
    
    # lire les attributs
    text = ""
    descr = ""
    for attr in content.find_all('b'):
        key = attr.text.strip()
        
        for s in attr.next_siblings:
            #print("%s %s" % (key,s.name))
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
            if key == "Formation nécesssaire":
                key = "Formation nécessaire"
            elif key == "caractéristique associée":
                key = "Caractéristique associée"
            
            sort[key]=text
            descr = s.next_siblings
            text = ""
        #else:
        #    print("- Skipping unknown property %s" % key)

    # lire la description
    descriptions = extractText(descr)
    sort['Description']=descriptions['text'].strip()
    sort['DescriptionHTML']=descriptions['html']
    
    # ajouter sort
    liste.append(sort)
    
    if MOCK_COMP:
        break

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/competences.yml", MATCH, FIELDS, HEADER, liste)
