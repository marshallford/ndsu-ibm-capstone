import requests
import json
from pathlib import Path
import os
from functools import reduce

import tensorflow as tf


attrs = {
    'changeID': '_number',
    'project': 'project',
    'insertions': 'insertions',
    'deletions': 'deletions',
    'accountID': 'owner._account_id',
    'verified': 'labels.Verified.value'
}
filename = 'changes.csv'
numberToIncrement = 500
stopAtByteSize = 100000  # 1000000  # 1MB


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
            f.write(line[:-1] + "\n")


n = 0
while sizeOfCSV() < stopAtByteSize:
    j = textToJson(queryChanges(n).text)
    writeChanges(j)
    n += numberToIncrement

filename_queue = tf.train.string_input_producer(["changes.csv"])

reader = tf.TextLineReader()
key, value = reader.read(filename_queue)

# Default values, in case of empty columns. Also specifies the type of the
# decoded result.
record_defaults = [[""], [""], [""], [""], [""], [""]]
deletions, insertions, changeid, project, verified, accountid = tf.decode_csv(
    value, record_defaults=record_defaults)
# Stacking columns together (test)
features = tf.stack([deletions, insertions, verified])

with tf.Session() as sess:
    # Start populating the filename queue.
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    for i in range(1200):
        # Retrieve a single instance:
        example, label = sess.run([features, project])
        print (example, label)

    coord.request_stop()
    coord.join(threads)
