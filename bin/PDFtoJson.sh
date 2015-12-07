#!/bin/bash

cd $(dirname $0)/..

PDF="$1"
SOURCE=$(echo "$PDF" | sed 's/\.pdf$//')
OUT=$(echo "$SOURCE" | sed -r 's|^.*/([^/]*)$|\1|')

mkdir -p data/DOIs
pdftohtml -xml "$PDF" > /dev/null
bin/PDFtoJson.py "$SOURCE".xml > data/DOIs/"$OUT".json
rm -f "$SOURCE".xml
rm -f $SOURCE-*.png

