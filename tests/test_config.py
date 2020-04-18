"""
Unittests for config module.
"""
import os
import pytest
import etcd3
import etcdgo
import configparser
import yaml
import json

MOCKED = os.environ.get("PYTEST_MOCKED", None)


@pytest.fixture
def config(mocker):
    """
    Config to test.
    """
    if MOCKED:
        mocker.patch('etcd3.Etcd3Client.__init__', return_value=None)
        mocker.patch('etcd3.Etcd3Client.get_all')
        mocker.patch('etcd3.Etcd3Client.put')

    def _callback(type):
        obj = etcdgo.get_config(
            etcd3.Etcd3Client(),
            type,
            basefolder="/config_test")

        return obj

    return _callback


def test_config_push_error(config):
    """
    Test errors when using push.
    """
    obj = config("yaml")

    with pytest.raises(ValueError):
        obj.push(None, "myfile.txt")

    with pytest.raises(ValueError):
        obj.push(list(), "myfile.txt")

    with pytest.raises(ValueError):
        obj.push("test", None)

    with pytest.raises(ValueError):
        obj.push("test", list())


def test_config_pull_error(config):
    """
    Test errors when using pull.
    """
    obj = config("yaml")

    with pytest.raises(ValueError):
        obj.pull(None)

    with pytest.raises(ValueError):
        obj.pull(list())


def test_yaml_push_pull(tmpdir, config):
    """
    Test YamlConfig::push/pull method implementation.
    """
    testfile = tmpdir / "config.yaml"
    testfile.write("""
        people:
            gigi:
                surname: burigi
                birth: 4/7/1916
            osvaldo:
                surname: carrube
                birth: 5/8/1980
    """)
    obj = config("yaml")
    obj.push("config_yaml", str(testfile))

    if MOCKED:
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_yaml/people/gigi/surname", "burigi")
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_yaml/people/gigi/birth", "4/7/1916")
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_yaml/people/osvaldo/surname", "carrube")
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_yaml/people/osvaldo/birth", "5/8/1980")
    else:
        expected_data = {
            "people": {
                "gigi": {
                    "surname": "burigi",
                    "birth": "4/7/1916"
                },
                "osvaldo": {
                    "surname": "carrube",
                    "birth": "5/8/1980"
                }
            }
        }

        data = obj.pull("config_yaml")
        assert data == expected_data

        data_str = obj.dump("config_yaml")
        assert yaml.safe_load(data_str) == expected_data


def test_json_push_pull(tmpdir, config):
    """
    Test JsonConfig::push/pull method implementation.
    """
    testfile = tmpdir / "config.json"
    testfile.write("""
        {
            "people": {
                "gigi": {
                    "surname": "burigi",
                    "birth": "4/7/1916"
                },
                "osvaldo": {
                    "surname": "carrube",
                    "birth": "5/8/1980"
                }
            }
        }
    """)
    obj = config("json")
    obj.push("config_json", str(testfile))

    if MOCKED:
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_json/people/gigi/surname", "burigi")
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_json/people/gigi/birth", "4/7/1916")
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_json/people/osvaldo/surname", "carrube")
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_json/people/osvaldo/birth", "5/8/1980")
    else:
        expected_data = {
            "people": {
                "gigi": {
                    "surname": "burigi",
                    "birth": "4/7/1916"
                },
                "osvaldo": {
                    "surname": "carrube",
                    "birth": "5/8/1980"
                }
            }
        }

        data = obj.pull("config_json")
        assert data == expected_data

        data_str = obj.dump("config_json")
        assert json.loads(data_str) == expected_data


def test_ini_push_pull(tmpdir, config):
    """
    Test IniConfig::push/pull method implementation.
    """
    testfile = tmpdir / "config.ini"
    testfile.write("""
        [gigi]
        surname=burigi
        birth=4/7/1916

        [osvaldo]
        surname=carrube
        birth=5/8/1980
    """)
    obj = config("ini")
    obj.push("config_ini", str(testfile))

    if MOCKED:
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_ini/gigi/surname", "burigi")
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_ini/gigi/birth", "4/7/1916")
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_ini/osvaldo/surname", "carrube")
        etcd3.Etcd3Client.put.assert_any_call(
            "/config_test/config_ini/osvaldo/birth", "5/8/1980")
    else:
        expected_data = {
            "gigi": {
                "surname": "burigi",
                "birth": "4/7/1916"
            },
            "osvaldo": {
                "surname": "carrube",
                "birth": "5/8/1980"
            }
        }

        data = obj.pull("config_ini")
        assert data == expected_data

        data_str = obj.dump("config_ini")
        parser = configparser.ConfigParser()
        parser.read_string(data_str)
        config_data = {section: dict(parser.items(section))
                       for section in parser.sections()}

        assert config_data == expected_data
