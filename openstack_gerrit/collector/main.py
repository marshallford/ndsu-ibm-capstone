import csv
from dateutil.parser import parse
from functools import reduce
import json
import logging
import os
from pathlib import Path
import urllib.parse
import requests

LOG = logging.getLogger(__name__)


# attr function
# given a change dict, returns 0 or 1 for Jenkins pass/fail
def verified(change):
    value = change.get('labels', {}).get('Verified', {}).get('value')
    if value is None:
        return None
    elif value <= 0:
        return 0
    else:
        return 1


# attr function
# given a change dict, return delta in seconds between created and updated time
def created_updated_delta(change):
    created = parse(change['created'])
    updated = parse(change['updated'])
    return int((updated - created).total_seconds())


# constants
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

changeUrlParams = 'o=CURRENT_REVISION&o=CURRENT_COMMIT&o=CURRENT_FILES&o=DETAILED_ACCOUNTS&o=LABELS' # NOQA

KB = 1024 * 1
MB = 1024 * KB
GB = 1024 * MB
stopAtSize = 1 * MB


class GerritSession(requests.Session):

    base_url = 'https://review.openstack.org'

    def query_change(self, change_id):
        """Return a dict representing a single change."""
        url = "{}/changes/{}?{}"
        resp = self.get(url.format(self.base_url, change_id, changeUrlParams))
        return self._strip_gerrit_weirdness(resp)

    def _strip_gerrit_weirdness(self, response):
        xssi_crap, jsonable = response.text.split('\n', 1)
        return json.loads(jsonable)

    def query_changes(self, query, start):
        """Return a list of changes from a given query from offset 'start'"""
        query = urllib.parse.quote(query)

        url = "{}/changes/?q={}&{}&start={}"
        resp = self.get(url.format(self.base_url, query, changeUrlParams, str(start))) # NOQA
        return self._strip_gerrit_weirdness(resp)

    def get_changes(self, query, chunk_size=500):
        """
        Return a generator that can be used to
        iterate though all changes from a query.
        """
        start = 0
        while sizeOfCSV() < stopAtSize:
            changes = self.query_changes(query, start)
            LOG.debug("got {0} changes to process".format(len(changes)))
            if not changes:
                LOG.info("out of changes that match query.")
                break

            for change in changes:
                yield change

            start += chunk_size


# return size of csv in bytes
def sizeOfCSV():
    try:
        return int(os.stat(filename).st_size)
    except:
        return 0


# remove duplicates and changes with a 'None' value for 'verified'
def deduplicateCSV():
    newCSV = []
    seenKeys = set()
    f = open(filename, "r")
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        if row[0] == 'None' or row[1] in seenKeys:
            continue
        seenKeys.add(row[1])
        newCSV.append(','.join(row))
    f = open(filename, "w+")
    for i in newCSV:
        f.write(i + '\n')


# return an array of the change's values
def changeValues(change):
    values = []
    for attr in map(lambda x: x['value'], attrs):
        if callable(attr):
            values.append(str(attr(change)))
        else:
            values.append(str(reduce(dict.get, attr.split("."), change)))
    return values


# write a list of changes to the csv
def writeChanges(changes):
    needs_headers = False
    if not Path(filename).is_file():
        needs_headers = True

    with open(filename, 'a+') as f:
        if needs_headers:
            f.write(','.join(map(lambda x: x['label'], attrs)) + '\n')
        for change in changes:
            f.write(','.join(changeValues(change)) + "\n")


def main():
    query = ('status:open '
             'label:Verified '
             'reviewer:"Jenkins <jenkins@openstack.org>"')

    gerrit = GerritSession()
    print('generating csv...')
    writeChanges(gerrit.get_changes(query))
    print('deduplicating csv...')
    deduplicateCSV()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    main()
