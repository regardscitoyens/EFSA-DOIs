#!/bin/bash

PDF="$1"
SOURCE=$(echo "$PDF" | sed 's/\.pdf$//')
OUT=$(echo "$SOURCE" | sed -r 's|^.*/([^/]*)$|\1|')

mkdir -p data/DOIs
pdftohtml -xml "$PDF" > /dev/null
#bin/scrap.py "$SOURCE".xml > data/DOIs/"$OUT".csv
#rm -f "$SOURCE".xml
rm -f $SOURCE-*.png
