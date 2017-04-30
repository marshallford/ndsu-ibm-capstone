# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import yaml
import numpy as np
import tflearn
from tflearn.data_utils import load_csv
import object_storage_tensorflow as obj_tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Load CSV file, indicate that the first column represents labels
data, labels = load_csv('changes.csv', target_column=0,
                        categorical_labels=True, n_classes=2)

project_name_mapping_file = 'project_name_mapping.npy'


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


def getConfig():
    configFile = 'config.yaml'
    config = {}
    if os.path.exists(configFile):
        with open(configFile, 'r') as f:
            config = yaml.load(f)
    return config


config = getConfig()
bucket = config['bucket']
remoteFolder = config['remote_folder']


def preprocess(changes, columns_to_delete, is_live):
    # Sort by descending id and delete columns
    for column_to_delete in sorted(columns_to_delete, reverse=True):
        [change.pop(column_to_delete) for change in changes]
    # Project id mappings
    projects = {}
    if is_live:
        remotePath = obj_tf.s3.getBaseFolderPath(bucket, remoteFolder)
        projects_file = '{}/{}'.format(remotePath, project_name_mapping_file)
        projects = np.load(projects_file).item()
    else:
        project_names = []
        for i in changes:
            project_names.append(i[0])
        projects = dict(convert_number(project_names))
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
    data, projects = preprocess(data, to_ignore, False)
    # Setup model
    model = setupModel()
    # Start training (apply gradient descent algorithm)
    print('training on data...')
    model.fit(data, labels, n_epoch=10, batch_size=16, show_metric=True)

    shouldSave = input('Save model to file? [Y/n]: ').lower()
    if (shouldSave == '') or (list(shouldSave)[0] == 'y'):
        localSave = "saved_model"
        if not os.path.exists(localSave):
            os.makedirs(localSave)
        # Save TF model
        print("saving model...")
        model.save("{}/model.tfl".format(localSave))
        # Save project mapping
        print("saving project id mapping...")
        np.save("{}/{}".format(localSave, project_name_mapping_file), projects)
        # Upload to object storage
        filenames = []
        data = []
        for item in os.listdir(localSave):
            path = os.path.join(localSave, item)
            if os.path.isfile(path):
                filenames.append(item)
                data.append(open(path, 'rb', ).read())
        print("uploading to object storage (S3)...")
        obj_tf.s3.uploadFolder(bucket, remoteFolder, filenames, data)
        print('finished.')
