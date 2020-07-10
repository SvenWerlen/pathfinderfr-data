#!/bin/bash
rm -f /tmp/out.txt
for file in $( eval find ../data -name "*.yml" )
do
  printf "%-40s: %4d\n" "$file" "$(grep "Nom:" $file | wc -l)" >> /tmp/out.txt
done
cat /tmp/out.txt | sort | grep -v "versions"
