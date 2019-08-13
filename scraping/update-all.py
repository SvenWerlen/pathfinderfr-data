#!/bin/bash

echo "#####################"
echo "       EQUIPMENT"
echo "#####################"

./extract-weapons.py
./extract-armors.py

echo "#####################"
echo "       TRAITS"
echo "#####################"

./extract-races-traits-alternatifs.py
./extract-traits.py

