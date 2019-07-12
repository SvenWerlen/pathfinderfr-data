#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# cette fonction permet de convertir un tableau en texte
#
def table2text(table):
    text = ""
    for tr in table:
        for td in tr:
            text += td.text.strip() + ", "
        text = text[:-1] + "\n"
    return text


def html2text(htmlEl):
    if htmlEl.name is None or htmlEl.name == 'a':
        return htmlEl.string
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
    else:
        return ""
    
#
# cette fonction extait une propriété (format BD)
#
def extractBD(html):
    titreEl = html.find('div',{'class':['BDtitre']})
    titre = titreEl.text.strip()
    
    descr = ""
    # lire la partie descriptive
    for el in titreEl.next_siblings:
        descr += html2text(el)
    
    return {'nom': titre, 'descr': descr.strip()}
