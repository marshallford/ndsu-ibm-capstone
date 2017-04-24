import json
import gerrit
from collector.main import changeValues, queryChange, textToJson

# get private ssh key
f = open('/home/marshall/.ssh/marshallford-openstack', 'r')
key = f.read()

# get gerrit stream
gerrit_stream = gerrit.GerritEvents(
  userid='marshallford',
  host='review.openstack.org',
  key=key)

# loop for gerrit events
for event in gerrit_stream.events():
    eventJson = json.loads(event)
    changeId = eventJson.get('change', {}).get('number', None)
    if changeId is None:
        continue
    change = textToJson(queryChange(changeId).text)
    values = changeValues(change)
    print(values)
