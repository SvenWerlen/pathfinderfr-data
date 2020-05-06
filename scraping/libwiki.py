#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import re


#
# cette fonction parse une ligne de wiki habituellement similaire à: "{s:BDTitre|Tigre|FP 4}"
# et produit une structure { 's': 'BDTitre', 'data': ["Tigre", "FP 4"] }
#
def parseWiki(data):
  # clean links before processing
  regex = re.compile('\[\[.*?\|.*?\]\]')
  for match in regex.findall(data):
    el = re.search('\[\[.*?\|(.*?)\]\]', match)
    data = data.replace(match, el.group(1))
  
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
  result = {}
  while True:
    el = re.search("'''(.+?)'''(.+)", data)
    if el:
      key = el.group(1).strip()
      hasMore = el.group(2).find("'''")
      if hasMore > 0:
        result[key.lower()] = cleanValue(el.group(2)[0:hasMore].strip())
        data = el.group(2)[hasMore:]
      else:
        result[key.lower()] = cleanValue(el.group(2).strip())
        return result
    else:
      return result

#
# nettoie la valeur de certaines particularités
#
def cleanValue(value):
  if value.endswith(',') or value.endswith(';') or value.endswith('.'):
    value = value[:-1].strip()
  return value

#
# cette fonction récupère et convertit une valeur en chiffre
# +3 => 3, 1.000 => 1000, '-' => None
#
def parseNumber(number):
  number =  number.replace(',','').replace('.','').replace(' ','').replace('–','-').strip()
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
  return text.replace("[[", "").replace("]]", "").replace("''", "").replace("'''", "").strip()

#
# cette fonction tente d'ajouter une clé/valeur sur un dict
# lance une exception si la valeur existe déjà pour éviter les erreurs
#
def setValue(dictObj, key, value):
  if key in dictObj:
    raise ValueError("'%s' already exist!" % key)
  
  dictObj[key] = value

#
# cette fonction tente d'extraire une attaque et la converture sous une forme structurées
# morsure, +16 (2d6+7), 2 griffes, +15 (1d8+5)
# => [ { 'nom': "morsure", 'attaque': "+16", 'dommages': "2d6+7" }, ...]
# 
def extractAttacks(text):
  text = cleanText(text)
  
  liste = []
  if text.startswith('nuée'):
    attack = re.search('(.*)? \((.*?)\)', text)
    if attack:
      nom = attack.group(1).replace(',','').strip()
      dmg = attack.group(2)
      liste.append( { 'attaque': nom, 'dommages': dmg } )
    else:
      raise ValueError("Invalid attack format '%s'" % text)
    
  else:
    regex = re.compile('(.*?) ([\+-][\+0-9/]+) (contact )?\((.*?)\)')
    for match in regex.findall(text):      
      nom = match[0].replace(',','').strip()
      if nom.startswith('et') or nom.startswith('ou'):
        nom = nom[2:].strip()
      bon = match[1]
      typ = match[2].strip()
      dmg = match[3]
      newEl = { 'attaque': nom, 'bonus': bon, 'dommages': dmg }
      if len(typ) > 0:
        newEl['type'] = 'contact'
      liste.append( newEl )
    
  return liste
