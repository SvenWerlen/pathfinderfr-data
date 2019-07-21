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

printf "###\n### Sceptres\n###\n\n" >> ../data/magic.yml
echo "Processing sceptres..."
./extract-magic-scepters.py >> ../data/magic.yml

printf "###\n### Bâtons\n###\n\n" >> ../data/magic.yml
echo "Processing bâtons..."
./extract-magic-staffs.py >> ../data/magic.yml

printf "###\n### Objets merveilleux\n###\n\n" >> ../data/magic.yml
echo "Processing objets merveilleux..."
./extract-magic-objects.py >> ../data/magic.yml
