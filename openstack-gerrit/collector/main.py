import requests
import json
from pathlib import Path
import os
from functools import reduce


def jenkinFunc(change):
    # access to messages
    # change["messages"]
    return "foo"


attrs = {
    'changeID': '_number',
    'project': 'project',
    'insertions': 'insertions',
    'deletions': 'deletions',
    'accountID': 'owner._account_id',
    'jenkins': jenkinFunc
}
filename = 'changes.csv'
numberToIncrement = 500
stopAtByteSize = 10000  # 1000000  # 1MB


def queryChanges(start):
    url = "https://review.openstack.org/changes/?q=status:closed&o=CURRENT_REVISION&o=CURRENT_COMMIT&o=CURRENT_FILES&o=DETAILED_ACCOUNTS&o=MESSAGES&start={}" # NOQA
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
            f.write(', '.join(list(attrs.keys())) + '\n')
        for change in j:
            line = ""
            for _, attr in attrs.items():
                if callable(attr):
                    line += str(attr(change))
                else:
                    line += str(reduce(dict.get, attr.split("."), change))
                line += ","
            f.write(line + "\n")


n = 0
while sizeOfCSV() < stopAtByteSize:
    j = textToJson(queryChanges(n).text)
    writeChanges(j)
    n += numberToIncrement
