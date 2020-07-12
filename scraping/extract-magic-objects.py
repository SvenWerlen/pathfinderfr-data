#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import table2text, extractBD_Type1, extractBD_Type2, html2text, cleanName, mergeYAML

## Configurations pour le lancement
MOCK_MAGIC = None
#MOCK_MAGIC = "mocks/magic-objets.html"                  # décommenter pour tester avec les objets merveilleux pré-téléchargées
MOCK_MAGIC_ITEM = None
#MOCK_MAGIC_ITEM = "mocks/magic-ailes-vol.html"      # décommenter pour tester avec détails pré-téléchargé
#MOCK_MAGIC_ITEM = "mocks/magic-casque-comprehension.html"      # décommenter pour tester avec détails pré-téléchargé

TEXTE = ''

FIELDS = ['Nom', 'Type', 'Prix', 'Source', 'Emplacement', 'Poids', 'Aura', 'NLS', 'Conditions', 'Coût', 'Description', 'Référence' ]
MATCH = ['Nom']

liste = []


# first = column with name
# second = column with cost
PATHFINDER = "http://www.pathfinder-fr.org/Wiki/"
REFERENCE = PATHFINDER + "Pathfinder-RPG.Liste%20alphab%c3%a9tique%20des%20objets%20merveilleux.ashx"
TYPE = "Objet merveilleux"


if MOCK_MAGIC:
    content = BeautifulSoup(open(MOCK_MAGIC),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE).read(),features="lxml").body


propList = []

multicol = content.find_all('div',{'class':['article_3col']})

liste = []

print("Extraction des objets merveilleux...")

found = False
for m in multicol:
    for link in m.find_all('a'):
        
        # extraire adresse URL
        reference = PATHFINDER + link['href']
                
        # extraire nom
        nom = link.text.strip()
        
        # jump
        #if nom == "Bandelettes de Frappes Dévastatrices":
        #    found = True
        
        #if not found:
        #    continue

        # skip unknown links
        if('class' in link.attrs and 'unknownlink' in link['class']):
            continue

        
        # débogage
        print("Traitement de %s..." % nom.strip())
        
        # récupérer le détail d'un objet
        if MOCK_MAGIC_ITEM:
            page = BeautifulSoup(open(MOCK_MAGIC_ITEM),features="lxml").body
        else:
            try:
                page = BeautifulSoup(urllib.request.urlopen(reference).read(),features="lxml").body
                
                pageNotFound = page.find('h1',{'class':['pagetitlesystem']})
                if(pageNotFound and pageNotFound.text() == 'Page Not Found'):
                    continue
                
            except:
                #print("Page doesn't exist! Skipping...")
                continue

        for boite in page.find_all('div',{'class':['BD']}):
            
            data = {**extractBD_Type2(boite)}
            descr = data['descr']
            
            if len(data['descr']) == 0:
                print("Description invalide pour: %s" % href)
                exit(1)
            
            element = {}
            element["Nom"] = data["nomAlt"] # prendre le nom de la page détaillée
            element["Type"] = TYPE
            element["Prix"] = data["prixAlt"] # prendre le prix de la page détaillée
            element["Source"] = "MJ"
            element["Description"] = data["descr"]
            element["Référence"] = reference
            
            # infos additionnelles
            if "emplacement" in data:
                element["Emplacement"] = data["emplacement"]
            if "poids" in data:
                element["Poids"] = data["poids"]
            if "aura" in data:
                element["Aura"] = data["aura"]
            if "nls" in data:
                # NLS parfois variable
                if isinstance(data["nls"], int):
                    element["NLS"] = data["nls"]
                else:
                    element["Description"] = "NLS: " + data["nls"] + "\n\n" + element["Description"]
            if "conditions" in data:
                element["Conditions"] = data["conditions"]
            if "coût" in data:
                element["Coût"] = data["coût"]
            
            # si l'objet à plusieurs prix, alors créer les variations de l'objet
            variations = re.split('(?<=\)),\s+|(?<=\))\s+ou\s+', element["Prix"]) 
            if len(variations) > 1:
                
                added = False
                for variation in variations:
                    varElement = dict(element)
                    try:
                        price = re.search('^(.+? po) \(', variation).group(1)
                    except:
                        print("ERROR: Could not extract the variation detail for " + element["Nom"] + " '" + variation + "'")
                        exit(1)
                    try:
                        detail = re.search('po \((.+?)\)$', variation).group(1)
                    except:
                        print("ERROR: Could not extract the variation detail for " + element["Nom"] + "'" + variation + "'")
                        exit(1)
                    varElement["Prix"] = price
                    varElement["Nom"] = element["Nom"] + " (" + detail + ")"
                    print("Creation de la variation " + varElement["Nom"])
                    liste.append(varElement)
                    
            else:
                liste.append(element)
                    
#exit(1)

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/magic.yml", MATCH, FIELDS, HEADER, liste)

