import object_storage_tensorflow as obj_tf
import os
# from utils import ROOT_DIR


# basic
# testingFile = open('/tmp/testing.txt', 'r').read()
# obj_tf.s3.upload('my-test-bucket', 'testing.txt', testingFile)
# obj_tf.s3.download('my-test-bucket', 'testing.txt')

# folders
filenames = []
data = []
root = '/tmp/testing'
folder = 'testing'
for item in os.listdir(root):
    path = os.path.join(root, item)
    if os.path.isfile(path):
        filenames.append(item)
        data.append(open(path, 'r').read())

obj_tf.s3.uploadFolder('my-test-bucket', folder, filenames, data)
obj_tf.s3.downloadFolder('my-test-bucket', folder)
