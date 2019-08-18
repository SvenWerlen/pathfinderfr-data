#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanSectionName, cleanInlineDescription, extractLevel, mergeYAML

## Configurations pour le lancement
MOCK_RACE = None
#MOCK_RACE = "mocks/race-drow.html"       # décommenter pour tester avec une classe pré-téléchargée

URLs = [
    {'name': 'Demi-elfe', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Demi-elfe.ashx", 'source': 'MJ'},
    {'name': 'Demi-orque', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Demi-orque.ashx", 'source': 'MJ'},
    {'name': 'Elfe', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Elfe.ashx", 'source': 'MJ'},
    {'name': 'Gnome', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Gnome.ashx", 'source': 'MJ'},
    {'name': 'Halfelin', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Halfelin.ashx", 'source': 'MJ'},
    {'name': 'Humain', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Humain.ashx", 'source': 'MJ'},
    {'name': 'Nain', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Nain.ashx", 'source': 'MJ'},
    
    {'name': 'Aasimar', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.aasimar%20(race).ashx", 'source': 'MR'},
    {'name': 'Dhampir', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.dhampir%20(race).ashx", 'source': 'MR'},
    {'name': 'Drow', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.drow%20(race).ashx", 'source': 'MR'},
    {'name': 'Fetchelin', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.fetchelin%20(race).ashx", 'source': 'MR'},
    {'name': 'Gobelin', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Gobelin%20(race).ashx", 'source': 'MR'},
    {'name': 'Hobgobelin', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.hobgobelin%20(race).ashx", 'source': 'MR'},
    {'name': 'Homme-félin', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.homme-f%c3%a9lin%20(race).ashx", 'source': 'MR'},
    {'name': 'Homme-rat', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.homme-rat%20(race).ashx", 'source': 'MR'},
    {'name': 'Ifrit', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.ifrit%20(race).ashx", 'source': 'MR'},
    {'name': 'Kobold', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.kobold%20(race).ashx", 'source': 'MR'},
    {'name': 'Ondin', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.ondin%20(race).ashx", 'source': 'MR'},
    {'name': 'Orque', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.orque%20(race).ashx", 'source': 'MR'},
    {'name': 'Oréade', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.or%c3%a9ade%20(race).ashx", 'source': 'MR'},
    {'name': 'Sylphe', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.sylphe%20(race).ashx", 'source': 'MR'},
    {'name': 'Tengu', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.tengu%20(race).ashx", 'source': 'MR'},
    {'name': 'Tieffelin', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.tieffelin%20(race).ashx", 'source': 'MR'},

    {'name': 'Aquatique', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.aquatique%20(race).ashx", 'source': 'MR'},
    {'name': 'Changelin', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.changelin%20(race).ashx", 'source': 'MR'},
    {'name': 'Duergar', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.duergar%20(race).ashx", 'source': 'MR'},
    {'name': 'Grippli', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.grippli%20(race).ashx", 'source': 'MR'},
    {'name': 'Homme-poisson', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.homme-poisson%20(race).ashx", 'source': 'MR'},
    {'name': 'Kitsune', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.kitsune%20(race).ashx", 'source': 'MR'},
    {'name': 'Nagaji', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.nagaji%20(race).ashx", 'source': 'MR'},
    {'name': 'Samsaran', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.samsaran%20(race).ashx", 'source': 'MR'},
    {'name': 'Strix', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.strix%20(race).ashx", 'source': 'MR'},
    {'name': 'Suli', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.suli%20(race).ashx", 'source': 'MR'},
    {'name': 'Svirfneblin', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.svirfneblin%20(race).ashx", 'source': 'MR'},
    {'name': 'Vanara', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.vanara%20(race).ashx", 'source': 'MR'},
    {'name': 'Vishkanya', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.vishkanya%20(race).ashx", 'source': 'MR'},
    {'name': 'Wayang', 'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.wayang%20(race).ashx", 'source': 'MR'},
]

FIELDS = ['Nom', 'Source', 'Référence', 'Traits', 'Description' ]
MATCH = ['Nom']


liste = []

# itération sur chaque page
for data in URLs:
    race = {}

    link = data['link']

    print("Traitement %s" % link)
    pageURL = link

    if MOCK_RACE:
        content = BeautifulSoup(open(MOCK_RACE),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(pageURL).read(),features="lxml").body

    # titre
    name = content.find_next('h1',{'class':'pagetitle'}).string.strip()
    if name.startswith('Les '):
        name = name[4:-1].title()

    race['Nom'] = data['name']

    # source
    race['Source'] = data['source']

    # référence
    race['Référence'] = link

    # traits
    race['Traits'] = []
    section = jumpTo(content, 'h2',{'class':'separator'}, "Traits raciaux standards")
    for s in section:
        if s.name == 'div' and 'class' in s.attrs and "arrondi" in s.attrs['class']:
            first = True
            for attr in s.find_all('li'):
                trait = {}
                descr = ""
                for el in attr.children:
                    if el.name == 'b':
                        name = el.text.strip()
                        if first:
                            trait['Nom'] = "Caractéristiques"
                            descr = name
                        else:
                            if name.endswith('.'):
                                name = name[:-1]
                            trait['Nom'] = name
                        first = False
                    elif el.string:
                        descr += el.string

                trait['Description'] = descr.strip()
                race['Traits'].append(trait)

    # ajouter race
    liste.append(race)

    if MOCK_RACE:
        break

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/races.yml", MATCH, FIELDS, HEADER, liste)
