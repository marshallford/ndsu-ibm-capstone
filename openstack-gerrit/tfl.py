# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import numpy as np
import tflearn

# Load CSV file, indicate that the first column represents labels
from tflearn.data_utils import load_csv
data, labels = load_csv('changes.csv', target_column=0,
                        categorical_labels=True, n_classes=2)

dict_path = "saved_model/project.dict"


# used by inital model creation and for live predictions
def setupModel():
    # Build neural network
    net = tflearn.input_data(shape=[None, 5])
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 2, activation='softmax')
    net = tflearn.regression(net)
    # Create model
    return tflearn.DNN(net)


def convert_number(x):
    # get unique elements
    for i in x:
        x = list(set(x))
        y = []
        for i in range(len(x)):
            y.append([x[i], i])
        return y


def preprocess(changes, columns_to_delete):
    # Sort by descending id and delete columns
    for column_to_delete in sorted(columns_to_delete, reverse=True):
        [passenger.pop(column_to_delete) for passenger in changes]
    # Here we convert the project name to an int

    project_names = []
    # Load in old data
    if os.path.isfile(dict_path):
        with open(dict_path) as raw_data:
            for item in raw_data:
                if ':' in item:
                    key, value = item.split(':', 1)
                    project_names.append(key)

    # create dict
    for i in changes:
        project_names.append(i[0])

    # Deduplicate
    project_names = set(project_names)

    # Create dict
    project_dict = dict(convert_number(project_names))

    # convert with dict
    for i in changes:
        i[0] = int(project_dict[i[0]])

    with open(dict_path, 'w') as f:
        for key, value in project_dict.items():
            f.write('%s:%s\n' % (key, value))
    # data = dict()
        return np.array(changes, dtype=np.float32)


to_ignore = [0]
if __name__ == "__main__":

    # remove this to ensure that this is safe
    if os.path.isfile(dict_path):
        os.remove(dict_path)
    # Preprocess data
    data = preprocess(data, to_ignore)
    # Setup model
    model = setupModel()
    # Start training (apply gradient descent algorithm)
    model.fit(data, labels, n_epoch=10, batch_size=16, show_metric=True)

    failed = [334758, 'openstack-dev/ci-sandbox', 1, 0, 21976, 51682]
    passed = [457575, 'openstack/packstack', 60, 4, 13294, 18906]
    # Preprocess data
    failed, passed = preprocess([failed, passed], to_ignore)
    pred = model.predict([failed, passed])
    print("Failed:", pred[0][1])
    print("Passed:", pred[1][1])

    if not os.path.exists("saved_model"):
        os.makedirs("saved_model")
    model.save("saved_model/model.tfl")
