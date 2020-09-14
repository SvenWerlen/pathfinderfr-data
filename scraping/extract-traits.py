#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import extractList, mergeYAML


## Configurations pour le lancement
MOCK_TRAITS_BASE = None
#MOCK_TRAITS_BASE = "mocks/traits-base.html"       # décommenter pour tester avec la liste de traits pré-téléchargée
MOCK_TRAITS_RACE = None
#MOCK_TRAITS_RACE = "mocks/traits-race.html"       # décommenter pour tester avec la liste de traits pré-téléchargée
MOCK_TRAITS_REG = None
#MOCK_TRAITS_REG = "mocks/traits-region.html"      # décommenter pour tester avec la liste de traits pré-téléchargée
MOCK_TRAITS_RELI = None
#MOCK_TRAITS_RELI = "mocks/traits-religieux.html"  # décommenter pour tester avec la liste de traits pré-téléchargée

REF_TRAITS_BASE = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Traits%20de%20base.ashx"
REF_TRAITS_RACE = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Traits%20de%20race.ashx"
REF_TRAITS_REG  = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Traits%20r%c3%a9gionaux.ashx"
REF_TRAITS_RELI = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Traits%20religieux.ashx"
liste = []

FIELDS = ['Nom', 'Race', 'Source', 'Description', 'Remplace', 'Modifie', 'Référence' ]
MATCH = ['Nom']

#
# traits de base
#
print("Extraction des traits de base...")
if MOCK_TRAITS_BASE:
    content = BeautifulSoup(open(MOCK_TRAITS_BASE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REF_TRAITS_BASE).read(),features="lxml").body

sections = content.find_all('h2',{'class':['separator']})

for s in sections:
    # ignorer la navigation
    if s.text.strip().startswith("Traits de personnages"):
        continue
    
    prefix = ""
    if "combat" in s.text:
        prefix = "Trait de combat: "
    elif "foi" in s.text:
        prefix = "Trait de foi: "
    elif "magie" in s.text:
        prefix = "Trait de magie: "
    elif "sociaux" in s.text:
        prefix = "Trait social: "
    else:
        print("Type de trait inconnu")
        exit(1)
    
    for l in extractList(s):
        trait = {}
        trait['Nom'] = prefix + l["Name"]
        trait['Source'] = "MJRA"
        trait['Description'] = l["Desc"]
        trait['Référence'] = REF_TRAITS_BASE
        liste.append(trait)

#
# traits de race
#
print("Extraction des traits de race...")
if MOCK_TRAITS_RACE:
    content = BeautifulSoup(open(MOCK_TRAITS_RACE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REF_TRAITS_RACE).read(),features="lxml").body

sections = content.find_all('h2',{'class':['separator']})

for s in sections:
    # ignorer la navigation
    if s.text.strip().startswith("Traits de personnages"):
        continue
    
    race = ""
    if "demi-elfes" in s.text:
        race = "Demi-elfe"
    elif "demi-orques" in s.text:
        race = "Demi-orque"
    elif "elfiques" in s.text:
        race = "Elfe"
    elif "gobelins" in s.text:
        race = "Gobelin"
    elif "orques" in s.text:
        race = "Orque"
    elif "gnomes" in s.text:
        race = "Gnome"
    elif "halfelins" in s.text:
        race = "Halfelin"
    elif "humains" in s.text:
        race = "Humain"        
    elif "nains" in s.text:
        race = "Nain"        
    elif "ethnique" in s.text: # n'est pas supporté encore
        continue 
    else:
        print("Type de race inconnu: %s" % s.text)
        exit(1)
    
    for l in extractList(s):
        trait = {}
        trait['Nom'] = "Trait de race: " + l["Name"]
        trait['Race'] = race
        trait['Source'] = "MJRA"
        trait['Description'] = l["Desc"]
        trait['Référence'] = REF_TRAITS_RACE
        liste.append(trait)


#
# traits régionaux
#
print("Extraction des traits régionaux...")
if MOCK_TRAITS_REG:
    content = BeautifulSoup(open(MOCK_TRAITS_REG),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REF_TRAITS_REG).read(),features="lxml").body

page = content.find('div',{'class':['presentation navmenudroite']})

for l in extractList(page):
    trait = {}
    trait['Nom'] = "Trait régional: " + l["Name"]
    trait['Source'] = "MJRA"
    trait['Description'] = l["Desc"]
    trait['Référence'] = REF_TRAITS_REG
    liste.append(trait)
    
#
# traits religieux
#
print("Extraction des traits religieux...")
if MOCK_TRAITS_RELI:
    content = BeautifulSoup(open(MOCK_TRAITS_RELI),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REF_TRAITS_RELI).read(),features="lxml").body

page = content.find('div',{'class':['presentation navmenudroite']})

for l in extractList(page):
    trait = {}
    trait['Nom'] = "Trait religieux: " + l["Name"]
    trait['Source'] = "MJRA"
    trait['Description'] = l["Desc"]
    trait['Référence'] = REF_TRAITS_RELI
    liste.append(trait)


print("Fusion avec fichier YAML existant...")

HEADER = """###
### ATTENTION: certains traits ont été ajustés manuellement
### - Duergars: les traits des Nains ont été ajoutés individuellement
### - Suli: les attaques d'énergie ont été ajustés (nom et description)
### - Traits de campagne: ajouté manuellement
###

"""

mergeYAML("../data/traits.yml", MATCH, FIELDS, HEADER, liste)
