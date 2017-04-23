import json
import pprint
import gerrit
from main import verified

f = open("/home/marshall/.ssh/marshallford-openstack", "r")
key = f.read()

gerrit_stream = gerrit.GerritEvents(
  userid='marshallford',
  host='review.openstack.org',
  key=key)

for event in gerrit_stream.events():
    json = json.loads(event)
    pprint.pprint(json)
    print("verified: " + str(verified(json)))
