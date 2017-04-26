#!/usr/bin/env python

from __future__ import print_function

import csv
from dateutil.parser import parse
from functools import reduce
import json
import logging
import os
from pathlib import Path

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
numberToIncrement = 500
stopAtByteSize = 1000000  # 1000000  # 1MB
baseUrl = 'https://review.openstack.org'
changeUrlParams = 'o=CURRENT_REVISION&o=CURRENT_COMMIT&o=CURRENT_FILES&o=DETAILED_ACCOUNTS&o=LABELS' # NOQA


class GerritSession(requests.Session):

    # return Response object of single change
    def query_change(self, change_id):
        url = "{}/changes/{}?{}"
        resp = self.get(url.format(baseUrl, change_id, changeUrlParams))
        return self._strip_gerrit_weirdness(resp)

    def _strip_gerrit_weirdness(self, response):
        xssi_crap, jsonable = response.text.split('\n', 1)
        return json.loads(jsonable)

    def query_changes(self, query, start):
        """Return a list of changes from a given query from offset 'start'"""

        url = "{}/changes/?q={}&{}&start={}" # NOQA
        resp = self.get(url.format(baseUrl, query, changeUrlParams, str(start))) # NOQA
        return self._strip_gerrit_weirdness(resp)

    def get_changes(self, query):
        """
        Return a generator that can be used to
        iterate though all changes from a query.
        """
        start = 0
        while sizeOfCSV() < stopAtByteSize:
            changes = self.query_changes(query, start)
            LOG.debug("Got {0} changes to process".format(len(changes)))
            if not changes:
                print("Out of changes...")
                break

            for change in changes:
                yield change

            start += numberToIncrement


# return size of csv in bytes
def sizeOfCSV():
    try:
        return int(os.stat(filename).st_size)
    except:
        return 0


# remove duplicates and changes with a 'None' value for 'verified'
def deduplicateCSV():
    newCSV = list()
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
    values = list()
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
    # status:open label:Verified reviewer:"Jenkins <jenkins@openstack.org>"
    query = 'status%3Aopen%20label%3AVerified%20reviewer%3A%22Jenkins%20%3Cjenkins%40openstack.org%3E%22' # NOQA

    gerrit = GerritSession()

    writeChanges(gerrit.get_changes(query))
    deduplicateCSV()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
