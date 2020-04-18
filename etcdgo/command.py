"""
command line definition.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
import click
import etcd3
import etcdgo


class Arguments:
    """
    Default program arguments.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.client = None
        self.base_folder = None


# pylint: disable=invalid-name
pass_arguments = click.make_pass_decorator(Arguments, ensure=True)


class CatchAllExceptions(click.Group):
    """
    Class created to catch all exceptions coming from the application.
    """

    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except Exception as exc:
            click.echo(str(exc))


@click.group(cls=CatchAllExceptions)
@click.option(
    '--hostname',
    '-h',
    default="localhost",
    type=click.STRING,
    help="Etcd database hostname (default: localhost)")
@click.option(
    '--port',
    '-p',
    default="2349",
    type=click.INT,
    help="Etcd database port (default: 2349)")
@click.option(
    '--base-folder',
    '-f',
    default="/config",
    type=click.STRING,
    help="Etcd database base folder (default: /config)")
@pass_arguments
def cli(args, hostname, port, base_folder):
    """
    Etcdgo command line to push/pull configurations.
    """
    args.client = etcd3.Etcd3Client(hostname, port)
    args.base_folder = base_folder


@cli.command()
@click.argument("label")
@click.argument("config")
@pass_arguments
def push(args, label, config):
    """
    Push/update a configuration.
    """
    if not label:
        raise ValueError("label can't be empty.")

    if not config:
        raise ValueError("config can't be empty.")

    if not os.path.isfile(config):
        raise ValueError("configuration file doesn't exist.")

    filename, fileext = os.path.splitext(config)
    if not filename:
        raise ValueError("filename can't be empty.")

    config_type = None
    if fileext == ".json":
        config_type = "json"
    elif fileext in [".yaml", ".yml"]:
        config_type = "yaml"
    elif fileext == ".ini":
        config_type = "ini"
    else:
        raise ValueError("'%s' extension type is not supported." % fileext)

    config_client = etcdgo.get_config(
        args.client,
        config_type,
        basefolder=args.base_folder)

    config_client.push(label, config)


@cli.command()
@click.option(
    '--output-type',
    '-o',
    default="json",
    type=click.STRING,
    help="Configuration output type (default: json)")
@click.argument("label")
@pass_arguments
def pull(args, label, output_type):
    """
    Pull a configuration and convert it into a specific type.
    """
    if not label:
        raise ValueError("label can't be empty.")

    if not output_type:
        raise ValueError("output_type can't be empty.")

    config_client = etcdgo.get_config(
        args.client,
        output_type,
        basefolder=args.base_folder)

    data_str = config_client.dump(label)
    click.echo(data_str)
