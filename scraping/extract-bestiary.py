# -*- coding: utf-8 -*-

import urllib.request
import re
from bs4 import BeautifulSoup
from operator import itemgetter

from libhtml import jumpTo, html2text, getValidSource, mergeYAML

def extractText(list):
    text = ""
    for el in list:
        text += html2text(el)
    return text

URLs = [{'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Monstres.ashx"}]

List_URLSs = []

for u in URLs:
    parsed_html = BeautifulSoup(urllib.request.urlopen(u['URL']).read(), features="lxml").find(class_='page espace-col').find_all(class_='pagelink')
    for link in parsed_html:
        completeLink = 'https://www.pathfinder-fr.org/Wiki/'+link['href']
        if completeLink not in List_URLSs:
            List_URLSs.append(completeLink)

FIELDS = ['Nom', 'FP', 'Source', 'Typologie', 'Caractéristiques', 'Description', 'Référence']
MATCH = ['Nom']
IGNORE = ['Source']

list = []
list_names = []
list_no_FP = []

num = 0

for u in List_URLSs:

    contentTag = BeautifulSoup(urllib.request.urlopen(u).read(), features="lxml").find(id='content')
    BDTags = contentTag.find_all(class_='BD')
    if len(BDTags) == 0:
        print('This URL, ' + u + ', does not contain correct data about a monster.')
        continue
    else:
        for BDTag in  BDTags:
            monster = {}
            titreTag = BDTag.find(class_='BDtitre')
            if titreTag is None:
                print('This URL, '+u+', does not contain correct data about a monster.')
                continue
            else:
                titre = ''
                name = ''
                fp = ''
                for string in titreTag.strings:
                    titre += string
                regex = r"(.*)(FP.*)"
                matches = re.finditer(regex, titre, re.MULTILINE)
                for matchNum, match in enumerate(matches, start=1):
                    for groupNum in range(0, len(match.groups())):
                        groupNum = groupNum + 1
                        if groupNum == 1:
                            name = match.group(groupNum)
                        if groupNum == 2:
                            fp = match.group(groupNum)
                if name == '':
                    list_no_FP.append({'Nom':titre, 'URL': u})
                    print('This specific BDTag, '+titre+', in URL, ' + u + ', does not contain correct data about a monster (No Name).')
                    continue
                if fp == '':
                    list_no_FP.append({'Nom': titre, 'URL': u})
                    print('This specific BDTag, '+titre+', in URL, ' + u + ', does not contain correct data about a monster (No FP).')
                    continue
                if name in list_names:
                    print('This Name, ' + name + ', is already stored.')
                    continue
                list_names.append(name)
                monster['Nom'] = name
                monster['FP'] = fp
                monster['Source'] = ''
                typologyTag = titreTag.find_next_sibling()
                monster['Typologie'] = ''
                if typologyTag is not None:
                    imgTypeTags = typologyTag.find_all('img')
                    if len(imgTypeTags) > 0 :
                        for img in imgTypeTags:
                            monster['Typologie'] += img['title'] + ', '
                monster['Typologie'] = monster['Typologie'][:-2]
                monster['Caractéristiques'] = ''
                ulTag = BDTag.select_one('.BD > ul')
                divTags = BDTag.select('.BDtexte, .BDsoustitre')
                if ulTag is None and len(divTags) == 0:
                    list_no_FP.append({'Nom': monster['Nom'], 'URL': u})
                    print('This Name, ' + monster['Nom'] + ', has no Technical Description attached to it.')
                    continue
                else:
                    if len(divTags) > 0:
                        for string in divTags[0].stripped_strings:
                            source = string
                        if source.find('Source') != -1 or source.find('Bestiaire') != -1 or source.find('Bestiare') != -1:
                            monster['Source'] = source.replace('Source : ', '')
                        divTags.pop(0)
                        for div in divTags:
                            for string in div.strings:
                                monster['Caractéristiques'] += string
                        monster['Caractéristiques'] = monster['Caractéristiques'].replace('\n\n','\n')
                    if ulTag is not None:
                        liTags = ulTag.find_all('li')
                        if monster['Source'] == '':
                            if liTags[0].string is None:
                                source = extractText(liTags[0])
                            else:
                                source = liTags[0].string.strip()
                            if source.find('Source') == -1 and source.find('Bestiaire') == -1 and source.find('Bestiare') == -1:
                                list_no_FP.append({'Nom': monster['Nom'], 'URL': u})
                                print('This Name, ' + monster['Nom'] + ', has no Source attached to it.')
                                continue
                            monster['Source'] = source.replace('Source : ', '')
                        liTags.pop(0)
                        for li in liTags:
                            for string in li.strings:
                                monster['Caractéristiques'] += string
                            monster['Caractéristiques'] += '\n'
                if monster['Caractéristiques'] == '':
                    list_no_FP.append({'Nom': monster['Nom'], 'URL': u})
                    print('This Name, ' + monster['Nom'] + ', has no Technical Description attached to it.')
                    continue
                monster['Description'] = ''
                descriptionTag = contentTag.select_one('.Bestiaire td:last-child > div')
                if descriptionTag is not None:
                    monster['Description'] = extractText(descriptionTag)
                monster['Référence'] = u
                list.append(monster)
                num += 1

listSorted = sorted(list, key=itemgetter('Nom'))

print('Number in list_no_FP', len(list_no_FP))
print('Number in list', len(listSorted))

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/bestiary.yml", MATCH, FIELDS, HEADER, listSorted, IGNORE)

for elt in list_no_FP:
    print(elt['Nom'], ' ', elt['URL'])