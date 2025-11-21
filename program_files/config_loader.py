from configparser import ConfigParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] # Project root directory

def load_config(path=None) -> ConfigParser:
    """
    Load configuration from an .ini file.
    Args:
        path (str, optional): Path to the config file. Defaults to None, which loads the dev config.
    Returns:
        ConfigParser: The loaded configuration object.
    """
    if path is None:
        path = ROOT / "config" / "dev_config.ini"
    config = ConfigParser()
    config.read(path)
    return config
    