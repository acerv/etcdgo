"""
Unittests for command module.
"""
import os
import pytest
from click.testing import CliRunner
import etcd3
import etcdgo.command


@pytest.fixture
def runner(mocker):
    """
    Click runner client.
    """
    mocker.patch('etcd3.Etcd3Client.__init__', return_value=None)
    mocker.patch('etcdgo.config.Config.__init__', return_value=None)

    runner = CliRunner()
    with runner.isolated_filesystem():
        def _callback(
                cmd,
                hostname="localhost",
                port="2349",
                basefolder="/cmdline_test"):
            ret = runner.invoke(etcdgo.command.cli, [
                "-h",
                hostname,
                "-p",
                port,
                "-f",
                basefolder,
            ] + cmd)

            return ret

        yield _callback


def test_cli_help(runner):
    """
    Test for --help option
    """
    ret = runner(['--help'])
    assert not ret.exception
    assert ret.exit_code == 0


def test_push_config_type_error(request, runner):
    """
    This test check if pushing non-supported configuration will raise
    an exception.
    """
    key = request.node.name

    with open("other.txt", "w") as config:
        config.write("data = test")

    # push configuration file
    ret = runner(['push', key, 'other.txt'])
    assert str(ret.exception) == "'.txt' extension type is not supported."
    assert ret.exit_code == 1


def test_push_empty_config_error(request, runner):
    """
    This test check if pushing with empty config will raise an exception.
    """
    ret = runner(['push', 'myconfig', ''])
    assert str(ret.exception) == "config can't be empty."
    assert ret.exit_code == 1


def test_push_empty_label_error(request, runner):
    """
    This test check if pushing a configuration with empty label will raise
    an exception.
    """
    ret = runner(['push', '', 'other.ini'])
    assert str(ret.exception) == "label can't be empty."
    assert ret.exit_code == 1


def test_push_config_not_exist_error(request, runner):
    """
    This test check if pushing non existing configuration will raise
    an exception.
    """
    key = request.node.name

    # configuration doesn't exist
    ret = runner(['push', key, 'other.ini'])
    assert str(ret.exception) == "configuration file doesn't exist."
    assert ret.exit_code == 1


def test_push_error(request, mocker, runner):
    """
    Push a configuration and check if exceptions are handled.
    """
    key = request.node.name

    with open("myconfig.ini", "w") as config:
        config.write("[config]\ndata = test")

    mocker.patch(
        "etcdgo.config.Config.push",
        side_effect=Exception("test exception"))

    # push configuration file
    ret = runner(['push', key, 'myconfig.ini'])
    assert str(ret.exception) == "test exception"
    assert ret.exit_code == 1


def test_push(request, mocker, runner):
    """
    Push a configuration.
    """
    key = request.node.name

    with open("myconfig.ini", "w") as config:
        config.write("[config]\ndata = test")

    mocker.patch("etcdgo.config.Config.push")

    # push configuration file
    ret = runner(['push', key, 'myconfig.ini'])
    assert not ret.exception
    assert ret.exit_code == 0

    etcdgo.config.Config.push.assert_called_with(key, "myconfig.ini")


def test_pull_empty_label_error(request, runner):
    """
    This test check if pulling a configuration with empty label will raise
    an exception.
    """
    ret = runner(['pull', ''])
    assert str(ret.exception) == "label can't be empty."
    assert ret.exit_code == 1


def test_pull_output_type_error(request, runner):
    """
    This test check if pulling a configuration with non supported output type
    will raise an exception.
    """
    ret = runner(['pull', 'mystuff', '--output-type', ''])
    assert str(ret.exception) == "output_type can't be empty."
    assert ret.exit_code == 1

    ret = runner(['pull', 'mystuff', '--output-type', 'txt'])
    assert str(ret.exception) == "'txt' format is not supported"
    assert ret.exit_code == 1


def test_pull_error(request, mocker, runner):
    """
    Pull a configuration and check if exceptions are handled.
    """
    key = request.node.name

    mocker.patch(
        "etcdgo.config.Config.dump",
        side_effect=Exception("test exception"))

    # push configuration file
    ret = runner(['pull', key])
    assert str(ret.exception) == "test exception"
    assert ret.exit_code == 1


def test_pull_ini(request, mocker, runner):
    """
    Push/pull a ini configuration.
    """
    key = request.node.name

    mocker.patch(
        "etcdgo.config.Config.dump",
        return_value="[config]\ntest = data")

    # push configuration file
    ret = runner(['pull', key, '--output-type', 'ini'])
    assert not ret.exception
    assert ret.exit_code == 0
    assert ret.output == "[config]\ntest = data\n"


def test_pull_json(request, mocker, runner):
    """
    Pull a json configuration.
    """
    key = request.node.name

    mocker.patch(
        "etcdgo.config.Config.dump",
        return_value="{\n'test':'data'\n}")

    # push configuration file
    ret = runner(['pull', key, '--output-type', 'json'])
    assert not ret.exception
    assert ret.exit_code == 0
    assert ret.output == "{\n'test':'data'\n}\n"


def test_pull_yaml(request, mocker, runner):
    """
    Pull a yaml configuration.
    """
    key = request.node.name

    mocker.patch(
        "etcdgo.config.Config.dump",
        return_value="people:\n  gianni: patoc\n  gigi: bufera\n")

    # push configuration file
    ret = runner(['pull', key, '--output-type', 'json'])
    assert not ret.exception
    assert ret.exit_code == 0
    assert ret.output == "people:\n  gianni: patoc\n  gigi: bufera\n\n"
