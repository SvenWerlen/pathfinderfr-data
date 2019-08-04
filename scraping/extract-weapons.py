#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html


## Configurations pour le lancement
URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tableau%20r%c3%a9capitulatif%20des%20armes.ashx"
URLDET = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Descriptions%20individuelles%20des%20armes.ashx"
MOCK_W = None
#MOCK_W = "mocks/weapons.html"           # décommenter pour tester avec les armes pré-téléchargées
MOCK_WD = None
#MOCK_WD = "mocks/weapons-details.html"  # décommenter pour tester avec les armes pré-téléchargées


#
# cette fonction permet de sauter à l'élément recherché et retourne les prochains éléments
#
def jumpTo(html, afterTag, afterCond, elementText):
    seps = content.find_all(afterTag, afterCond);
    for s in seps:
        if s.text.lower().strip().startswith(elementText.lower()):
            return s.next_siblings

liste = []


if MOCK_W:
    content = BeautifulSoup(open(MOCK_W),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

tables = content.find_all('table',{'class':'tablo'})

weapon = {}

for t in tables:
    rows = t.find_all('tr',{'class':''}) + t.find_all('tr',{'class':['alt']})
    for r in rows:
        cols = r.find_all('td')
        if len(cols) == 9:
            # Name & Reference
            nameLink = cols[0].find('a')
            weapon['01Nom'] = cols[0].text.strip()
            if weapon['01Nom'].endswith(" (3)"):
                weapon['01Nom'] = weapon['01Nom'][:-4]
            if not nameLink is None:
                weapon[u'20Référence'] = "http://www.pathfinder-fr.org/Wiki/" + nameLink['href']
            else:
                weapon[u'20Référence'] = URL
            # Others
            weapon['01Nom'] = weapon['01Nom'].replace('’','\'')
            weapon['04Prix'] = cols[1].text.strip()
            weapon[u'05DégâtsP'] = cols[2].text.strip()
            weapon[u'06DégâtsM'] = cols[3].text.strip()
            weapon[u'07Critique'] = cols[4].text.strip()
            weapon[u'08Portée'] = cols[5].text.strip()
            weapon[u'09Poids'] = cols[6].text.strip()
            weapon[u'10Type'] = cols[7].text.strip()
            weapon[u'11Spécial'] = cols[8].text.strip()
            weapon[u'99Complete'] = False

            weapon['02Source'] = "MJ"
            weapon['EMPTY'] = ""
            liste.append(weapon)
            weapon = {}


#
# cette fonction ajoute les infos additionelles
#
def addInfos(liste, name, source):
    names = []
    # ugly fix
    name = name.replace('’','\'')
    if(name == u"Coup-de-poing"):
        names = [u"Coup-de-poing américain".lower()]
    elif(name == u"Arbalète à répétition"):
        names = [u"Arbalète légère à répétition".lower(),u"Arbalète lourde à répétition".lower()]
    elif(name == u"Arbalète double ou Double arbalète"):
        names = [u"Arbalète double".lower()]
    elif(name == u"Masse d'armes"):
        names = [u"Masse d'armes lourde".lower(),u"Masse d'armes légère".lower()]
    elif(name == u"Flèche de fumée ou flèche fumigène"):
        names = [u"Flèches de fumée (20)".lower()]
    elif(name == u"Flèches assommantes ou flèches à têtes rondes"):
        names = [u"Flèches à tête ronde (20)".lower()]
    elif(name == u"Fléchette ou dard"):
        names = [u"Fléchettes".lower()]
    elif(name == u"Bille de fronde"):
        names = [u"Billes (10)".lower()]
    elif(name == u"Carreau d'arbalète"):
        names = [u"Carreaux (10)".lower()]
    elif(name == u"Flèches"):
        names = [u"Flèches (20)".lower()]
    elif(name == u"Flèches de vol"):
        names = [u"Flèches de vol (20)".lower()]
    elif(name == u"Shuriken"):
        names = [u"Shuriken (5)".lower()]
    elif(name == u"Fléchettes de sarbacane"):
        names = [u"Dard, sarbacane (10)".lower()]
    elif(name == u"Double lame ou épée double"):
        names = [u"Double-lame".lower()]
    elif(name == u"Rondache ou écu à pointes"):
        names = [u"Rondache à pointes".lower(),u"Rondache".lower(),u"Écu à pointes".lower()]
    elif(name == u"Arc composite"):
        names = [u"Arc court composite".lower(),u"Arc long composite".lower()]
    elif(name == u"Haches d'armes naine"):
        names = [u"Hache de guerre naine".lower()]
    elif(name == u"Bâton de jet halfelin ou fustibale halfelin"):
        names = [u"Bâton de jet halfelin".lower()]
    elif(name == u"Bolas bohémiens ou tribaux"):
        names = [u"Bolas tribaux".lower()]
    else:
        names = [name.lower()]

    # add infos to existing weapong in list
    found = False
    for l in liste:
        if l['01Nom'].lower() in names:
            l[u'99Complete'] = True
            l[u'12Description'] = descr.strip()
            if not source is None:
                l['02Source'] = source
            found = True
    if not found:
        print("COULD NOT FIND : '" + name + "'");


if MOCK_WD:
    content = BeautifulSoup(open(MOCK_WD),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URLDET).read(),features="lxml").body

section = jumpTo(html, 'h1',{'class':'separator'}, u"À mains nues")
newObj = True
name = ""
descr = ""
source = None
sourceNext = None
for s in section:
    if s.name == 'div':
        for e in s.children:
            if e.name == 'h2' or e.name == 'b':
                if not newObj:
                    addInfos(liste, name, sourceNext)

                sourceNext = source
                if e.name == 'h2':
                    newObj = True
                else:
                    name = e.text.strip()
                    descr = ""
                    source = None
                    newObj = False
            elif e.name == 'br':
                descr += "\n"
            elif e.name is None or e.name == 'a':
                descr += e.string.replace('\n',' ')
            elif e.name == 'i':
                descr += e.text
            elif e.name == 'div':
                for c in e.children:
                    if c.name == 'img':
                        if('logoAPG' in c['src']):
                            source = 'MJRA'
                        elif('logoUC' in c['src']):
                            source = 'AG'
                        elif('logoMCA' in c['src']):
                            source = 'MCA'
                        elif('logoAE' in c['src']):
                            source = 'AE'
                        else:
                            print(c['src'])
                            exit(1)

addInfos(liste, name, sourceNext)

for l in liste:
    if not l[u'99Complete']:
        print("INCOMPLETE: '" + l['01Nom'] + "'");
    del l[u'99Complete']


yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace('01Nom','Nom')
yml = yml.replace('02Source','Source')
yml = yml.replace('04Prix','Prix')
yml = yml.replace(u'05DégâtsP',u'DégâtsP')
yml = yml.replace(u'06DégâtsM',u'DégâtsM')
yml = yml.replace('07Critique','Critique')
yml = yml.replace(u'08Portée',u'Portée')
yml = yml.replace('09Poids','Poids')
yml = yml.replace('10Type','Type')
yml = yml.replace(u'11Spécial',u'Spécial')
yml = yml.replace(u'12Description',u'Description')
yml = yml.replace(u'20Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)
