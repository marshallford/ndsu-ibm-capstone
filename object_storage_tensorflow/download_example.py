import object_storage_tensorflow as obj_tf
# import os
# from utils import ROOT_DIR

conn = obj_tf.s3.getConnection()
# data = open(os.path.join(ROOT_DIR, '../LICENSE'), 'rb')
# conn.Bucket('my-test-bucket').put_object(Key='LICENSE', Body=data)

myTestBucket = conn.Bucket('my-test-bucket')
myTestBucket.download_file('LICENSE', '/tmp/LICENSE.proof')
