"""
Configuration classes definition.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import json
import yaml
import logging
import etcd


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

        Example:
            Convert the given file into a dictionary like..

                {
                    "myname0": {
                        "config0": "1",
                        "config1": "2"
                    },
                    "myname1": {
                        "config0": "0"
                    },
                }

            and then save it as..

                /config/myname0/config0 = 1
                /config/myname0/config1 = 2
                /config/myname1/config0 = 0

        Args:
            name     (str): name to associate with file.
            filepath (str): path of the file to be pushed.
        """
        if not name or not isinstance(name, str):
            raise ValueError("name must be a string")

        if not filepath or not isinstance(filepath, str):
            raise ValueError("filepath must be a string")

        self._logger.info("pushing '%s' with name '%s'", filepath, name)

        config_path = "%s/%s" % (self._basefolder, name)

        paths = dict()

        def dict_path(data, path):
            for key, value in data.items():
                next_path = path + "/" + key
                if isinstance(value, dict):
                    dict_path(value, next_path)
                elif isinstance(value, str):
                    paths[next_path] = value

        data = self._convert(filepath)
        dict_path(data, config_path)

        for path, value in paths.items():
            self._logger.debug("setting: %s -> %s", path, value)
            self._client.set(path, value)

        self._logger.info("configuration pushed")

    def pull(self, name):
        """
        Pull a format supported configuration from an etcd database.

        Example:
            The following DB configuration..

                /config/myname0/config0 = 1
                /config/myname0/config1 = 2
                /config/myname1/config0 = 0

            becomes..

                {
                    "myname0": {
                        "config0": "1",
                        "config1": "2"
                    },
                    "myname1": {
                        "config0": "0"
                    },
                }

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

        config = dict()

        for leaf in root.leaves:
            leaf_str = leaf.key.replace(config_path + "/", "")

            self._logger.debug("reading %s", leaf.key)
            dirs = leaf_str.split("/")

            # avoid empty paths
            if not dirs or not dirs[0]:
                continue

            # create the branch
            pointer = config
            if len(dirs) > 1:
                for dirname in dirs[:-1]:
                    if dirname not in pointer:
                        pointer[dirname] = dict()

                    pointer = pointer.get(dirname)

            pointer[dirs[-1]] = leaf.value

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
