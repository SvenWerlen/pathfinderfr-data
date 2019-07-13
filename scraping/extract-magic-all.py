#!/bin/bash

printf "###\n### Armures et boucliers\n###\n\n" > ../data/magic.yml
echo "Processing armures et boucliers..."
./extract-magic-armors.py >> ../data/magic.yml

printf "###\n### Armes\n###\n\n" >> ../data/magic.yml
echo "Processing armes..."
./extract-magic-weapons.py >> ../data/magic.yml

printf "###\n### Anneaux\n###\n\n" >> ../data/magic.yml
echo "Processing anneaux..."
./extract-magic-rings.py >> ../data/magic.yml
