#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
from bs4 import BeautifulSoup
from lxml import html


## Configurations pour le lancement
MOCK_RACE = None
#MOCK_RACE = "mocks/race-drow.html"       # décommenter pour tester avec une classe pré-téléchargée

URLs = [
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.aasimar%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.dhampir%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.drow%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.fetchelin%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Gobelin%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.hobgobelin%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.homme-f%c3%a9lin%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.homme-rat%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.ifrit%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.kobold%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.ondin%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.orque%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.or%c3%a9ade%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.sylphe%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.tengu%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.tieffelin%20(race).ashx", 'source': 'MR'},

    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.aquatique%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.changelin%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.duergar%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.grippli%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.homme-poisson%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.kitsune%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.nagaji%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.samsaran%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.strix%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.suli%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.svirfneblin%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.vanara%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.vishkanya%20(race).ashx", 'source': 'MR'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.wayang%20(race).ashx", 'source': 'MR'},

]


#
# cette fonction extrait le texte du prochain élément après ...
#
def findAfter(html, afterTag, afterCond, searched):
    elements = html.find_next(afterTag, afterCond).next_siblings
    for el in elements:
        if el.name == searched:
            return el.text.strip()

#
# cette fonction extrait le texte pour une propriété <b>propriété</b> en prenant le texte qui suit
#
def findProperty(html, propName):
    for el in html:
        if el.name == 'b' and el.text.lower().startswith(propName.lower()):
            value = ""
            for e in el.next_siblings:
                if e.name == 'br':
                    break
                elif e.string:
                    value += e.string
                else:
                    value += e
            return value.replace('.','').strip()
    return None

#
# cette fonction permet de sauter à l'élément recherché et retourne les prochains éléments
#
def jumpTo(html, afterTag, afterCond, elementText):
    seps = content.find_all(afterTag, afterCond);
    for s in seps:
        if s.text.lower().strip().startswith(elementText.lower()):
            return s.next_siblings

liste = []

# itération sur chaque page
for data in URLs:
    race = {}

    link = data['link']

    print("Processing %s" % link)
    pageURL = link

    if MOCK_RACE:
        content = BeautifulSoup(open(MOCK_RACE),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(pageURL).read(),features="lxml").body

    # titre
    name = content.find_next('h1',{'class':'pagetitle'}).string.strip()
    if name.startswith('Les '):
        name = name[4:-1].title()

    race[u'01Nom'] = name

    # source
    race[u'03Source'] = data['source']

    # référence
    race[u'04Référence'] = link

    # traits
    race[u'05Traits'] = []
    section = jumpTo(html, 'h2',{'class':'separator'}, u"Traits raciaux standards")
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
                            trait['01Nom'] = u"Caractéristiques"
                            descr = name
                        else:
                            if name.endswith('.'):
                                name = name[:-1]
                            trait['01Nom'] = name
                        first = False
                    elif el.string:
                        descr += el.string

                trait['02Description'] = descr.strip()
                race[u'05Traits'].append(trait)

    race['EMPTY'] = ""

    # ajouter race
    liste.append(race)

    if MOCK_RACE:
        break

yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace(u'01Nom',u'Nom')
yml = yml.replace(u'02Référence',u'Référence')
yml = yml.replace(u'02Description',u'Description')
yml = yml.replace(u'03Source',u'Source')
yml = yml.replace(u'04Référence',u'Référence')
yml = yml.replace(u'05Traits',u'Traits')
yml = yml.replace("EMPTY: ''",'')
print(yml)
