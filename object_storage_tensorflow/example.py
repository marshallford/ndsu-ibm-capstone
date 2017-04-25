import object_storage_tensorflow as obj_tf
# import os
# from utils import ROOT_DIR

testingFile = open('/tmp/testing.txt', 'r').read()
obj_tf.s3.upload('my-test-bucket', 'foobar', testingFile)
obj_tf.s3.download('my-test-bucket', 'foobar')
