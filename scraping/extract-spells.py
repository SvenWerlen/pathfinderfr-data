#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import yaml
from lxml import html
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
    from bs4 import NavigableString

DEBUG = False

liste = []

PROPERTIES = [ u"Nom", u"École", u"Niveau", u"Portée", u"Cibles", u"Zone", u"Zone d'effet", u"Effet", u"Temps d’incantation", u"Temps d'incantation", u"Composantes", u"Cible", u"Durée", u"Jet de sauvegarde", u"Résistance à la magie", u"Description"]


# récupérer la liste des pages
url = ["http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts.ashx",
       "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts%20(suite).ashx",
       "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Liste%20des%20sorts%20(fin).ashx"]

list = []
if DEBUG:
    parsed_html = BeautifulSoup(open("sortsA.txt"),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_all('li')
else:
    list = []
    for u in url:
        parsed_html = BeautifulSoup(urllib.urlopen(u).read(),features="lxml")
        list += parsed_html.body.find(id='PageContentDiv').find_all('li')

#for l in list:
#    element = l.find_next('a')
#    title = element.get('title')
#    link  = element.get('href')
#    print "Processing %s (%s)" % (title,link)
#exit(1)

def extractText(list):
    text = ""
    for el in list:
        if el.name == 'br':
            if text[-2:] != '\n\n':
                text += '\n'
        elif el.name in ('b','h2','h3'):
            if el.string:
                text += ' ' + el.string.strip().upper()
            else:
                text += ' ' + extractText(el.contents).upper()
        elif el.string:
            text += ' ' + el.string.strip()
        elif el.name in ('div','ul','li','i','a'):
            if el.name == 'li':
                text += '\n *'
            text += ' ' + extractText(el.contents)
        elif el.name in ('img'):
            # do nothing
            text
        else:
            print " - HTML element %s ignored!" % el.name

    return text.strip(' ').replace(u'¶','')


# itération sur chaque page
for l in list:
    sort = {}
    
    element = l.find_next('a')
    title = element.get('title')
    link  = element.get('href')
    
    print "Processing %s" % title
    pageURL = "http://www.pathfinder-fr.org/Wiki/" + link
    
    sort['Nom']=title
    sort['Reference']=pageURL
    
    if DEBUG:
        content = BeautifulSoup(open("sort5.html"),features="lxml").body.find(id='PageContentDiv')
    else:
        content = BeautifulSoup(urllib.urlopen(pageURL).read(),features="lxml").body.find(id='PageContentDiv')
              
    # lire les attributs
    text = ""
    for attr in content.find_all('b'):
        key = attr.text.strip()
        
        for s in attr.next_siblings:
            #print "%s %s" % (key,s.name)
            if s.name == 'b' or  s.name == 'br':
                break
            elif s.string:
                text += s.string

        if key in PROPERTIES:
            sort[key]=text.strip()
            descr = s.next_siblings
            text = ""
        else:
            print "- Skipping unknown property %s" % key

    # lire la description
    text = extractText(descr)
    
    sort['Description']=text.strip()
    
    # ajouter sort
    liste.append(sort)
    
    if DEBUG:
        break

if DEBUG:
    print yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
    exit(1)

with open("sorts.yml", "w") as f:
    yaml.safe_dump(liste, f, default_flow_style=False, allow_unicode=True)
