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
URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tableau%20r%c3%a9capitulatif%20des%20armures.ashx"
URLDET = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Descriptions%20individuelles%20des%20armures.ashx#Armurec%C3%A9r%C3%A9monielledesoie"
MOCK_W = None
MOCK_W = "mocks/armors.html"           # décommenter pour tester avec les armes pré-téléchargées
MOCK_WD = None
MOCK_WD = "mocks/armors-details.html"  # décommenter pour tester avec les armes pré-téléchargées


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

armor = {}

for t in tables:
    rows = t.find_all('tr',{'class':''}) + t.find_all('tr',{'class':['alt']})
    for r in rows:
        cols = r.find_all('td')
        if len(cols) == 10:
            # Name & Reference
            nameLink = cols[0].find('a')
            if not nameLink is None:
                armor['01Nom'] = nameLink.text.strip()
                armor[u'20Référence'] = "http://www.pathfinder-fr.org/Wiki/" + nameLink['href']
            else:
                armor['01Nom'] = cols[0].text.strip()
                armor[u'20Référence'] = URL
            # Others
            armor['01Nom'] = armor['01Nom'].replace('’','\'')
            armor['04Prix'] = cols[1].text.strip()
            armor[u'05Bonus'] = cols[2].text.strip()
            armor[u'06BonusDexMax'] = cols[3].text.strip()
            armor[u'07Malus'] = cols[4].text.strip()
            armor[u'08ÉchecProfane'] = cols[5].text.strip()
            armor[u'09Vit9m'] = cols[6].text.strip()
            armor[u'10Vit6m'] = cols[7].text.strip()
            armor[u'11Poids'] = cols[8].text.strip()
            armor[u'99Complete'] = False

            armor['02Source'] = "MJ"
            if cols[9].text.strip() == "UC":
                armor['02Source'] = "AG"
            armor['EMPTY'] = ""
            liste.append(armor)
            armor = {}

#
# cette fonction ajoute les infos additionelles
#
def addInfos(liste, name, source):
    names = []
    # ugly fix
    name = name.replace('’','\'')
    if name.endswith('.'):
        name = name[:-1]
    if(name == u"Habits rembourrés"):
        names = [u"Vêtements rembourrés".lower()]
    elif(name == u"Armure lamellaire"):
        names = [u"Armure lamellaire (acier)".lower(),u"Armure lamellaire (fer)".lower(),u"Armure lamellaire (cuir)".lower(),u"Armure lamellaire (corne)".lower(),u"Armure lamellaire (pierre)".lower()]
    elif(name == u"Armure à plaques ou de plaques"):
        names = [u"Armure de plaques".lower()]
    elif(name == u"Écu en bois ou en acier"):
        names = [u"Écu (bois)".lower(),u"Écu (acier)".lower()]
    elif(name == u"Rondache en bois ou en acier"):
        names = [u"Rondache (bois)".lower(),u"Rondache (acier)".lower()]
    elif(name == u"Madu en acier ou en cuir"):
        names = [u"Madu (cuir)".lower(),u"Madu (acier)".lower()]
    elif(name == u"Rondache à manipulation rapide ou de preste usage, en bois ou en acier"):
        names = [u"Rondache de preste usage (bois)".lower(),u"Rondache de preste usage (acier)".lower()]
    elif(name == u"Gantelet d'armes (ou gantelet à fixations)"):
        names = [u"Gantelet d'armes".lower()]
    elif(name == u"Armure à plaques flexible ou agile"):
        names = [u"Armure de plaques flexible".lower()]
    elif(name == u"Armure de peau"):
        names = [u"Armure en peau".lower()]
    else:
        names = [name.lower()]

    # add infos to existing armors in list
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
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(html, 'h1',{'class':'separator'}, u"Armures classiques")

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
                    source = None
                else:
                    name = e.text.strip()
                    source = None
                    descr = ""
                    newObj = False
            elif e.name == 'br':
                descr += "\n"
            elif e.name is None or e.name == 'a':
                if not e.string is None:
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
yml = yml.replace(u'05Bonus',u'Bonus')
yml = yml.replace(u'06BonusDexMax',u'BonusDexMax')
yml = yml.replace('07Malus','Malus')
yml = yml.replace(u'08ÉchecProfane',u'ÉchecProfane')
yml = yml.replace('09Vit9m','Vit9m')
yml = yml.replace('10Vit6m','Vit6m')
yml = yml.replace(u'11Poids',u'Poids')
yml = yml.replace(u'12Description',u'Description')
yml = yml.replace(u'20Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)
