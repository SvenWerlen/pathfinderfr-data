#!/bin/bash

echo "#####################"
echo "       BASE"
echo "#####################"

./extract-feats.py

echo "#####################"
echo "       EQUIPMENT"
echo "#####################"

./extract-weapons.py
./extract-armors.py
./extract-equipment.py

echo "#####################"
echo "       TRAITS"
echo "#####################"

./extract-races-traits-alternatifs.py
./extract-traits.py

