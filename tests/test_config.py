"""
Unittests for config module.
"""
import os
import pytest
import etcd
import etcdgo

MOCKED = os.environ.get("PYTEST_MOCKED", None)


@pytest.fixture
def config(mocker):
    """
    Config to test.
    """
    if MOCKED:
        mocker.patch('etcd.Client.__init__', return_value=None)
        mocker.patch('etcd.Client.read')
        mocker.patch('etcd.Client.set')

    def _callback(type):
        obj = etcdgo.get_config(
            etcd.Client(),
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
    obj.push("config0", str(testfile))

    if MOCKED:
        etcd.Client.set.assert_any_call(
            "/config_test/config0/people/gigi/surname", "burigi")
        etcd.Client.set.assert_any_call(
            "/config_test/config0/people/gigi/birth", "4/7/1916")
        etcd.Client.set.assert_any_call(
            "/config_test/config0/people/osvaldo/surname", "carrube")
        etcd.Client.set.assert_any_call(
            "/config_test/config0/people/osvaldo/birth", "5/8/1980")
    else:
        data = obj.pull("config0")
        assert data == {
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
    obj.push("config0", str(testfile))

    if MOCKED:
        etcd.Client.set.assert_any_call(
            "/config_test/config0/people/gigi/surname", "burigi")
        etcd.Client.set.assert_any_call(
            "/config_test/config0/people/gigi/birth", "4/7/1916")
        etcd.Client.set.assert_any_call(
            "/config_test/config0/people/osvaldo/surname", "carrube")
        etcd.Client.set.assert_any_call(
            "/config_test/config0/people/osvaldo/birth", "5/8/1980")
    else:
        data = obj.pull("config0")
        assert data == {
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
