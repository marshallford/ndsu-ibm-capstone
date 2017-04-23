# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import numpy as np
import tflearn

# Load CSV file, indicate that the first column represents labels
from tflearn.data_utils import load_csv
data, labels = load_csv('changes.csv', target_column=0,
                        categorical_labels=True, n_classes=2)


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
    for i in changes:
        project_names.append(i[1])
    project_dict = dict(convert_number(project_names))
    for i in changes:
        i[1] = project_dict[i[1]]

    # for i in range(len(changes)):
        # Converting 'sex' field to float (id is 1 after removing labels column) # noqa
        # changes[i][1] = 1. if changes[i][1] == 'female' else 0.
    return np.array(changes, dtype=np.float32)


# Preprocess data
data = preprocess(data, [2])

# Build neural network
net = tflearn.input_data(shape=[None, 4])
net = tflearn.fully_connected(net, 32)
net = tflearn.fully_connected(net, 32)
net = tflearn.fully_connected(net, 2, activation='softmax')
net = tflearn.regression(net)

# Define model
model = tflearn.DNN(net)
# Start training (apply gradient descent algorithm)
model.fit(data, labels, n_epoch=10, batch_size=16, show_metric=True)

failed = ['334758', 'openstack-dev/ci-sandbox', '1', '0', '21976']
passed = ['457575', 'openstack/packstack', '60', '4', '13294']
# Preprocess data
failed, passed = preprocess([failed, passed], [2])
pred = model.predict([failed, passed])
# print("Failed:", pred[0][1])
# print("Passed:", pred[1][1])

if not os.path.exists("saved_model"):
    os.makedirs("saved_model")
model.save("saved_model/model.tfl")
