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
MOCK_LIST = None
MOCK_DON = None
#MOCK_LIST = "mocks/donsListe.html"   # décommenter pour tester avec une liste pré-téléchargée
#MOCK_DON  = "mocks/don3.html"        # décommenter pour tester avec un sort pré-téléchargé

URLs = ["http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.tableau%20r%c3%a9capitulatif%20des%20dons.ashx"]

PROPERTIES = [  u"Catégorie", u"Catégories", u"Conditions", u"Condition", u"Conditions requises", u"Normal", u"Avantage", u"Avantages", u"Spécial", u"À noter"]

liste = []


list = []
if MOCK_LIST:
    parsed_html = BeautifulSoup(open(MOCK_LIST),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_all('tr')
else:
    list = []
    for u in URLs:
        parsed_html = BeautifulSoup(urllib.request.urlopen(u).read(),features="lxml")
        list += parsed_html.body.find(id='PageContentDiv').find_all('tr')


# itération sur chaque page
for l in list:
    don = {}
    
    element = l.find_next('a')
    title = element.text
    link  = element.get('href')
    source  = l.find_next('sup').text
    if source == "MJ-UC":
        source = "MJ"
    elif source == "MA": # doit être une erreur
        source = "AO"
    
    print("Processing %s" % title)
    pageURL = "http://www.pathfinder-fr.org/Wiki/" + link
    
    don[u'Nom']=title
    don[u'Référence']=pageURL
    don[u'Source']=source
        
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

yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
print(yml)