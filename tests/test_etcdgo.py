"""
Test package functionalities.
"""
import pytest
import etcd
import etcdgo
import etcdgo.config


def test_get_config_error():
    """
    Test get_config with json type.
    """
    with pytest.raises(ValueError):
        etcdgo.get_config(None, "json")

    with pytest.raises(ValueError):
        client = etcd.Client()
        etcdgo.get_config(client, None)

    with pytest.raises(NotImplementedError):
        client = etcd.Client()
        etcdgo.get_config(client, "txt")


def test_get_config_json():
    """
    Test get_config with json type.
    """
    client = etcd.Client()
    obj = etcdgo.get_config(client, "json")
    assert isinstance(obj, etcdgo.config.JsonConfig)


def test_get_config_yaml():
    """
    Test get_config with yaml type.
    """
    client = etcd.Client()
    obj = etcdgo.get_config(client, "yaml")
    assert isinstance(obj, etcdgo.config.YamlConfig)


def test_get_config_ini():
    """
    Test get_config with ini type.
    """
    client = etcd.Client()
    obj = etcdgo.get_config(client, "ini")
    assert isinstance(obj, etcdgo.config.IniConfig)


def test_get_config_basefolder(mocker):
    """
    Test get_config using basefolder.
    """
    mocker.patch('etcdgo.config.YamlConfig.__init__', return_value=None)

    client = etcd.Client()
    test_basefolder = "/config_test"
    etcdgo.get_config(client, "yaml", basefolder=test_basefolder)

    etcdgo.config.YamlConfig.__init__.assert_called_with(
        client,
        basefolder=test_basefolder)
