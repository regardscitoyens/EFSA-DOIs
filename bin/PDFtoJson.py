#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, json

filepath = sys.argv[1]
with open(filepath, 'r') as xml_file:
    xml = xml_file.read()

appendText = lambda text, app: "%s %s" % (text.rstrip(), app.lstrip()) if text else app.strip()
def appendValToField(dico, key, value):
    if key in dico:
        dico[key] = appendText(dico[key], value)
    else:
        dico[key] = value

re_clean_bal = re.compile(r'<[^>]+>')
re_clean_spaces = re.compile(r'\s+')
clean = lambda x: re_clean_spaces.sub(' ', re_clean_bal.sub('', x)).strip()

re_line = re.compile(r'<page number|text top="(\d+)" left="(\d+)"[^>]*font="(\d+)">(.*)</text>', re.I)
re_skip = re.compile(r'<b>(I hereby declare that I|and that the above Dec|SIGNED).*</b>')
re_extract_field = re.compile(r'^\s*<b>\s*([^<:]+)[:\s]*</b>\s*(.*)$')
re_extract_date = re.compile(r'^\s*<b>Date:\s*(\d+)/(\d+)/(\d+)\s*Signature.*$')
re_extract_startend = re.compile(r'^(\d+)/(\d+) - (now|(\d+)/(\d+))$')


mint = 370
maxt = 830
l1 = 57
l2 = 352
l3 = 548
l4 = 744
page = 0
readTable = False
readRecords = False
field = None

record = {"activities": []}
activity = ["", "", "", "", "", ""]
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
    val = clean(text)
    if not val:
        continue
    if page == 1 and not readTable:
        if top < mint:
            continue
        if text.startswith("<b>"):
            field, val = map(clean, re_extract_field.search(text).groups())
            if field == "Name":
                record["Family name"], record["First name"] = val.split(', ')
            elif field.startswith("Nature"):
                readTable = True
            else:
                appendValToField(record, field, val)
        elif field:
            appendValToField(record, field, val)
        continue
    if text.startswith('<b>Date:'):
        record['Date'] = clean(re_extract_date.sub(r'\3-\2-\1', text))
        continue
    if re_skip.match(text):
        continue
    readRecords |= text.startswith('<b>Subject ')
    if not readRecords or text.startswith('<b>Subject '):
        continue
    if left == l1:
        if "(Close family" in val:
            record["activities"].append(list(activity))
            activity = [activity[0], "", "", "", "", "X"]
            continue
        elif activity[2]:
            record["activities"].append(list(activity))
            activity = [val, "", "", "", "", ""]
            continue
        activity[0] = appendText(activity[0], val)
    elif left == l2:
        match = re_extract_startend.search(val).groups()
        start = "%s-%s" % (match[1], match[0])
        end = match[2] if not match[3] else "%s-%s" % (match[4], match[3])
        if activity[2]:
            record["activities"].append(list(activity))
            activity = [activity[0], "", "", start, end, activity[5]]
            continue
        activity[3] = start
        activity[4] = end
    elif left == l3:
        if val.startswith('-Name: '):
            val = val.replace('-Name: ', '')
        if activity[2]:
            record["activities"].append(list(activity))
            activity = [activity[0], val, "", activity[3], activity[4], activity[5]]
            continue
        if val == "German Endocrine Society Member":
            activity[1] = "German Endocrine Society"
            activity[2] = "Member"
        elif val == "British Toxicology Society scientific society":
            activity[1] = "British Toxicology Society"
            activity[2] = "scientific society"
        else:
            activity[1] = appendText(activity[1], val)
    elif left == l4:
        activity[2] = appendText(activity[2], val)
    else:
        print >> sys.stderr, "WARNING, line at X %s not caught:" % left, text
if activity[2]:
    record["activities"].append(activity)

print json.dumps(record, encoding='utf-8', indent=2)
