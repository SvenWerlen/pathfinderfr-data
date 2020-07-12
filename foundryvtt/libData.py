#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import re

#
# cette fonction tente de convertir un poids exprimé en texte en valeur (float)
#
def getWeight(weight):
  weight = weight.replace(",",".")
  
  try :  
    return float(weight) 
  except : 
    # just ignore
    weight
      
  m = re.search('([\d\.]+?) kg', weight)
  if m:
      return float(m.group(1))
  m = re.search('([\d\.]+?) g', weight)
  if m:
      return float(m.group(1))/1000
  return None


def getPrice(price):
  price = price.replace(",",".")
  
  try :  
    return float(price) 
  except : 
    # just ignore
    price
  
  m = re.search('([\d ]+?) po', price.replace('.',''))
  if m:
      return int(m.group(1).replace(' ', ''))
  return None


def extractQuantity(name):
    m = re.search('(.*)\((\d+?)\)(.*)', name)
    if m:
        name = m.group(1) + m.group(3)
        return [int(m.group(2)), name.replace("  ", " ").strip()]
    return [1, name]

def cleanTitle(title):
    return title[0].upper() + title[1:]
