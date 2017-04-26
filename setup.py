#!/usr/bin/env python
# https://docs.python.org/3/distutils/setupscript.html

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ndsu-ibm-capstone',
    version='1.0',
    description='TensorFlow Object Storage Data Plugin',
    author='Marshall ford',
    author_email='',
    url='',
    install_requires=[
        'boto3',
        'pyyaml'
    ],
)
