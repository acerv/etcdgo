
Introduction
============

etcdgo is a library to push/pull configurations inside etcd databases.
Supported filetypes are the following:

* JSON
* Yaml
* INI

For example:

```python
import etcd
import etcdgo

client = etcd.Client(host='127.0.0.1', port=4003)

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
