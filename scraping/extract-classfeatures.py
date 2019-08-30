#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, html2text, cleanSectionName, cleanInlineDescription, extractLevel, mergeYAML

## Configurations pour le lancement
MOCK_CF = None
#MOCK_CF = "mocks/classe-maitre-espion.html"       # décommenter pour tester avec les rages pré-téléchargées

FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']
URL = "http://www.pathfinder-fr.org/Wiki/"

classes = []
with open("../data/classes.yml", 'r') as stream:
    try:
        classes = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

liste = []
listeDescr = []
listeNames = {}

print("Extraction des aptitude...")

def addClassFeature(name, link, level):
    if name == "—":
        return
    if "#" in link:
        link = "#" + link.split("#")[1]
    for el in listeDescr:
        if el['RéférenceAlt'] and el['RéférenceAlt'] == link:
            add = dict(el)
            add['Nom'] = name.strip()
            add['Nom'] = add['Nom'][0].upper() + add['Nom'][1:]
            add['Niveau'] = level
            # si nom déjà dans liste => ajouter #D pour distinguer
            matches = [c for c in listeNames if add['Nom'] == c]
            if matches:
                listeNames[add['Nom']] += 1
                add['Nom'] += " #%s" % listeNames[add['Nom']]
            else:
                listeNames[add['Nom']] = 1
            
            del add['RéférenceAlt']
            liste.append(add)
            return
    # non-trouvé!
    print("Aucune description correspondant à '%s'" % link)
    exit(1)

def extractDescriptions(cl, listeDescr, section, baseURL):
    newObj = False
    descr = ""

    altLink = None
    for s in section:
        if s.name == 'h3':
            if newObj:
                classfeature['Description'] = descr
                classfeature['Niveau'] = extractLevel(classfeature['Description'], 150)
                listeDescr.append(classfeature)
                classfeature = {'Auto': True, 'RéférenceAlt': altLink }
                altLink = None
                descr = ""
            else:
                classfeature = {'Auto': True, 'RéférenceAlt': altLink }
                
            newObj = True
            classfeature['Nom'] = cleanSectionName(s.text)
            classfeature['Classe'] = cl['Nom']
            classfeature['Source'] = cl['Source']
            classfeature['Référence'] = baseURL + s.find('a')['href']

        elif s.name == 'div' and s.has_attr('class') and (s['class'][0] == 'ref'):
            altLink = s.find('a')['href']
        else:
            descr += html2text(s)
    
    ## last element
    classfeature['Description'] = descr
    classfeature['Niveau'] = extractLevel(classfeature['Description'], 150)
    listeDescr.append(classfeature)
    
    

idx = 0
for cl in classes:
    idx+=1
    if idx != 8:
        continue

    print("Extraction des aptitudes de '%s' ..." % cl['Nom'])

    if MOCK_CF:
        content = BeautifulSoup(open(MOCK_CF),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(cl['Référence']).read(),features="lxml").body

    sectionNames = ["Descriptif de la classe", "Caractéristiques de la classe", "Caractéristiques de classe"]
    section = None
    for s in sectionNames:
        section = jumpTo(content, 'h2',{'class':'separator'}, s)
        if section:
            break

    if not section:
        print("- Section Description/Caractéristiques pour la classe %s n'a pas être trouvée!!!" % cl['Nom'])
        continue

    #
    # extraction des descriptions des aptitudes
    #
    listeDescr = []
    extractDescriptions(cl, listeDescr, section, cl['Référence'])
    
    #
    # extraction des descriptions provenant d'autres pages
    #
    links = content.find_next('table',{"class": "tablo"}).find_all('a')
    for a in links:
        link = a['href']
        if '#' in link:
            link = link.split('#')[0]
        if link.lower() not in cl['Référence'].lower():
            print("- Extraction sous-page: %s" % link)
            detailPage = BeautifulSoup(urllib.request.urlopen(URL + link).read(),features="lxml").body
            extractDescriptions(cl, listeDescr, detailPage.find('div',{"id": "PageContentDiv"}).children, URL + link)
            break
    
    #
    # extraction des aptitudes depuis le tableau
    #
    rows = content.find_next('table',{"class": "tablo"}).find_all('tr')
    column = 0
    level = 1
    for r in rows:
        # trouver "Spécial" dans les tites pour identifier la bonne colonne
        if r.has_attr('class') and (r['class'][0] == 'titre' or r['class'][0] == 'soustitre'):
            idx = 0
            for td in r.find_all('td'):
                if td.text == "Spécial":
                    column = idx
                idx+=1
            continue
        
        # colonne non-trouvée?
        if column == 0:
            print("Incapable de trouver la liste des aptitudes dans le tableau!")
            exit(1)
        
        tds = r.find_all('td')
        
        # ignore footers
        if len(tds) <= column:
            continue
        
        # extraire chaque aptitude
        curName = ""
        curHref = ""
        
        for c in tds[column].children:
            if c.name == "a":
                curHref = c['href']
            elif c.name is None and "," in c.string :
                val = c.string.split(',')
                curName += val[0]
                addClassFeature(curName, curHref, level)
                curName = ""
                curHref = ""
                continue
            elif c.name == "br":
                continue
            curName += c.string
        # dernier élément
        if len(curName.strip()) > 0:
            addClassFeature(curName, curHref, level)
        
        level += 1
    
    if MOCK_CF:
        break
    break

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
