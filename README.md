[![Build Status](https://travis-ci.org/acerv/etcdgo.svg?branch=master)](https://travis-ci.org/acerv/etcdgo)

Introduction
============

etcdgo is a library to push/pull configurations inside [etcd](https://etcd.io)
databases. Supported filetypes are the following:

* JSON
* Yaml
* INI

Usage example:

```python
import etcd3
import etcdgo

client = etcd3.Etcd3Client(host='127.0.0.1', port=4003)

# push a json configuration inside database
config = etcdgo.get_config(client, "json")
config.push("myconfig", "myfile.json")

# push a yaml configuration inside database
config = etcdgo.get_config(client, "yaml")
config.push("myconfig", "myfile.yaml")

# push a ini configuration inside database
config = etcdgo.get_config(client, "ini")
config.push("myconfig", "myfile.ini")

# pull data from etcd database
data = config.pull("myconfig")
```

To install the library:

```bash
pip install etcdgo
```

Push/pull via command line
==========================

etcdgo library contains a tool called ``etcdgo-cli`` which can be used to
push/pull configurations inside an etcd database.

```bash
# push ini configuration
$ etcdgo-cli \
    --hostname 10.0.1.21 \
    --port 2379 \
    --basefile /configs \
    push pytest0 pytest.ini

# pull configuration
$ etcdgo-cli \
    --hostname 10.0.1.21 \
    --port 2379 \
    --basefile /configs \
    pull --output-type=ini pytest0
[pytest]
addopts = -vv -s
log_cli = True
log_level = DEBUG
```

``etcdgo-cli`` will automatically recognize the file extension and push it as
needed, but pull command needs to specify the output type, via ``--output-type``
option.

How data is stored
==================

Before pushing configurations inside an etcd database, all files are converted
into a dictionary and then flatten. The ``basefolder`` is given to the configuration
object and it's the root of our configurations.

For example:

```python
import etcd3
import etcdgo

client = etcd3.Etcd3Client(host='127.0.0.1', port=4003)
config = etcdgo.get_config(client, "ini", basefolder="/configs")
config.push("foods", "myconfig.ini")
```

Our ``myconfig.ini`` configuration:

```ini
[apple]
color = red
taste = sweet

[coffee]
color = black
taste = bitter
```

Once ``myconfig.ini`` is pushed into etcd, it will be flatten as following:

```etcd
/configs/foods/apple/color = 'red'
/configs/foods/apple/taster = 'sweet'
/configs/foods/coffee/color = 'black'
/configs/foods/coffee/taste = 'bitter'
```

Yaml/JSON configurations are flatten with the same principle. In this case,
**lists are stored as strings**.

For example:

```python
import etcd3
import etcdgo

client = etcd3.Etcd3Client(host='127.0.0.1', port=4003)
config = etcdgo.get_config(client, "json", basefolder="/configs")
config.push("foods", "myconfig.json")
```

Our ``myconfig.json`` configuration:

```json
{
    "fruits" : {
        "apple" : {
            "color": "red",
            "taste": "sweet"
        },
        "coffee" : {
            "color": "black",
            "taste": "bitter"
        },
    },
    "sets" : ["fruits", "vegetables" ]
}
```

Once ``myconfig.json`` is pushed into etcd, it will be flatten as following:

```etcd
/configs/foods/fruits/apple/color = 'red'
/configs/foods/fruits/apple/taster = 'sweet'
/configs/foods/fruits/coffee/color = 'black'
/configs/foods/fruits/coffee/taste = 'bitter'
/configs/foods/sets = '["fruits", "vegetables"]'
```
