import json
import gerrit
import yaml
import os
from collector.main import changeValues, GerritSession
from generate_model import setupModel, preprocess, to_ignore

# load model
model = setupModel()
model.load("saved_model/model.tfl")


# get private ssh key
configFile = 'config.yaml'
config = {}
if os.path.exists(configFile):
    with open(configFile, 'r') as f:
        config = yaml.load(f)
else:
    config['openstack_ssh_key'] = input("Path to openstack private key: ")
key = open(config['openstack_ssh_key'], 'r').read()

# get gerrit stream
gerrit_stream = gerrit.GerritEvents(
  userid='marshallford',
  host='review.openstack.org',
  key=key)

gerrit_requester = GerritSession()
# loop over gerrit events
for event in gerrit_stream.events():
    eventJson = json.loads(event)
    changeId = eventJson.get('change', {}).get('number', None)
    if changeId is None:
        continue
    change = gerrit_requester.query_change(changeId)
    values = changeValues(change)
    test = preprocess([values[1:]], to_ignore)
    pred = model.predict(test)
    print("### EVENT ###")
    print("Values: ", values[1:])
    print("Test: ", pred[0][1])
    if values[0] != 'None':
        print("Actual score: ", values[0])
