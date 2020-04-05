"""
Configuration classes definition.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import json
import yaml
import logging
import etcd
import flatten_dict


class Config:
    """
    Base configuration to implement in order to push/pull configurations inside
    an etcd database.
    """

    def __init__(self, client, basefolder="/config"):
        """
        Args:
            client (etcd.Client): etcd Client instance.
        """
        self._logger = logging.getLogger("converter")
        self._client = client
        self._basefolder = basefolder

    def _convert(self, filepath):
        """
        Convert a file into a dictionary.

        Args:
            filepath (str): path of the file to be pushed.
        """
        raise NotImplementedError()

    def push(self, name, filepath):
        """
        Push a format supported file into an etcd database.

        Args:
            name     (str): name to associate with file.
            filepath (str): path of the file to be pushed.
        """
        if not name or not isinstance(name, str):
            raise ValueError("name must be a string")

        if not filepath or not isinstance(filepath, str):
            raise ValueError("filepath must be a string")

        self._logger.info("pushing '%s' with name '%s'", filepath, name)

        # convert  to dict
        data = self._convert(filepath)

        # flatten the dictionary
        config_path = "%s/%s" % (self._basefolder, name)
        paths = flatten_dict.flatten(data)

        for dirs, value in paths.items():
            path = config_path + "/" + '/'.join(item for item in dirs)
            self._logger.debug("setting: %s -> %s", path, value)
            self._client.set(path, value)

        self._logger.info("configuration pushed")

    def pull(self, name):
        """
        Pull a format supported configuration from an etcd database.

        Args:
            name (str): name to associate with file.

        Returns:
            dict: configuration stored inside the database.
        """
        if not name or not isinstance(name, str):
            raise ValueError("name must be a string")

        self._logger.info("fetching '%s'", name)

        config_path = "%s/%s" % (self._basefolder, name)
        root = self._client.read(config_path, recursive=True)
        if not root:
            return dict()

        flat_dict = {
            leaf.key.replace(config_path, ""):
            leaf.value for leaf in root.leaves
        }
        config = flatten_dict.unflatten(flat_dict, splitter="path")['/']

        self._logger.info("configuration fetched")

        return config


class JsonConfig(Config):
    """
    Push/pull JSON configurations inside an etcd database.
    """

    def _convert(self, filepath):
        data = dict()
        with open(filepath, 'r') as fdata:
            data = json.loads(fdata.read())
        return data


class YamlConfig(Config):
    """
    Push/pull Yaml configurations inside an etcd database.
    """

    def _convert(self, filepath):
        data = dict()
        with open(filepath, 'r') as fdata:
            data = yaml.safe_load(fdata.read())
        return data
