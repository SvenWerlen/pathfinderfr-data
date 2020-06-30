# Pathfinder-fr Data (Foundry VTT)

Cette section contient les scripts permettant de produire les fichiers JSON qui pourront être importés
dans Foundry VTT afin de générer des compendiums.

## Vue d'ensemble

Cette documentation présente comment mettre en place un environnement de développement afin de tester des mises à jour
de données en les important dans [FoundryVTT](https://foundryvtt.com/). 

Le processus, une fois l'environnement en place, est:
1. Effectuer des modifications dans les données 
1. Exécuter le(s) script(s) afin d'extraire les données et produire des fichiers au format JSON qui pourront être importés dans Foundry
1. Exécuter une fonction du module `pf1-fr` dans Foundry pour générer le(s) compendium(s)

## Pré-requis

* Les données requises sont déjà disponibles dans le dépôt mais peuvent être mises à jour au besoin (voir ci-bas)
* Une installation locale de [FoundryVTT](https://foundryvtt.com/) est recommandée pour ne pas avoir à téléverser les fichiers à chaque nouvelle mise à jour à tester.
* Foundry doit pouvoir accéder aux données du répertoire [`foundryvtt/data`](data)
  * Si votre environnement est Linux (ou MacOS), il suffit de créer un lien symbolique et de le placer dans le répertoire `[FVTT_HOME]/resources/app/public/`. Exemple: `ln -s [GIT]/foundryvtt/data [FVTT_HOME]/resources/app/public/`
  * Si votre environnement est Windows, le plus simple est de déplacer le projet GIT dans le répertoire `[FVTT_HOME]/resources/app/public/`.
  * Avec Windows 10, il est possible d'utiliser [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10) afin d'avoir une expérience de travail conviviale pour l'exécution des scripts
* Vous pouvez tester que les données sont bien accessibles en ouvrant votre navigateur à l'adresse correspondant au répertoire. Pour une installation par défaut et l'utilisation d'un lien symobolique comme présenté ci-dessus, l'adresse serait:
```
http://localhost:30000/data/classes.json
```
  
## Générer les compendiums 

1. Démarrer FoundryVTT
1. Démarrer un monde basé sur le système [Pathfinder 1](https://foundryvtt.com/packages/pf1/) avec le module [Improvements for French](https://foundryvtt.com/packages/pf1-fr/) activé
1. Ouvrir la console (F12)
1. Exécuter la fonction `pf1frLoadData` avec les paramètres
  * `path`: chemin pour accéder au répertoire des données (où se trouvent les fichiers JSON)
  * `liste`: liste des compendiums à importer (tous par défaut)
1. Un message informatif affichera a progression et les compendiums générés seront préfixés de `Imported`

Exemple 1: importer les dons et les modifs pour les dons, en assumant que le répertoire data est accessible à la racine du serveur `/data`
```javascript
pf1frLoadData("/data", ["feats", "featsBuffs"])
```

Exemple 2: importer toutes les données (classes, feats, featsBuffs, classfeatures, spells, weapons, armors, magic, equipment, beastiary)
```javascript
pf1frLoadData("/data")
```

## Supprimer les compendiums générés (nettoyage)

La fonction `pf1frLoadData` peut être exécutée avec un 3ième paramètre à `true` pour supprimer tous les compendiums générés:
```javascript
pf1frLoadData("/data", [], true)
```

## Intégrer les compendiums

Pour intégrer les compendiums dans le module officiel ([Improvements for French](https://foundryvtt.com/packages/pf1-fr/)), veuillez contribuer
sur les sources de données ([www.pathfinder-fr.org](https://www.pathfinder-fr.org), chiffrier [Foundry PF1 buffs](https://docs.google.com/spreadsheets/d/1oD38PDiGVGF3BgQ_6souC3_KM1hq5v-hgOqGNrNA16I)) 
puis me contacter sur Discord (Dorgendubal#3348). J'exécuterai alors les scripts nécessaires pour intégrer les nouvelles données, après avoir effectués quelques validations.

## Mettre à jour les données

Les scripts s'appuient sur les données suivantes:
* [Les données](../data) extraites du site https://pathfinder-fr.org
* [Le fichier CSV](data/buffs-feats.csv) généré à partir du chiffrier (Spreadsheet) [Foundry PF1 buffs](https://docs.google.com/spreadsheets/d/1oD38PDiGVGF3BgQ_6souC3_KM1hq5v-hgOqGNrNA16I)

Pour mettre [les données](../data) de Pathfinder FR à jour, il est nécessaire d'exécuter les scripts situés dans le répertoire [`/scraping/`](../scraping/).
Le processus complet `update-all.sh` prend plusieurs heures et pourrait échouer en raison de sa fragilité. Veuillez me contacter si vous désirez mettre
les données à jour et que vous éprouvez des difficultés.

Pour mettre à jour [Le fichier CSV](data/buffs-feats.csv) des buffs, exécuter simplement le script [`downloadFeatsBuffs.sh`](downloadFeatsBuffs.sh) qui se chargera de télécharger le tout en quelques secondes.



