"""
package definition.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import etcd3
import etcdgo.config


def get_config(client, config_type, basefolder="/config"):
    """
    Return an object that can be used to push/pull configurations inside
    an etcd database.

    Examples:

        import etcd3
        import etcdgo

        client = etcd3.Etcd3Client()

        # push a json configuration inside database
        config = etcdgo.get_config(client, "json")
        config.push("myconfig", "myfile.json")

        # push a yaml configuration inside database
        config = etcdgo.get_config(client, "yaml")
        config.push("myconfig", "myfile.yaml")

        # pull data from etcd database
        data = config.pull("myconfig")

    Args:
        client (etcd3.Etcd3Client): etcd client object.
        config_type    (str): configuration type. Supported: json, yaml.
        basefolder     (str): root of the configuration inside the etcd database.

    Returns:
        Config: object to push/pull configurations inside an etcd database.
    """
    if not client or not isinstance(client, etcd3.Etcd3Client):
        raise ValueError("client must be of type etcd3.Etcd3Client")

    if not config_type or not isinstance(config_type, str):
        raise ValueError("config_type must be a string")

    obj = None
    if config_type.lower() == "json":
        obj = etcdgo.config.JsonConfig(client, basefolder=basefolder)
    elif config_type.lower() == "yaml":
        obj = etcdgo.config.YamlConfig(client, basefolder=basefolder)
    elif config_type.lower() == "ini":
        obj = etcdgo.config.IniConfig(client, basefolder=basefolder)
    else:
        raise NotImplementedError("'%s' format is not supported" % config_type)

    return obj
