from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

def get_config() -> ConfigParser:
    """
    Load config/config.ini and normalize [paths] entries to absolute paths.
    Relative paths in config.ini are interpreted relative to the PROJECT ROOT
    (i.e., the parent of the config/ directory).
    """
    script_dir = Path(__file__).resolve().parent           # .../program_files
    project_root = script_dir.parent                       # .../IBM-Senior-Design
    config_path = project_root / "config" / "config.ini"

    if not config_path.is_file():
        raise FileNotFoundError(f"config.ini not found at {config_path}")

    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    cfg.read(config_path)

    # Normalize all [paths] entries to absolute paths
    if "paths" in cfg:
        for key, val in list(cfg["paths"].items()):
            p = Path(val).expanduser()
            if not p.is_absolute():
                p = (project_root / p).resolve()
            cfg["paths"][key] = str(p)

    return cfg

def set_config_value(section: str, key: str, value: str):
    """
    Update a value in config/config.ini (creating the section if needed).

    Example:
        set_config_value('constraints', 'target_utilization', '0.6')
    """
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    config_path = project_root / "config" / "config.ini"

    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    read_files = cfg.read(config_path)
    if not read_files:
        raise FileNotFoundError(f"config.ini not found at {config_path}")

    if section not in cfg:
        cfg.add_section(section)

    cfg[section][key] = value

    with open(config_path, "w", encoding="utf-8") as configfile:
        cfg.write(configfile)