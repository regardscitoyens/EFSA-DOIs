#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re

filepath = sys.argv[1]
with open(filepath, 'r') as xml_file:
    xml = xml_file.read()

def appendValToField(dico, key, value):
    if key in dico:
        dico[key] = "%s %s" % (dico[key].rstrip(), value.lstrip())
    else:
        dico[key] = value

re_clean_bal = re.compile(r'<[^>]+>')
re_clean_spaces = re.compile(r'\s+')
clean = lambda x: re_clean_spaces.sub(' ', re_clean_bal.sub('', x)).strip()

re_line = re.compile(r'<page number|text top="(\d+)" left="(\d+)"[^>]*font="(\d+)">(.*)</text>', re.I)
re_extract_field = re.compile(r'^\s*<b>\s*([^<:]+)[:\s]*</b>\s*(.*)$')
re_extract_date = re.compile(r'^\s*<b>Date:\s*(\d+)/(\d+)/(\d+)\s*Signature.*$')


mint = 370
maxt = 830
page = 0
readTable = False
field = None
headers = ['Family name', 'First name', 'Title', 'Date', 'Profession', 'Current EFSA involvements', '']

record = {}
for line in (xml).split("\n"):
    if line.startswith('<page'):
        page += 1
    if not line.startswith('<text'):
        continue
    attrs = re_line.search(line)
    if not attrs or not attrs.groups():
        raise Exception("WARNING : text line detected with wrong format %s" % line)
    font = int(attrs.group(3))
    top = int(attrs.group(1))
    left = int(attrs.group(2))
    text = attrs.group(4).replace("&amp;", "&").replace('&#34;', '"')
    if top > maxt:
        continue
    #print "DEBUG %s %s %s %s" % (font, left, top, text)
    if page == 1 and not readTable:
        if top < mint:
            continue
        val = clean(text)
        if not val:
            continue
        if text.lstrip().startswith("<b>"):
            field, val = map(clean, re_extract_field.search(text).groups())
            if field == "Name":
                record["Family name"], record["First name"] = val.split(', ')
            elif field.startswith("Nature"):
                readTable = True
            else:
                appendValToField(record, field, val)
        elif field:
            appendValToField(record, field, val)
        if not readTable:
            continue
    elif text.lstrip().startswith('<b>Date:'):
        record['Date'] = clean(re_extract_date.sub(r'\3-\2-\1', text))

print ",".join(['"%s"' % h for h in headers])
print ",".join([('"%s"' % record[h].replace('"', '""')).encode('utf-8') if h in record else "" for h in headers])

