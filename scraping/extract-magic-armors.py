#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import *

## Configurations pour le lancement
MOCK_MAGIC = None
#MOCK_MAGIC = "mocks/magic-armors.html"                  # décommenter pour tester avec les armures pré-téléchargées
MOCK_MAGIC_DETAILS = None
#MOCK_MAGIC_DETAILS = "mocks/magic-armors-details.html"  # décommenter pour tester avec le détails des armures pré-téléchargées

FIELDS = ['Nom', 'Résumé', 'Restrictions', 'Prix', 'PrixModif', 'Aura', 'NLS', 'Source', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom']

# Plus rapide de copier directement ici que d'essayer d'extraire
TEXTE1 = 'Les armures et boucliers magiques offrent à leur utilisateur une protection supplémentaire, sous la forme d’un bonus d’altération (de +5 au maximum) qui s’ajoute au bonus à la CA de l’objet lui-même. Les bonus d’une armure, d’un bouclier et de leur magie respective sont cumulatifs. Toutes les armures et tous les boucliers magiques sont des versions de maître, leur malus d’armure aux tests est ainsi réduit de 1.'
TEXTE2 = 'Une armure peut, en plus de son bonus d’altération, posséder certaines propriétés. Celles-ci sont considérées comme un bonus supplémentaire pour ce qui est du prix de l’armure, même si elles n’ont aucune influence sur la CA. Une armure ne peut jamais avoir un bonus total (bonus d’altération plus bonus lié à ses propriétés, y compris celles qui proviennent des aptitudes du personnage et des sorts) supérieur à +10. Toute armure possédant une propriété spéciale doit avoir au moins un bonus d’altération de +1.'
TEXTE3 = 'Les armures et les boucliers peuvent être fabriqués dans un matériau inhabituel. Lancez 1d100 : sur un résultat de 01–95, l’objet est d’un matériau standard et, sur 96–100, il est fait d’un matériau spécial (voir la Section "Les matériaux spéciaux").'
TEXTE4 = 'Même si l’armure est accompagnée de bottes, de gantelets ou d’un heaume, ces parties peuvent être échangées contre d’autres objets magiques du même type sans nuire à la CA.'

liste = []


REFERENCE = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.armures%20magiques.ashx"
REFERENCE_DETAILS = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.descriptions%20individuelles%20des%20propri%c3%a9t%c3%a9s%20sp%c3%a9ciales%20des%20armures%20et%20des%20boucliers.ashx"

if MOCK_MAGIC:
    content = BeautifulSoup(open(MOCK_MAGIC),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE).read(),features="lxml").body


##
## BONUS D'ALTERATION
##
table = getTableWithCaption( content, "Prix des bonus d'altération des armures et des boucliers" )
if not table:
    print("Table des prix de bonus d'altération non-trouvée!!")
    exit(1)

notes = []

for tr in table.find_all('tr'):
    if 'class' in tr.attrs and "titre" in tr.attrs['class']:
        continue
    tds = tr.find_all('td')
    if len(tds) == 2:
        price = re.search('([\d ]+) po', html2text(tds[1]))
        if price:
            price = int(price.group(1).replace(' ', ''))
        else:
            print("Prix invalide: %s" % html2text(tds[1]))
            
        liste.append({
          "Nom": "Bonus d'alteration %s" % cleanName(html2text(tds[0])),
          "Résumé": "Bonus d'altération qui s’ajoute à la CA de l'objet",
          "Prix": price,
          "Source": "MJ",
          "Référence": "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.armures%20magiques.ashx#PRIXBONUSDALTERATION"
        })
    else:
        notes.append(html2text(tds[0]))

# ajout des descriptions
description = "%s\n\n%s\n\n%s\n\n%s" % (TEXTE1, TEXTE2, TEXTE3, TEXTE4)
descriptionHTML = "<p>%s</p><p>%s</p><p>%s</p><p>%s</p>" % (TEXTE1, TEXTE2, TEXTE3, TEXTE4)
for n in notes:
    description += "\n\n%s" % n
    descriptionHTML += "<p><i>%s</i></p>" % n
for el in liste:
    el['Description'] = description
    el['DescriptionHTML'] = descriptionHTML


##
## PROPRIÉTÉS
##
TABLE_NAMES = ["Propriétés ajoutant un prix spécifique", "Propriétés ajoutant un bonus de +1", "Propriétés ajoutant un bonus de +2", "Propriétés ajoutant un bonus de +3", "Propriétés ajoutant un bonus de +4", "Propriétés ajoutant un bonus de +5"]
existing = {}
for T in TABLE_NAMES:
    table = getTableWithCaption( content, T )
    if not table:
      print("Table '%s' non-trouvée!!" % T)
      exit(1)
    
    for tr in table.find_all('tr'):
        if 'class' in tr.attrs and "titre" in tr.attrs['class']:
            continue
          
        trs = tr.find_all('td')
        if len(trs) == 5:
            nom = cleanName(html2text(trs[0]))
            link = trs[0].find('a')['href']
            description = "%s" % html2text(trs[3])
            element = {
              "Nom": "Propriété: %s" % nom,
              "Restrictions": html2text(trs[2]),
              "PrixModif": html2text(trs[4]),
              "Source": getValidSource(trs[1].text),
              "Résumé": description,
              "Référence": "https://www.pathfinder-fr.org/Wiki/%s" % link if link else REFERENCE_DETAILS
            }
            liste.append(element)
            existing[nom.lower()] = element

if MOCK_MAGIC_DETAILS:
    content = BeautifulSoup(open(MOCK_MAGIC_DETAILS),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE_DETAILS).read(),features="lxml").body


##
## DETAILS DES ARMURES
##
for boite in content.find_all('div',{'class':['BD']}):
            
    data = {**extractBD_Type2(boite)}
    if not data['nomAlt'].lower() in existing:
      print("Propriété sans correspondance sur la page sommaire: %s" % data['nomAlt'])
      continue
    
    element = existing[data['nomAlt'].lower()]
    element['Description'] = data['descr']
    element['DescriptionHTML'] = data['descrHTML']
    element["Aura"] = data["aura"]
    element["NLS"] = int(data["nls"])
        
    del(existing[data['nomAlt'].lower()])


if len(existing) > 0:
    print("Éléments sans détails")
    print(existing)
    exit(1)

#exit(1)

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/magic-armures.yml", MATCH, FIELDS, HEADER, liste)
