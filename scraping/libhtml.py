#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re

#
# cette fonction permet de convertir un tableau en texte
#

TYPE_DESCR = 1
TYPE_PROPS = 2
TYPE_FABRI = 3

VALID_PROPS   = ["aura", "nls", "conditions", "emplacement", "poids"]
VALID_FABRICS = ["coût", "conditions"]



def table2text(table):
    text = ""
    first = True
    for tr in table:
        if first:
            first = False
        else:
            text += "*) "
        for td in tr:
            text += td.text.strip() + ", "
        text = text[:-2] + "\n"

    return text


def html2text(htmlEl):
    if htmlEl.name is None or htmlEl.name == 'a':
        return htmlEl.string
    # ignore <sup>
    elif htmlEl.name == 'sup':
        return ""
    elif htmlEl.name == 'i':
        return htmlEl.text.replace("\n"," ")
    elif htmlEl.name == 'br':
        return "\n"
    elif htmlEl.name == 'b':
        return "\n" + htmlEl.text.replace("\n"," ").upper()
    elif htmlEl.name == 'center':
        return table2text(htmlEl.find('table'))
    elif htmlEl.name == 'ul':
        for li in htmlEl.find_all('li'):
            text = ""
            for c in li.children:
                text += html2text(c)
            return text
    elif htmlEl.name == "td":
        text = ""
        for c in htmlEl.children:
            text += html2text(c)
        return text
    else:
        return ""

  
#
# cette fonction nettoie la valeur d'une propriété
# 
def cleanProperty(text):  
    text = text.strip()
    if text.endswith('.') or text.endswith(';'):
        text = text[:-1].strip()
    return text

#
# vérifie chaque propriété pour savoir si elle est valide
#
def checkProperties(caracs, valid):
    for c in caracs:
        #print("Checking %s..." % c)
        found = False
        for v in valid:
            if c.lower() == v:
                found = True
                break
        if not found:
            print("Caractéristique invalide '%s' détectée" % c)
            print(caracs)
            exit(1)

#
# cette fonction extrait les propriétés
#
def extractProps(liste):
    curProp = None
    curValue = ""
    props = {}
    for el in liste:
        if el.name == 'b':
            if curProp:
                value = cleanProperty(curValue)
                # hack pour NLS fusionné avec conditions de création. 
                # Ex: NLS 4 ; Création d’armes et armures magiques, graisse ; 
                # => NLS 4
                # => Création: Création d’armes et armures magiques, graisse
                if curProp == "nls":
                    NLS = re.search('(\d+) *; *(.+)', value)
                    if NLS:
                        props["nls"] = int(NLS.group(1))
                        props["conditions"] = cleanProperty(NLS.group(2))
                    else:
                        props["nls"] = int(value)
                # ignorer "Prix" qui est déjà déterminé
                elif curProp != "prix":
                    props[curProp] = value
                
                    
            curProp = el.text.strip().lower()
            curValue = ""
        else:
            curValue += html2text(el)
    # dernière entrée
    if curProp and curProp != "prix":
        props[curProp] =  cleanProperty(curValue)
    return props

#
# cette fonction extait une propriété (format BD type 1)
#
#   NOM
#   -------------
#   Description
#   -------------
#   Caractéristiques
#
def extractBD_Type1(html):
    titreEl = html.find('div',{'class':['BDtitre']})
    titre = titreEl.text.strip()
    #print("Extracting %s..." % titre)
    
    descr = ""    
    section = TYPE_DESCR

    # lire la partie descriptive
    for el in titreEl.next_siblings:
        if el.name == "div" and 'class' in el.attrs and "box" in el.attrs['class']:
            if "caractéristiques" != el.text.lower():
                print("Section invalide: %s" % el.text)
                exit(1)
            section = TYPE_PROPS
            continue
        
        if section == TYPE_DESCR:
            descr += html2text(el)
        elif section == TYPE_PROPS:
            if el.name == 'ul':
                caracs = extractProps(el.find('li').children)

    # validation des propriétés
    checkProperties(caracs,VALID_PROPS)

    # debug (décommenter)
    #print(props)
    
    # merge props
    return { **{'descr': descr.strip()}, **caracs }

#
# cette fonction extait une propriété (format BD type 2)
#
#   NOM
#   -------------
#   Caractéristiques
#   -------------
#   Description
#   -------------
#   Fabrication (optionnel)
#
def extractBD_Type2(html):
    
    titreEl = html.find('div',{'class':['BDtitre']})
    titre = titreEl.text.strip()
    #print("Extracting %s..." % titre)
    
    
    descr = ""    
    section = TYPE_PROPS

    # lire la partie descriptive
    props = []
    fabrics = []
    for el in titreEl.next_siblings:
        if el.name == "div" and 'class' in el.attrs and "box" in el.attrs['class']:
            if el.text.lower() == "description":
                section = TYPE_DESCR
            elif el.text.lower() == "fabrication":
                section = TYPE_FABRI
            else:
                print("Section invalide: %s" % el.text)
                exit(1)
            continue
        
        if section == TYPE_DESCR:
            descr += html2text(el)
        elif section == TYPE_PROPS:
            props.append(el)
        elif section == TYPE_FABRI:
            fabrics.append(el)

    props = extractProps(props)
    fabrics = extractProps(fabrics)
    
    # debug (décommenter)
    #print(props)
    #print(fabrics)
    
    # validation des propriétés
    checkProperties(props,VALID_PROPS)
    checkProperties(fabrics,VALID_FABRICS)
    
    # merge props
    return { **{'descr': descr.strip()}, **props, **fabrics }
