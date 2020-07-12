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

URL = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Points%20h%c3%a9ro%c3%afques.ashx"


PROPERTIES = [  "Condition", "Normal", "Avantage", "Spécial"]
FIELDS = ['Nom', 'Résumé', 'Catégorie', 'Conditions', 'ConditionsRefs', 'Avantage', 'AvantageHTML', 'Normal', 'Spécial', 'Source', 'Référence' ]
MATCH = ['Nom']



parsed_html = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml")
feats = map(
    lambda node: node.find_parent("div", class_="BD"),
    parsed_html.body.find(id="PageContentDiv").find_all("b", text="Avantage")
)
spells = map(
    lambda node: node.find_parent("div", class_="BD"),
    parsed_html.body.find(id="PageContentDiv").find_all("b", text="Niveau")
)


liste = []
for content in feats:
    don = {}
    don['Nom']=cleanName(content.find("div", class_="BDtitre").text)
    don['Référence']=URL
    don['Source']="MJRA"
    don["Catégorie"]="Points héroïques"
    
    for key in PROPERTIES:
        attribute = content.find("b", text=key)
        if attribute is not None:
            text = ""
            for s in attribute.next_siblings:
                if s.string is not None:
                    text += " " + s.string
            if text.startswith(" . "):
                text = text[3:]
            
            if key == "Condition":
                key = "Conditions"
            
            don[key]=cleanProperty(text)

    liste.append(don)


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/dons.yml", MATCH, FIELDS, HEADER, liste)


PROPERTIES = ['École', 'Niveau', 'Portée', 'Portée courte', 'Cible', 'Temps d’incantation', 'Composantes', 'Durée', 'Jet de sauvegarde', 'Résistance à la magie' ]
FIELDS = ['Nom', 'École', 'Niveau', 'Portée', 'Cible ou zone d\'effet', 'Temps d\'incantation', 'Composantes', 'Durée', 'Jet de sauvegarde', 'Résistance à la magie', 'Description', 'DescriptionHTML', 'Source', 'Référence' ]
MATCH = ['Référence']
IGNORE = ['Source']


liste = []
for content in spells:
    sort = {}
    sort['Nom']=cleanName(content.find("div", class_="BDtitre").text)
    print(sort['Nom'])
    sort['Référence']=URL + "#" + sort['Nom']
    sort['Source']="MJRA"

    key=""
    text=""
    for tag in content.find("div", class_="BDtitre").next_siblings:
        if tag.name == "b" or tag.name == "br":
            if key != "":
                if key in PROPERTIES:
                    if key == "Cible":
                        key = "Cible ou zone d'effet"
                    if key == "Temps d’incantation":
                        key = "Temps d'incantation"
                    if key == "Portée courte":
                        key = "Portée"
                        text = "courte " + text
                    sort[key]=cleanProperty(text)
                else:
                    print("- Skipping unknown property [%s]" % key)
                key=""
                text=""
        if tag.name == "b":
            key = tag.text
        if tag.name is None:
            text += tag.string
        if tag.name == "a":
            text += tag.text

    sort["Description"] = text.replace("\n", " ").strip()
    liste.append(sort)


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/spells.yml", MATCH, FIELDS, HEADER, liste, IGNORE)
