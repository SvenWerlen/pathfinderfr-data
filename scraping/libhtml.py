#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.parse
import yaml
import re

#
# cette fonction permet de convertir un tableau en texte
#

TYPE_DESCR = 1
TYPE_PROPS = 2
TYPE_FABRI = 3

VALID_PROPS   = ["aura", "nls", "conditions", "emplacement", "poids", "prixalt"] 
VALID_FABRICS = ["coût", "conditions"]

MODE_TEXT = 1 # pure text
MODE_HTML = 2 # clean HTML

#
# cette fonction permet de sauter à l'élément recherché et retourne les prochains éléments
#
def jumpTo(html, afterTag, afterCond, elementText):
    seps = html.find_all(afterTag, afterCond);
    for s in seps:
        if s.text.lower().strip().startswith(elementText.lower()):
            return s.next_siblings

#
# cette fonction extrait le texte du prochain élément après ...
#
def findAfter(html, afterTag, afterCond, searched):
    elements = html.find_next(afterTag, afterCond).next_siblings
    for el in elements:
        if el.name == searched:
            return html2text(el)

#
# cette fonction extrait le texte pour une propriété <b>propriété</b> en prenant le texte qui suit
#
def findProperty(html, propName, removeEndDot = True):
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
            
            value = value.strip()
            if removeEndDot:
                return value.replace('.','').strip()
            else:
                return value

    return None

#
# cette fonction convertit un tableau en texte
#
def table2text(table, mode = MODE_TEXT):
    if table is None:
        return ""
    text = ""
    
    if mode == MODE_TEXT:
      first = True
      for tr in table.find_all('tr'):
          if first:
              first = False
          else:
              text += "• "
          for td in tr.find_all('td'):
              text += html2text(td, True, mode).replace('\n','') + ", "
          text = text[:-2] + "\n"

    else:
      text += "<table>"
      caption = table.find('caption')
      if caption:
          text += "<caption>%s</caption>" % caption.text
      for tr in table.find_all('tr'):
          classes = "title" if 'class' in tr.attrs and "titre" in tr.attrs['class'] else ""
          classes = " class=\"%s\"" % classes if len(classes) > 0 else ""
          text += "<tr%s>" % classes
          for td in tr.find_all('td'):
              colspan = " colspan=\"%s\"" % td.attrs['colspan'] if 'colspan' in td.attrs else ""
              classes = "note" if 'class' in td.attrs and "note" in td.attrs['class'] else ""
              classes = " class=\"%s\"" % classes if len(classes) > 0 else ""
              text += "<td%s%s>%s</td>" % (colspan, classes, html2text(td))
          text += "</tr>"
      text += "</table>"

    return text



def html2text(htmlEl, skipDiv = True, mode = MODE_TEXT):
    if htmlEl.name is None or htmlEl.name == 'a':
        if htmlEl.string is None:
            return ""
        else:
            return htmlEl.string.replace("\n"," ")
    # ignore <sup>
    elif htmlEl.name == 'sup':
        return ""
    elif htmlEl.name == 'i':
        text = ""
        for c in htmlEl.children:
            text += html2text(c, skipDiv, mode)
        return text.replace("\n"," ")
    elif htmlEl.name == 'br':
        return "\n" if mode == MODE_TEXT else "<br/>"
    elif htmlEl.name == 'b':
        if mode == MODE_TEXT:
            text = ""
            for c in htmlEl.children:
                text += html2text(c, skipDiv, mode)
            return text.replace("\n"," ").upper()
        else:
            text = "<b>"
            for c in htmlEl.children:
                text += html2text(c, skipDiv, mode)
            return text + "</b>"
    elif htmlEl.name == 'center':
        return table2text(htmlEl.find('table'), mode)
    elif not skipDiv and htmlEl.name == 'div' and htmlEl.find('table'):
        return table2text(htmlEl.find('table'), mode)
    elif htmlEl.name == 'ul':
        if mode == MODE_TEXT:
            text = ""
            for li in htmlEl.find_all('li'):
                text += "• " + li.text + "\n"
            return "\n" + text + "\n"
        else:
            text = "<ul>"
            for li in htmlEl.find_all('li'):
                text += "<li>%s</li>" % li.text
            return text + "</ul>"
        
    elif htmlEl.name == "td":
        text = ""
        for c in htmlEl.children:
            text += html2text(c, skipDiv, mode)
        return text
    elif htmlEl.name == "h2" or htmlEl.name == "h3":
        if mode == MODE_TEXT:
            return cleanSectionName(htmlEl.text).upper()
        else:
            return "<%s>%s</%s>" % (htmlEl.name, cleanSectionName(htmlEl.text), htmlEl.name)
    elif htmlEl.name == "abbr":
        return htmlEl.text
    else:
        return ""

  
#
# cette fonction nettoie la valeur d'une propriété
# 
def cleanProperty(text, noReturn = True):  
    text = text.strip()
    if text.startswith(':'):
        text = text[1:].strip()
    if text.startswith('.'):
        text = text[1:].strip()
    
    if text.endswith('.') or text.endswith(';'):
        text = text[:-1].strip()
    if noReturn:
      return text.replace("\n", " ")
    else:
      return text

#
# vérifie chaque propriété pour savoir si elle est valide
#
def checkProperties(caracs, valid):
    for c in caracs:
        #print("Checking %s..." % c)
        found = False
        for v in valid:
            #print("- %s == %s?" % (c.lower(), v.lower()))
            if c.lower() == v.lower():
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
                        try:
                            props["nls"] = int(value)
                        except:
                            props["nls"] = value
                        
                
                else:
                    props[curProp] = cleanProperty(value)
                    
            curProp = el.text.strip().lower()
            # "Prix" est déjà déterminé
            if curProp == "prix":
                curProp = "prixAlt"
                        
            curValue = ""
        else:
            curValue += html2text(el)
    # dernière entrée
    if curProp and not curProp in props:
        props[curProp] =  cleanProperty(curValue)
    return props


#
# cette fonction nettoie un libellé
#
def cleanLabel(nom):
    value = nom.strip()
    if value.endswith('.'):
        value = value[:-1]
    return value

#
# cette fonction nettoie un nom de section
#
def cleanSectionName(nom):
    value = nom.replace("¶", "")
    return value.strip()

#
# cette fonction nettoie une description
#
def cleanInlineDescription(desc):
    return desc.replace('\n', ' ').replace('\t', ' ').replace('\r', '').strip()

#
# recherche dans le texte "... niveau XX"
# Ex: À partir du niveau 17, le barbare ...
#
def extractLevel(text, maxdist):
    idx = text.find(' niveau ')
    if idx >=0 and idx < maxdist:
        m = re.search(' ?niveau (\d+)', text)
        if m:
            return int(m.group(1))
    return 1

#
# check source
#
def getValidSource(src, exitOnInvalid = True):
    src = src.upper()
    VALID = ["MJ", "MJRA", "MCA", "MR", "B1", "AG", "AM", "AO", "CCMI", "PAIZO", "RTT", "PMI", "MMI", "FF", "CM", "AE", "MPNJ", "MM", "AA", "HOTS", "RSE", "UI", "UW", "WOV" ];
    for v in VALID:
        if src == v:
            return src
    if src == "M" or src == "F":
        return "MJ"
    if src == "UM":
        return "AM"
    if src == "UC":
        return "AG"
    if src == "APG":
        return "MJRA"
    if src == "MJ-UC" or src == "MDJ-CA":
        return "MJ"
    if src == "partagé":
        return None
    if src == "ISWG":
        return "CCMI"
    if src == "CMY":
        return "CM"
    if src == "BLOG PAIZO":
        return "PAIZO"
    if src.startswith("MR"):
        return "MR"
    if src == "ADM":
        return "AM"
    if src == "FAMF" or src == "":
        return "FF"

    print('Source invalide: ' + src)
    if exitOnInvalid:
        exit(1)

#
# extrait la source
#
def extractSource(div):
    for c in div.children:
        if c.name == 'img':
            if('logoAPG' in c['src']):
                return 'MJRA'
            elif('logoUC' in c['src']):
                return 'AG'
            elif('logoMR' in c['src']):
                return 'MR'
            elif('logoMCA' in c['src']):
                return 'MCA'
            elif('logoUM' in c['src']):
                return 'AM'
            elif('logoMC' in c['src']):
                return 'MC'
            elif('logoOA' in c['src']):
                return 'AO'
            elif('logoMMI' in c['src']):
                return 'MMI'
            elif('logoPMI' in c['src']):
                return 'PMI'
            elif('logoAE' in c['src']):
                return 'AE'
            elif('logoref' in c['src']): # ignore
                continue
            else:
                print("Invalid source: " + c['src'])
                exit(1)
    return None

#
# cette fonction extrait la liste des propriétés basée sur le format suivant
#
# <b>Nom de la propriété</b> Texte descriptif
# ...
# <h?> Fin de la liste
#
def extractList(htmlElement):
    newObj = False
    liste = []
    nom = ""
    descr = ""
    for el in htmlElement.next_siblings:
        if el.name in ('h1', 'h2', 'h3', 'h4'):
            break
        if el.name == "b":
            if newObj:
                liste.append({ 'Name': nom, 'Desc': cleanInlineDescription(descr) })
            nom = cleanLabel(el.text)
            descr = ""
            newObj = True
        
        elif el.name is None or el.name == 'a':
            descr += html2text(el)
            
    # last element        
    liste.append({ 'Name': nom, 'Desc': cleanInlineDescription(descr) })
    
    return liste

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
    return { **{'nomAlt': titre, 'descr': descr.strip()}, **caracs }


def cleanText(text):
    text = text.replace('\xa0', ' ')
    return re.sub(' +', ' ', text).replace("’","'").strip()

def cleanDescription(descr):
    return cleanText(descr).replace("\n\n•","\n•").strip()

def cleanName(name):
    return cleanText(name).replace("\n", " ");

def cleanNameForMatch(name):
    name = cleanText(name)
    #m = re.search('(.*)\([a-zA-Z]+\)', name)
    #if m:
    #    return m.group(1).strip()
    #else:
    #    return name
    return name.lower()


# Returns a text without the part in parenthesis. Eg: Dé (la bouteille) => Dé
def removeParenthesis(text):
    match = re.search('(.*)\(.+?\).*', text)
    if match:
        return match.group(1).strip()
    return text

#
# cette fonction extait une propriété (format BD type 2)
#
#   NOM
#   -------------
#   Caractéristiques
#   -------------
#   Description OR Caractéristiques (A&E)
#   -------------
#   Fabrication (optionnel) OR Creation (A&E)
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
            if el.text.lower() == "description" or el.text.lower() == "caractéristiques":
                section = TYPE_DESCR
            elif el.text.lower() == "fabrication" or el.text.lower() == "création":
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
    return { **{'nomAlt': cleanName(titre), 'descr': cleanDescription(descr)}, **props, **fabrics }


#
# cette fonction fusionne un YAML avec un existant en respectant les règles suivantes
# - l'ordre des champs
# - un retour à la ligne (ligne vide) entre chaque entrée
# - insertion uniquement à la fin
# - aucune suppression
# - modification des existantes (merge) sur la base du nom
#
def mergeYAML(origPath, matchOn, order, header, yaml2merge, ignoreFields = []):
    
    liste = []
    
    # lire le copyright (à intégrer en haut de chaque fichier)
    with open('../data/COPYRIGHT.TXT', 'r') as file:
        COPY = file.read()
    
    # lire le fichier original avec lequel fusionner
    with open(origPath, 'r') as stream:
        try:
            liste = yaml.safe_load(stream)
            if not liste:
              liste = []
        except yaml.YAMLError as exc:
            print(exc)
            exit(1)
    
    
    # préparer les champs pour le tri
    FIELDS = {}
    idx = 1
    for o in order:
        FIELDS[o]="{:02d}{:s}".format(idx,o)
        idx += 1

    # s'assurer que toutes les nouvelles entrées on un "nom"
    for el in yaml2merge:
        if not "Nom" in el:
            print("Entrée invalide (ne contient pas de nom)" % el)
            print(el)
            exit(1)
            
    # fusionner les listes
    for el in yaml2merge:
        idx = 0
        found = False
        for elOrig in liste:
            match = True
            # s'assurer que tous les champs correspondent
            for m in matchOn:
                # hotfix (automatch)
                #if urllib.parse.unquote(el['Référence']) == urllib.parse.unquote(elOrig['Référence']) and not 'first' in elOrig:
                #    break
                val1 = cleanNameForMatch(el[m]) if m in el else ""
                val2 = cleanNameForMatch(elOrig[m]) if m in elOrig else ""
                if val1 != val2:
                    match = False
                    break
            if match:
                #print("Match found for %s with %s" % (el['Nom'], liste[idx]['Nom']))
                old = liste[idx]
                liste[idx] = el
                for f in ignoreFields:
                    liste[idx][f] = old[f]
                liste[idx]['first'] = True
                found = True
                break
            idx += 1
        
        if not found:
            print("Élément '%s' ajouté" % el['Nom'])
            el['first'] = True
            liste.append(el)
    
    # préparer la liste finale (tri, retour de ligne, etc.)
    retListe = []
    for el in liste:
        newEl = {}
        
        # change field keys to apply sorting
        for k in el.keys():
            if k == 'first':
                continue
            if k in FIELDS.keys():
                newEl[FIELDS[k]]=el[k]
            else:
                print("Champs %s ne peut être trié!" % k)
                print(el)
                exit(1)
        
        newEl['EMPTY'] = ""
        retListe.append(newEl)
    
    result = yaml.safe_dump(retListe,default_flow_style=False, allow_unicode=True)
    for f in FIELDS:
        result = result.replace(FIELDS[f], f)
    result = result.replace("EMPTY: ''",'')
    
    # écrire le résultat dans le fichier d'origine
    outFile = open(origPath, "w")
    outFile.write(COPY + header + result)
