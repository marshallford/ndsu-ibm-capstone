import requests
import json
from pathlib import Path
import os
from functools import reduce

attrs = [
    '_number',
    'project',
    'insertions',
    'deletions',
    'owner._account_id'
]
filename = 'changes.csv'
numberToIncrement = 500
stopAtByteSize = 1000000  # 1MB


def queryChanges(start):
    url = "https://review.openstack.org/changes/?q=status:closed&o=CURRENT_REVISION&o=CURRENT_COMMIT&o=CURRENT_FILES&o=DETAILED_ACCOUNTS&start={}" # NOQA
    return requests.get(url.format(str(start)))


def textToJson(text):
    return json.loads(text[4:])


def sizeOfCSV():
    try:
        return int(os.stat(filename).st_size)
    except:
        return 0


def writeChanges(changes):
    headers = False
    if not Path(filename).is_file():
        headers = True
    with open(filename, 'a+') as f:
        if headers:
            f.write(', '.join(attrs) + '\n')
        for change in j:
            line = ""
            for attr in attrs:
                line += str(reduce(dict.get, attr.split("."), change)) + ","
            f.write(line + "\n")


n = 0
while sizeOfCSV() < stopAtByteSize:
    j = textToJson(queryChanges(n).text)
    writeChanges(j)
    n += numberToIncrement
