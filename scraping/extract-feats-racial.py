#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import html2text, mergeYAML

## Configurations pour le lancement
MOCK_LIST = None
MOCK_DON = None
#MOCK_LIST = "mocks/don-aasimar.html" # décommenter pour tester avec une liste pré-téléchargée
#MOCK_DON  = "mocks/don3.html"        # décommenter pour tester avec un sort pré-téléchargé

PROPERTIES = [  "Catégorie", "Catégories", "Conditions", "Condition", "Conditions requises", "Normal", "Avantage", "Avantages", "Spécial", "À noter"]

FIELDS = ['Nom', 'Résumé', 'Catégorie', 'Conditions', 'ConditionsRefs', 'Avantage', 'Normal', 'Spécial', 'Source', 'Référence' ]
MATCH = ['Nom']


races = []
with open("../data/races.yml", 'r') as stream:
    try:
        races = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)


liste = []

for r in races:

    u = r['Référence']
    
    print("Dons de races (%s)" % r['Nom'])

    if MOCK_LIST:
        html = BeautifulSoup(open(MOCK_LIST),features="lxml")
    else:
        html = BeautifulSoup(urllib.request.urlopen(u).read(),features="lxml")

    feats = html.find('table',{'class':'tablo autoalt toutgauche'})
    if not feats:
        print("No section feats found for %s" % u)
        continue

    # itération sur chaque page
    for r in feats.find_all('tr'):
        # ignore some rows
        if 'class' in r.attrs and 'titre' in r.attrs['class']:
            continue

        don = {}

        element = r.find_next('a')
        title = element.text
        link  = element.get('href')
        source  = r.find_next('sup').text
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
                elif s.name == 'ul':
                    text += "\n"
                    for li in s.find_all('li'):
                        text +=  li.text + "\n"
                    text += "\n"

            value = text.strip()
            if value.startswith(":"):
                value = value[1:]

            if key in PROPERTIES:
                if key == "Condition" or key == "Conditions requises":
                    key = "Conditions"
                elif key == "Avantages":
                    key = "Avantage"
                elif key == "Catégories":
                    key = "Catégorie"
                elif key == "À noter":
                    key = "Spécial"

                don[key]=value.strip()
                text = ""
            elif "Avantage" in don and len(key) < 15:
                don["Avantage"] += "\n" + key.upper() + " " + value.strip()
                text = ""
            else:
                print("- Skipping unknown property %s" % key)

        # ajouter don
        liste.append(don)

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/dons.yml", MATCH, FIELDS, HEADER, liste)
