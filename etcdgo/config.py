"""
Configuration classes definition.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import logging
import configparser
import json
import yaml
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

        config_path = "{0}/{1}".format(self._basefolder, name)

        # convert  to dict
        data = self._convert(filepath)

        # flatten the dictionary
        def slash_reducer(k1, k2):
            if k1 is None:
                return k2

            return "{0}/{1}".format(k1, k2)

        paths = flatten_dict.flatten(data, reducer=slash_reducer)

        for dirs, value in paths.items():
            path = "{0}/{1}".format(config_path, dirs)
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

        config_path = "{0}/{1}".format(self._basefolder, name)
        root = self._client.read(config_path, recursive=True)
        if not root:
            return dict()

        def slash_reducer(flat_key):
            # first element is empty
            return flat_key.split("/")[1:]

        flat_dict = {
            leaf.key.replace(config_path, ""):
            leaf.value for leaf in root.leaves
        }
        config = flatten_dict.unflatten(flat_dict, splitter=slash_reducer)

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


class IniConfig(Config):
    """
    Push/pull Yaml configurations inside an etcd database.
    """

    def _convert(self, filepath):
        parser = configparser.ConfigParser()
        parser.read(filepath)
        data = {section: dict(parser.items(section))
                for section in parser.sections()}
        return data
