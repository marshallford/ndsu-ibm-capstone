import json
import gerrit
from collector.main import changeToLine, queryChange, textToJson

f = open("/home/marshall/.ssh/marshallford-openstack", "r")
key = f.read()

gerrit_stream = gerrit.GerritEvents(
  userid='marshallford',
  host='review.openstack.org',
  key=key)

for event in gerrit_stream.events():
    eventJson = json.loads(event)
    changeId = eventJson.get('change', {}).get('number', None)
    if changeId is None:
        continue
    change = textToJson(queryChange(changeId).text)
    values = changeToLine(change).split(',')
    print(change)
    print(values)
