#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import cleanSectionName, mergeYAML

## Configurations pour le lancement
MOCK_LIST = None
MOCK_DON = None
#MOCK_LIST = "mocks/donsListe.html"   # décommenter pour tester avec une liste pré-téléchargée
#MOCK_DON  = "mocks/don3.html"        # décommenter pour tester avec un sort pré-téléchargé

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.tableau%20r%c3%a9capitulatif%20des%20dons.ashx"
PROPERTIES = [  "Catégorie", "Catégories", "Conditions", "Condition", "Conditions requises", "Normal", "Avantage", "Avantages", "Spécial", "À noter"]

FIELDS = ['Nom', 'Résumé', 'Catégorie', 'Conditions', 'Avantage', 'Normal', 'Spécial', 'Source', 'Référence' ]
MATCH = ['Nom']

liste = []


list = []
if MOCK_LIST:
    parsed_html = BeautifulSoup(open(MOCK_LIST),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_all('tr')
else:
    parsed_html = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_all('tr')

print("Extraction des dons...")

# itération sur chaque page
for tr in list:
    don = {}
    
    if 'class' in tr.attrs and 'titre' in tr.attrs['class']:
        continue
    
    element = tr.find_next('a')
    title = element.text
    link  = element.get('href')
    source  = tr.find_next('sup').text
    if source == "MJ-UC":
        source = "MJ"
    elif source == "MA": # doit être une erreur
        source = "AO"
    
    avantageShort = None
    columnIdx = 0
    for td in tr.find_all('td'):
        columnIdx += 1
        if columnIdx == 4:
            avantageShort = td.text
            break
    
    print("Processing %s" % title)
    pageURL = "http://www.pathfinder-fr.org/Wiki/" + link
    
    don['Nom']=title
    don['Référence']=pageURL
    don['Source']=source
    don['Résumé']=avantageShort
    
    if not avantageShort:
        print("Résumé n'a pas été trouvé pour %s" % title)
        exit(1)
        
    if MOCK_DON:
        content = BeautifulSoup(open(MOCK_DON),features="lxml").body.find(id='PageContentDiv')
    else:
        content = BeautifulSoup(urllib.request.urlopen(pageURL).read(),features="lxml").body.find(id='PageContentDiv')
    
    if(content == None):
        print("Page %s n'a pas pu être récupérée!" % pageURL)
        continue

    # lire les attributs
    text = ""
    for attr in content.find_all('b'):
        key = attr.text.strip()
        if key[-1]=='.':
            key = key[:-1]
        if key.endswith(' :'):
            key = key[:-2]
        
        for s in attr.next_siblings:
            #print "%s %s" % (key,s.name)
            if s.name == 'b':
                break
            elif s.string:
                text += s.string

        if key in PROPERTIES:
            if key == u"Condition" or key == u"Conditions requises":
                key = u"Conditions"
            elif key == u"Avantages":
                key = u"Avantage"
            elif key == u"Catégories":
                key = u"Catégorie"
            elif key == u"À noter":
                key = u"Spécial"
                
            don[key]=text.strip()
            descr = s.next_siblings
            text = ""
        else:
            print("- Skipping unknown property %s" % key)
    
    # ajouter don
    liste.append(don)
    
    if MOCK_DON:
        break


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/dons.yml", MATCH, FIELDS, HEADER, liste)
