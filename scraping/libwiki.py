#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import re


#
# cette fonction parse une ligne de wiki habituellement similaire à: "{s:BDTitre|Tigre|FP 4}"
# et produit une structure { 's': 'BDTitre', 'data': ["Tigre", "FP 4"] }
#
def parseWiki(data):
  el = re.search('^{s:(\w+)\|(.*)}$', data.strip())
  if el:
    return { 's': el.group(1), 'data': el.group(2).split('|') }
  el = re.search('^\*(.*)$', data.strip())
  if el:
    return { 's': 'BDTexte', 'data': el.group(1).split('|') }
  else:
    return None

#
# cette fonction sépare les éléments en se fiant sur les éléments en gras: "'''Réf''' +7, '''Vig''' +8, '''Vol''' +3"
# => { 'Réf' : "+7", 'Vig' : "+8", 'Vol' : "+3" }
#
def parseData(data):
  regex = re.compile("'''(.+?)'''([^']+)")
  matches = regex.findall(data.strip())
  data = {}
  for m in matches:
    key = m[0].strip()
    value = m[1].strip()
    
    # clean value
    if value.endswith(',') or value.endswith(';') or value.endswith('.'):
      value = value[:-1].strip()
    
    data[key.lower()] = value

  return data


#
# cette fonction récupère et convertit une valeur en chiffre
# +3 => 3, 1.000 => 1000, '-' => None
#
def parseNumber(number):
  number =  number.replace(',','').replace('.','').replace(' ','').strip()
  if number == '-' or number == '—':
    return 0
  else:
    return int(number)
  
def extractNumberWithSpecial(number):
  values = number.split(';')
  # ex: ; +5 contre les poisons
  if len(values) > 2:
    exit(1)
  if len(values) > 1:
    return { 'num': parseNumber(values[0]), 'special': cleanText(values[1]) }
  # ex: (+12 contre les maladies non magiques)
  el = re.search('(.*)\((.*)\)', number.strip())
  if el:
    return { 'num': parseNumber(el.group(1)), 'special': cleanText(el.group(2)) }
    
  return { 'num': parseNumber(number) }

#
# nettoie le texte de certaines particularités
#
def cleanText(text):
  return text.replace("[[", "").replace("]]", "").strip()

#
# cette fonction tente d'ajouter une clé/valeur sur un dict
# lance une exception si la valeur existe déjà pour éviter les erreurs
#
def setValue(dictObj, key, value):
  if key in dictObj:
    raise ValueError("'%s' already exist!" % key)
  
  dictObj[key] = value
  
