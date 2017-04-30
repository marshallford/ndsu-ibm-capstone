# ndsu-ibm-capstone
TensorFlow Object Storage Data Plugin

[Project Specification Document](https://docs.google.com/document/d/1mr2ggZHrlI0iniVcTVem0Ymqx7VJABBGUVTVuMMH41I/edit?usp=sharing)

## Workstation/Dev setup

### Installation
* Python 3
* Dependencies: `pip install .`
* Dev Dependencies: `pip install -r requirements.txt`
* Pathing ?: `python setup.py develop`

### Usage
* Lint all: `make lint`

#### Example config.yaml
```
endpoint: https://s3.foo.bar.net
accessKeyId: kpXpAspCbzZwNvxF
secretAccessKey: TAbnyKdWbTtsyhDm
```

#### Env vars
to add: `export FOO="str"`

* `NDSU_IBM_ENDPOINT`
* `NDSU_IBM_ACCESSKEYID`
* `NDSU_IBM_SECRETACCESSKEY`

### Testing
* run tests: `make test`

## Gerrit OpenStack demo

### Installation
* Dev Dependencies: `pip install -r openstack_gerrit/requirements.txt`

### Usage
* run collector: `cd collector && python main.py`
* even out dataset (optional): `perl get_50_50.perl`
* generate model: `python generate_model.py`
* test live data against model: `python live_gerrit_stream.py`

#### Example config.yaml
```
openstack_ssh_key: "/home/marshall/.ssh/marshallford-openstack"
userid: "marshallford"
bucket: "my-test-bucket"
remote_folder: "saved_model"
```
