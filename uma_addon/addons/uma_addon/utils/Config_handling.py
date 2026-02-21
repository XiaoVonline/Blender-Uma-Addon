import os
import configparser
from typing import Any

config_path = os.path.join(os.path.dirname(__file__), "..", "settings.cfg")

def get_config() -> configparser.ConfigParser:
    """
    Get the ConfigParser object for the settings.cfg file.

    :return configparser.ConfigParser: ConfigParser for the config file
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def get_config_parameter(
    section: str,
    parameter: str,
    data_type=str,
    fallback=None,
    config: configparser.ConfigParser = None,
) -> Any:
    """
    Get config parameter value from the config file.

    :param str section: Section name of the config
    :param str parameter: Parameter name
    :param _type_ data_type: Parameter value data type, defaults to str
    :param _type_ fallback: Fallback value if parameter is not found, defaults to None
    :param configparser.ConfigParser config: ConfigParser for the config file, defaults to None
    :return Any: Value of the config parameter
    """
    if config is None:
        config = get_config()

    get_method = {
        str: config.get,
        bool: config.getboolean,
        int: config.getint,
        float: config.getfloat,
        set: config.get,
    }.get(data_type, config.get)

    if data_type is set:
        # Check if the parameter exists in the config
        if config.has_option(section, parameter):
            value = config.get(section, parameter)
            # Check if the value is empty
            value = eval(value) if value else set()
        else:
            value = fallback
    else:
        value = get_method(section, parameter, fallback=fallback)

    return value

def set_config_parameter(
    section: str,
    parameter: str,
    value: str,
    config: configparser.ConfigParser = get_config(),
) -> None:
    """
    Set the given configuration to value in the section with the provided parameter.

    :param str section: Section name in the config file
    :param str parameter: Parameter of the config
    :param str value: Value of the config
    :param configparser.ConfigParser config: ConfigParser object, defaults to get_config()
    """
    # 如果 section 不存在，则创建
    if not config.has_section(section):
        config.add_section(section)

    config.set(section, parameter, value)
    with open(config_path, "w") as configfile:
        config.write(configfile)

def get_panel_name() -> str:
    """
    Get the N panel name from the config file. Defaults MMD.

    :return str: N panel name
    """
    return get_config_parameter("Addon Settings", "panel_name", fallback="MMD")