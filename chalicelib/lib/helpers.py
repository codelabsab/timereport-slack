from ruamel.yaml import YAML

yaml=YAML(typ='safe')


def parse_config(path='config.yaml'):
    """
    Parse config written in yaml
    :param path: the path to the config file. config.yaml is default
    :return: config
    """
    with open(path) as fd:
        config = yaml.load(fd)

    return config