import requests
import json
from pathlib import Path
from functools import reduce


def queryChanges(start):
    url = "https://review.openstack.org/changes/?q=status:closed&o=CURRENT_REVISION&o=CURRENT_COMMIT&o=CURRENT_FILES&o=DETAILED_ACCOUNTS&start={}"
    return requests.get(url.format(str(start)))


def textToJson(text):
    return json.loads(text[4:])


attrs = [
    '_number',
    'project',
    'insertions',
    'deletions',
    'owner._account_id'
]
filename = 'changes.csv'

j = textToJson(queryChanges(0).text)

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