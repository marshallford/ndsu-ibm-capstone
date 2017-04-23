import requests
import json
from pathlib import Path
import os
from functools import reduce
import csv
from dateutil.parser import parse


def verified(change):
    value = change.get('labels', {}).get('Verified', {}).get('value')
    if value is None:
        return None
    elif value <= 0:
        return 0
    else:
        return 1


def created_updated_delta(change):
    created = parse(change['created'])
    updated = parse(change['updated'])
    return int((updated - created).total_seconds())


attrs = list([
    {'label': 'verified', 'value': verified},
    {'label': 'changeID', 'value': '_number'},
    {'label': 'project', 'value': 'project'},
    {'label': 'insertions', 'value': 'insertions'},
    {'label': 'deletions', 'value': 'deletions'},
    {'label': 'accountID', 'value': 'owner._account_id'},
    {'label': 'created_updated_delta', 'value': created_updated_delta},
])
filename = 'changes.csv'
numberToIncrement = 500
stopAtByteSize = 1000000  # 1000000  # 1MB


def queryChanges(start):
    # status:open label:Verified reviewer:"Jenkins <jenkins@openstack.org>"
    query = 'status%3Aopen%20label%3AVerified%20reviewer%3A%22Jenkins%20%3Cjenkins%40openstack.org%3E%22' # NOQA
    url = "https://review.openstack.org/changes/?q={}&o=CURRENT_REVISION&o=CURRENT_COMMIT&o=CURRENT_FILES&o=DETAILED_ACCOUNTS&o=LABELS&start={}" # NOQA
    return requests.get(url.format(query, str(start)))


def textToJson(text):
    return json.loads(text[4:])


def sizeOfCSV():
    try:
        return int(os.stat(filename).st_size)
    except:
        return 0


def deduplicateCSV():
    newCSV = list()
    f = open(filename, "r")
    reader = csv.reader(f, delimiter=',')
    seenKeys = set()
    for row in reader:
        if row[0] == 'None' or row[1] in seenKeys:
            continue
        seenKeys.add(row[0])
        newCSV.append(','.join(row))
    f = open(filename, "w+")
    for i in newCSV:
        f.write(i + '\n')


def writeChanges(changes):
    headers = False
    if not Path(filename).is_file():
        headers = True
    with open(filename, 'a+') as f:
        if headers:
            f.write(','.join(map(lambda x: x['label'], attrs)) + '\n')
        for change in j:
            line = ""
            for attr in map(lambda x: x['value'], attrs):
                if callable(attr):
                    line += str(attr(change))
                else:
                    line += str(reduce(dict.get, attr.split("."), change))
                line += ","
            f.write(line[:-1] + "\n")


n = 0
while sizeOfCSV() < stopAtByteSize:
    j = textToJson(queryChanges(n).text)
    if (len(j) < 1):
        print("Out of changes...")
        break
    writeChanges(j)
    n += numberToIncrement
deduplicateCSV()
