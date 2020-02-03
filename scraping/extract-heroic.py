#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html


URL = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Points%20h%c3%a9ro%c3%afques.ashx"

parsed_html = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml")
feats = map(
    lambda node: node.find_parent("div", class_="BD"),
    parsed_html.body.find(id="PageContentDiv").find_all("b", text="Avantage")
)
spells = map(
    lambda node: node.find_parent("div", class_="BD"),
    parsed_html.body.find(id="PageContentDiv").find_all("b", text="Niveau")
)

# Extraction des dons
print("--- ====== Dons ======")
PROPERTIES = [ u"Condition", u"Normal", u"Avantage", u"Spécial" ]
dons = []
for content in feats:
    don = {}
    don[u'Nom']=content.find("div", class_="BDtitre").text
    don[u'Référence']=URL
    don[u'Source']="MJRA"
    don[u"Catégorie"]=u"Points héroïques"
    
    for key in PROPERTIES:
        attribute = content.find("b", text=key)
        if attribute is not None:
            text = ""
            for s in attribute.next_siblings:
                if s.string is not None:
                    text += " " + s.string
            if text.startswith(" . "):
                text = text[3:]
            don[key]=text

    dons.append(don)

yml = yaml.safe_dump(dons,default_flow_style=False, allow_unicode=True)
print(yml)

# Extraction des sorts
print("--- ====== Sorts ======")
PROPERTIES = [ u"École", u"Niveau", u"Portée", u"Portée courte", u"Cible", u"Temps d’incantation", u"Composantes", u"Durée", u"Jet de sauvegarde", u"Résistance à la magie"]
sorts = []
for content in spells:
    sort = {}
    sort[u'Nom']=content.find("div", class_="BDtitre").text
    sort[u'Référence']=URL
    sort[u'Source']="MJRA"
    sort[u"Catégorie"]=u"Points héroïques"

    key=""
    text=""
    for tag in content.find("div", class_="BDtitre").next_siblings:
        if tag.name == "b" or tag.name == "br":
            if key != "":
                if key in PROPERTIES:
                    if key == u"Cible":
                        key = u"Cible ou zone d'effet"
                    if key == u"Temps d’incantation":
                        key = u"Temps d'incantation"
                    if key == u"Portée courte":
                        key = u"Portée"
                        text = u"courte " + text
                    sort[key]=text.strip().strip(";").strip()
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

    sort[u"Description"] = text.replace("\n", " ").strip()
    sorts.append(sort)

yml = yaml.safe_dump(sorts,default_flow_style=False, allow_unicode=True)
print(yml)

# Extraction des objets magiques

# TODO  
