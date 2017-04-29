# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import numpy as np
import tflearn
from tflearn.data_utils import load_csv
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Load CSV file, indicate that the first column represents labels
data, labels = load_csv('changes.csv', target_column=0,
                        categorical_labels=True, n_classes=2)

project_name_mapping_path = "saved_model/project_name_mapping.npy"


# used by inital model creation and for live predictions
def setupModel():
    # Build neural network
    net = tflearn.input_data(shape=[None, 4])
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
    # Load in old data
    project_names = []
    if os.path.isfile(project_name_mapping_path):
        old_projects = np.load(project_name_mapping_path).item()
        project_names = list(old_projects.keys())
    else:
        exit('project mapping file does not exist')
    # Create dict
    projects = dict(convert_number(project_names))
    # Change out name for mapped integer
    for i in changes:
        project_name = i[0]
        if project_name in projects:
            i[0] = int(projects[project_name])
        else:
            i[0] = -1

    return [np.array(changes, dtype=np.float32), projects]


to_ignore = [0, 5]
if __name__ == "__main__":
    # Preprocess data
    data, projects = preprocess(data, to_ignore)
    # Setup model
    model = setupModel()
    # Start training (apply gradient descent algorithm)
    model.fit(data, labels, n_epoch=10, batch_size=16, show_metric=True)

    shouldSave = input('Save model and mappings to file? [Y/n]: ').lower()
    if (shouldSave == '') or (list(shouldSave)[0] == 'y'):
        if not os.path.exists("saved_model"):
            os.makedirs("saved_model")
        # Save TF model
        model.save("saved_model/model.tfl")
        # Save project mapping
        np.save(project_name_mapping_path, projects)
