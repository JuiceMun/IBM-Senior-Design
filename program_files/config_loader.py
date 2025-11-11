from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

def get_config() -> ConfigParser:
    """
    Load config/config.ini and normalize [paths] entries to absolute paths.
    Relative paths in config.ini are interpreted relative to the PROJECT ROOT
    (i.e., the parent of the config/ directory).
    """
    # Get current file's directory: .../project_root/config
    config_dir = Path(__file__).resolve().parent
    project_root = config_dir.parent
    config_path = project_root / "config" / "config.ini"   # <- make sure it works regardless of cwd

    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    if not config_path.is_file():
        raise FileNotFoundError(f"config.ini not found at {config_path}")

    cfg.read(config_path)

    # Normalize all [paths] entries to absolute paths
    if "paths" in cfg:
        for key, val in list(cfg["paths"].items()):
            p = Path(val).expanduser()
            if not p.is_absolute():
                p = (project_root / p).resolve()
            cfg["paths"][key] = str(p)

    return cfg