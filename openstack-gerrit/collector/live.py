import json
import pprint
import gerrit

f = open("/home/marshall/.ssh/marshallford-openstack", "r")
key = f.read()

gerrit_stream = gerrit.GerritEvents(
  userid='marshallford',
  host='review.openstack.org',
  key=key)

for event in gerrit_stream.events():
    pprint.pprint(json.loads(event))
