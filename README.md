# ndsu-ibm-capstone
TensorFlow Object Storage Data Plugin

## Workstation/Dev setup

### Installation
* Python 3?
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
