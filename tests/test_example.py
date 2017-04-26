import os
import unittest

import object_storage_tensorflow as obj_tf


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


class TestS3Connection(unittest.TestCase):

    @unittest.skipUnless(
        os.environ.get("TRAVIS_PULL_REQUEST") == 'false',
        "S3 tests will fail for Pull Requests due to lack of secrets.")
    def test_buckets(self):
        conn = obj_tf.s3.getConnection()
        names = []
        for bucket in conn.buckets.all():
            names.append(bucket.name)
        self.assertTrue(len(names) > 0)


if __name__ == '__main__':
    unittest.main()
