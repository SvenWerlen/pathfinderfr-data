#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import cleanSectionName, cleanProperty, cleanName, html2text, getValidSource, mergeYAML

## Configurations pour le lancement
MOCK_LIST = None
MOCK_DON = None
#MOCK_LIST = "mocks/donsListe.html"   # décommenter pour tester avec une liste pré-téléchargée
#MOCK_DON  = "mocks/don7.html"        # décommenter pour tester avec un sort pré-téléchargé

URLS = ["http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.tableau%20r%c3%a9capitulatif%20des%20dons.ashx",
        "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.dons%20daudace.ashx",
        "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.dons%20de%20cr%c3%a9ation%20dobjets.ashx",
        "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.dons%20d%c3%a9cole.ashx",
        "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.dons%20d%c3%a9quipe.ashx",
        "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.dons%20de%20m%c3%a9tamagie.ashx",
        "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.dons%20de%20spectacle.ashx",
        "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tableau%20r%c3%a9capitulatif%20des%20dons%20mythiques.ashx",
        "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.dons%20issus%20du%20cadre%20de%20campagne.ashx",
        ]

PROPERTIES = [  "Catégorie", "Catégories", "Conditions", "Condition", "Conditions requises", "Normal", "Avantage", "Avantages", "Spécial", "À noter"]

FIELDS = ['Nom', 'Résumé', 'Catégorie', 'Conditions', 'Avantage', 'Normal', 'Spécial', 'Source', 'Référence' ]
MATCH = ['Nom']

for URL in URLS:
    
    liste = []

    print("Extraction des dons: " + URL)

    list = []
    if MOCK_LIST:
        parsed_html = BeautifulSoup(open(MOCK_LIST),features="lxml")
        list = parsed_html.body.find(id='PageContentDiv').find_all('tr')
    else:
        parsed_html = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml")
        list = parsed_html.body.find(id='PageContentDiv').find_all('tr')
    
    # itération sur chaque page
    for tr in list:
        don = {}
        
        if 'class' in tr.attrs and 'titre' in tr.attrs['class']:
            continue
        
        element = tr.find_next('a')
        title = element.text
        link  = element.get('href')
        if tr.find('sup'):
            source = getValidSource(tr.find('sup').text)
        else:
            source = "MJ"
        
        avantageShort = None
        columnIdx = 0
        tds = tr.find_all('td')
        avantageShort = tds[len(tds)-1].text
        
        print("Don %s" % title)
        pageURL = "http://www.pathfinder-fr.org/Wiki/" + link
        
        don['Nom']=cleanName(title)
        don['Référence']=pageURL
        don['Source']=source
        don['Résumé']=cleanProperty(avantageShort)
        
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
                else:
                    text += html2text(s)

            if key in PROPERTIES:
                if key == u"Condition" or key == u"Conditions requises":
                    key = u"Conditions"
                elif key == u"Avantages":
                    key = u"Avantage"
                elif key == u"Catégories":
                    key = u"Catégorie"
                elif key == u"À noter":
                    key = u"Spécial"
                
                don[key]=cleanProperty(text)
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
