# config/config_loader.py
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

def get_config() -> ConfigParser:
    """
    Load config/config.ini and normalize [paths] entries to absolute paths.
    Relative paths in config.ini are interpreted relative to the PROJECT ROOT
    (i.e., the parent of the config/ directory).
    """
    config_dir = Path(__file__).resolve().parent          # .../IBM-Senior-Design/config
    project_root = config_dir.parent                      # .../IBM-Senior-Design
    config_path = config_dir / "config.ini"

    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    read_files = cfg.read(config_path)
    if not read_files:
        raise FileNotFoundError(f"config.ini not found at {config_path}")

    # Normalize all [paths] entries to absolute paths
    if "paths" in cfg:
        for key, val in list(cfg["paths"].items()):
            p = Path(val).expanduser()
            if not p.is_absolute():
                p = (project_root / p).resolve()          # <-- use project root, not config_dir
            cfg["paths"][key] = str(p)

    return cfg
