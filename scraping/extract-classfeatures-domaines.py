#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanLabel, cleanInlineDescription, mergeYAML

## Configurations pour le lancement
MOCK_DOMAINE = None
#MOCK_DOMAINE = "mocks/pretre-domaines.html"       # décommenter pour tester avec les rages pré-téléchargées
#MOCK_DOMAINE_PAGE = "mocks/domain-feu.html"

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.domaines.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']

liste = []

print("Extraction des aptitude (domaines)...")

if MOCK_DOMAINE:
    content = BeautifulSoup(open(MOCK_DOMAINE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

domaines = content.find_all("div", {'presentation navmenu'})
for dom in domaines:
  title = dom.find('h2').text
  if not title.startswith('Les domaines'):
    continue
  
  for d in dom.find_all("li"):
      link = d.find("a")
      if link is None:
          break;
      
      domain = {}
      domain['Nom'] = link.text
      domain['Classe'] = "Prêtre"
      domain['Source'] = "MJ"
      domain['Niveau'] = 1
      domain['Description'] = ""
      domain['DescriptionHTML'] = ""
      domain['Référence'] = "http://www.pathfinder-fr.org/Wiki/" + link["href"]
      
      print("Traitement: " + link["href"])
      if MOCK_DOMAINE:
          domainHTML = BeautifulSoup(open(MOCK_DOMAINE_PAGE),features="lxml").body
      else:
          domainHTML = BeautifulSoup(urllib.request.urlopen(domain['Référence']).read(),features="lxml").body
      
      pouvoirs = jumpTo(domainHTML, 'h2',{'class':'separator'}, "Pouvoirs accordés")
      if pouvoirs is None:
          pouvoirs = jumpTo(domainHTML, 'b',{}, "Pouvoirs accordés")
      if pouvoirs is None:
          print("NOT FOUND!!")
          continue
      for p in pouvoirs:
          if(p.name == 'h2'):
              break
          else:
              domain['Description'] += html2text(p)
              domain['DescriptionHTML'] += html2text(p, True, 2)
          
      liste.append(domain)

#exit(1)

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
