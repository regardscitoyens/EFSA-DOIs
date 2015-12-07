#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re, json

experts = []
for path, _, filenames in os.walk(os.path.join("data", "DOIs")):
    for f in filenames:
        if not f.endswith(".json"):
            continue
        with open(os.path.join(path, f)) as jsonfile:
            experts.append(json.load(jsonfile))
            experts[-1]["Full name"] = "%s, %s" % (experts[-1]["Family name"], experts[-1]["First name"])
            experts[-1]["DOI date"] = experts[-1]["Date"]
            experts[-1]["PDF"] = f.replace(".json", ".pdf")
            experts[-1]["Subject group"] = f[:f.find("_")]

def format_for_csv(val):
    if not val:
        return ""
    elif "," in val:
        val = '"%s"' % val.replace('"', '""')
    return val.encode("utf-8")

def write_csv(f, data, headers):
    print >> f, ",".join(map(format_for_csv, headers))
    for row in data:
        print >> f, ",".join(map(format_for_csv, [row[h] for h in headers]))

headers = ['Subject group', 'Full name', 'Family name', 'First name', 'Title', 'DOI date', 'Profession', 'Current EFSA involvements', 'PDF']
with open(os.path.join("data", "EFSA_experts_metas.csv"), "w") as f:
    write_csv(f, sorted(experts, key=lambda x: "%s - %s" % (x["Subject group"], x["Full name"])), headers)

activities = []
activities_by_group = {}
activities_by_nature = {}
headers = ['Subject group', 'Full name', 'DOI date', 'PDF']
for expert in experts:
    for act in expert["activities"]:
        activity = {
            "Nature of activity": act[0],
            "Organisation": act[1],
            "Subject matter": act[2],
            "Start date": act[3],
            "End date": act[4],
            "Activity of a close family member": act[5]
        }
        for h in headers:
            activity[h] = expert[h]
        activities.append(activity)
        if activity["Subject group"] not in activities_by_group:
            activities_by_group[activity["Subject group"]] = []
        activities_by_group[activity["Subject group"]].append(activity)
        if activity["Nature of activity"] not in activities_by_nature:
            activities_by_nature[activity["Nature of activity"]] = []
        activities_by_nature[activity["Nature of activity"]].append(activity)

headers = ['Subject group', 'Full name', 'Nature of activity', 'Activity of a close family member', 'Organisation', 'Subject matter', 'Start date', 'End date', 'DOI date', 'PDF']
with open(os.path.join("data", "EFSA_experts_activities.csv"), "w") as f:
    write_csv(f, sorted(activities, key=lambda x: "%s - %s - %s - %s" % (x["Subject group"], x["Full name"], x["Nature of activity"], x["Start date"])), headers)

headers_group = headers[1:]
for group in activities_by_group:
    with open(os.path.join("data", "EFSA_experts_group-%s_activities.csv" % group), "w") as f:
        write_csv(f, sorted(activities_by_group[group], key=lambda x: "%s - %s - %s" % (x["Full name"], x["Nature of activity"], x["Start date"])), headers_group)

headers_nature = headers[0:2] + headers[3:]
for nature in activities_by_nature:
    with open(os.path.join("data", "EFSA_experts_activities_cat-%s.csv" % nature[:nature.find(".")]), "w") as f:
        write_csv(f, sorted(activities_by_nature[nature], key=lambda x: "%s - %s - %s" % (x["Subject group"], x["Full name"], x["Start date"])), headers_group)
