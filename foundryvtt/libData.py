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
    return title[0] + title[1:].lower()

def generateHTML(description):
    text = description + "\n "
    
    # Bold text
    regex = re.compile('[A-ZÀÉÊÈ]{3,}')
    for match in regex.findall(text):
      text = text.replace(match, "<b>%s</b>" % (match[0] + match[1:].lower()))
    
    # Tables header
    ## new line then any character but new line nor *
    regex = re.compile('\n[^•^\n]+?\n•')
    for match in regex.findall(text):
      replacement = ""
      for el in match[2:-2].split(","):
        replacement += "<th>%s</th>" % el.strip()
      text = text.replace(match, "@@@<table border='1'><tr>%s</tr>###•" % replacement)
    
    # Table entries
    regex = re.compile('###•.+?\n[^•]', re.DOTALL)
    for match in regex.findall(text):
      print(match)
      print("=====")
      replacement = ""
      for row in match[3:].split("•"):
        replacement += "<tr>"
        print(row)
        for col in row.split(","):
          print(col)
          replacement += "<td>%s</td>" % col.strip()
        replacement += "</tr>"
      #text = text.replace(match, "%s</table>@@@" % replacement)
    exit(1)
    text = text.strip().replace("\n", "<br/>")
    text = text.strip().replace("@@@", "\n")
    
    return text
