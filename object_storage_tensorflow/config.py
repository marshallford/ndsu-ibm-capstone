import yaml
import os
from .utils import ROOT_DIR


def get():
    filename = os.path.join(ROOT_DIR, '../config.yaml')
    config = {}
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            config = yaml.load(f)
    else:
        config['endpoint'] = os.environ['NDSU_IBM_ENDPOINT']
        config['accessKeyId'] = os.environ['NDSU_IBM_ACCESSKEYID']
        config['secretAccessKey'] = os.environ['NDSU_IBM_SECRETACCESSKEY']
    return config
