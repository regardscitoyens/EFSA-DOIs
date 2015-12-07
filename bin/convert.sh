#!/bin/bash

cd $(dirname $0)/..

find PDFs/ -name "*.pdf" | while read pdf; do
  bin/PDFtoJson.sh "$pdf"
done

bin/JsonsToCSVs.py
