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
MOCK_RAGE = None
#MOCK_RAGE = "mocks/barbare-rages.html"       # décommenter pour tester avec les rages pré-téléchargées


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

# vérification des paramètres
if len(sys.argv) < 1:
    print("Usage: %s" % sys.argv[0])
    exit(1)

liste = []


if MOCK_RAGE:
    content = BeautifulSoup(open(MOCK_RAGE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen("http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.pouvoirs%20de%20rage.ashx").read(),features="lxml").body

section = jumpTo(html, 'h2',{'class':'separator'}, u"Description des pouvoirs de rage")

source = None
sourceNext = None
for s in section:
    if s.name == 'div':
        rage = {'4Source':'MJ','5Niveau':1}
        newObj = False
        brCount = 0
        descr = ""
        for e in s.children:
            if e.name == 'h3':
                if newObj:
                    rage['2Classe'] = 'Barbare'
                    rage['6Description'] = descr.strip()
                    if not sourceNext is None:
                        rage['4Source'] = sourceNext
                    rage['EMPTY'] = ""
                    liste.append(rage)
                    sourceNext = source
                    source = None
                    rage = {'4Source':'MJ','5Niveau':1}
                    brCount = 0
                    descr = ""
                else:
                    sourceNext = source
                rage['1Nom'] = "Rage: " + e.text.replace('¶','').strip()
                newObj = True
            elif e.name == 'b' and e.text == u'Prérequis':
                prerequis = str(e.next_sibling)
                if prerequis.startswith("'"):
                    prerequis = prerequis[1:]
                m = re.search(',? ?niveau (\d+)', prerequis)
                if m:
                   rage['5Niveau'] = int(m.group(1))
                   prerequis = re.sub(r',? ?niveau \d+', '', prerequis)
                rage[u'3Prérequis']=prerequis.replace(':','').strip()
            elif e.name == 'br':
                brCount+=1
                if(brCount==2 and u'3Prérequis' in rage):
                    descr = ""
            elif e.name is None or e.name == 'a':
                descr += e.string
            elif e.name == 'div':
                for c in e.children:
                    if c.name == 'img':
                        if('logoAPG' in c['src']):
                            source = 'MJRA'
                        elif('logoUC' in c['src']):
                            source = 'AG'
                        elif('logoMCA' in c['src']):
                            source = 'MCA'
                        else:
                            print(c['src'])
                            exit(1)
                    elif c.name == 'a':
                        rage[u'7Référence']="http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.pouvoirs%20de%20rage.ashx" + c['href']
        ## last element
        rage['2Classe'] = 'Barbare'
        rage['6Description'] = descr.strip()
        if not sourceNext is None:
            rage['4Source'] = sourceNext
        rage['EMPTY'] = ""
        liste.append(rage)
            

yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace('1Nom','Nom')
yml = yml.replace('2Classe','Classe')
yml = yml.replace(u'3Prérequis',u'Prérequis')
yml = yml.replace('4Source','Source')
yml = yml.replace('5Niveau','Niveau')
yml = yml.replace('6Description','Description')
yml = yml.replace(u'7Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)
