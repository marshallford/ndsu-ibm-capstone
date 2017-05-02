import json
import sys
import gerrit
import object_storage_tensorflow as obj_tf
from collector.main import changeValues, GerritSession
from generate_model import setupModel, getConfig, preprocess, to_ignore

config = getConfig()

# load model
model = setupModel()
print('downloading model from object storage (S3)...')
path, _ = obj_tf.s3.downloadFolder(config['bucket'], config['remote_folder'])
model.load("{}/model.tfl".format(path))


# get private ssh key
if 'openstack_ssh_key' not in config:
    config['openstack_ssh_key'] = input("Path to openstack private key: ")
key = open(config['openstack_ssh_key'], 'r').read()

# get gerrit stream
gerrit_stream = gerrit.GerritEvents(
  userid=config['userid'],
  host='review.openstack.org',
  key=key)

gerrit_requester = GerritSession()


# loop over gerrit events
def monitorGerrit():
    print('monitoring gerrit events...')
    for event in gerrit_stream.events():
        eventJson = json.loads(event)
        changeId = eventJson.get('change', {}).get('number', None)
        if changeId is None:
            continue
        change = gerrit_requester.query_change(changeId)
        values = changeValues(change)
        test, _ = preprocess([values[1:]], to_ignore, True)
        print("### EVENT ###")
        print("Values: ", values[1:])
        if test[0] is '-1':
            print("Test: not run, project name not included in model")
        else:
            pred = model.predict(test)
            print("Test: ", pred[0][1])
            if values[0] != 'None':
                print("Actual score: ", values[0])


if __name__ == "__main__":
    try:
        monitorGerrit()
    except KeyboardInterrupt:
        print("connection closed.")
        sys.exit(0)
