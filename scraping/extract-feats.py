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

FIELDS = ['Nom', 'Résumé', 'Catégorie', 'Conditions', 'ConditionsRefs', 'Avantage', 'AvantageHTML', 'Normal', 'Spécial', 'Source', 'Référence' ]
MATCH = ['Nom']

FEAT_REFS = []

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
    idxAvantages = -1
    for tr in list:
        don = {}
        
        if 'class' in tr.attrs and 'titre' in tr.attrs['class']:
            idx = 0
            for td in tr.find_all('td'):
                if td.text == "Avantages":
                    idxAvantages = idx
                    break
                idx+=1
            continue
        
        if idxAvantages < 0:
            print("Colonne 'Avantages' n'a pas pu être trouvée!!")
            exit(1)
        
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
        avantageShort = tds[idxAvantages].text
        
        print("Don %s" % title)
        pageURL = "http://www.pathfinder-fr.org/Wiki/" + link
        FEAT_REFS.append(link)
        
        don['Nom']=cleanName(title)
        don['Référence']=pageURL
        don['Source']=source
        don['Résumé']=cleanProperty(avantageShort)
        don['ConditionsRefs']=[]
        
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
        html = ""
        for attr in content.find_all('b'):
            key = attr.text.strip()
            if key[-1]=='.':
                key = key[:-1]
            if key.endswith(' :'):
                key = key[:-2]
            
            refs = []
            for s in attr.next_siblings:
                #print "%s %s" % (key,s.name)
                if s.name == 'b':
                    break
                else:
                    # keep links (href) to build dependency tables
                    if s.name == 'a':
                        refs.append(s['href'])
                    text += html2text(s)
                    html += html2text(s, True, 2)

            if key in PROPERTIES:
                if key == "Condition" or key == "Conditions requises":
                    key = "Conditions"
                elif key == "Avantages":
                    key = "Avantage"
                elif key == "Catégories":
                    key = "Catégorie"
                elif key == "À noter":
                    key = "Spécial"
                
                don[key]=cleanProperty(text, False)
                if key == "Avantage":
                    don["AvantageHTML"] = html
                
                descr = s.next_siblings
                text = ""
                html = ""
                
            else:
                print("- Skipping unknown property %s" % key)
        
            if key == "Conditions":
                for r in refs:
                    if r in FEAT_REFS:
                        don['ConditionsRefs'].append("http://www.pathfinder-fr.org/Wiki/" + r)
        
        # ajouter don
        liste.append(don)
        
        if MOCK_DON:
          print(liste)
          break


    print("Fusion avec fichier YAML existant...")

    HEADER = ""

    mergeYAML("../data/dons.yml", MATCH, FIELDS, HEADER, liste)
