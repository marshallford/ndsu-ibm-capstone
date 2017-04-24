import json
import gerrit
import tflearn
from collector.main import changeValues, queryChange, textToJson
from tfl import preprocess, to_ignore

# load model ???
net = tflearn.input_data(shape=[None, 5])
net = tflearn.fully_connected(net, 32)
net = tflearn.fully_connected(net, 32)
net = tflearn.fully_connected(net, 2, activation='softmax')
net = tflearn.regression(net)
# define model
model = tflearn.DNN(net)
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
    if values[0] is not None:
        print("Actual score: ", values[0])
