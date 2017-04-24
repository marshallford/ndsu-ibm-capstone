import json
import gerrit
from collector.main import changeValues, queryChange, textToJson
from tfl import setupModel, preprocess, to_ignore

# load model ??
model = setupModel()
model.load("saved_model/model.tfl")


# get private ssh key
f = open('/home/marshall/.ssh/marshallford-openstack', 'r')
key = f.read()

# get gerrit stream
gerrit_stream = gerrit.GerritEvents(
  userid='marshallford',
  host='review.openstack.org',
  key=key)

# loop over gerrit events
for event in gerrit_stream.events():
    eventJson = json.loads(event)
    changeId = eventJson.get('change', {}).get('number', None)
    if changeId is None:
        continue
    change = textToJson(queryChange(changeId).text)
    values = changeValues(change)
    # this shouldn't work, we aren't converting project string to id yet
    test = preprocess([values[1:]], to_ignore)
    pred = model.predict(test)
    print("### EVENT ###")
    print("Values: ", values[1:])
    print("Test: ", pred[0][1])
    if values[0] != 'None':
        print("Actual score: ", values[0])
