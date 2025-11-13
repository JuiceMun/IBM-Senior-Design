from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

# ----------------------------
# Helpers
# ----------------------------
def _project_root() -> Path:
    """Absolute path to the project root (parent of program_files/)."""
    return Path(__file__).resolve().parent.parent

def _config_path(config_name: str) -> Path:
    """Absolute path to the desired config file inside /config."""
    path = _project_root() / "config" / config_name
    if not path.is_file():
        raise FileNotFoundError(f"{config_name} not found at {path}")
    return path

def _load_config(config_name: str) -> ConfigParser:
    """Load a ConfigParser with ExtendedInterpolation."""
    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    cfg.read(_config_path(config_name))
    return cfg

def _normalize_paths(cfg: ConfigParser) -> None:
    """Normalize [paths] section entries to absolute paths from project root."""
    if "paths" not in cfg:
        return
    root = _project_root()
    for key, val in list(cfg["paths"].items()):
        p = Path(val).expanduser()
        if not p.is_absolute():
            p = (root / p).resolve()
        cfg["paths"][key] = str(p)

# ----------------------------
# Public
# ----------------------------
def get_config(config_name: str) -> ConfigParser:
    """
    Load config/<config_name> and normalize [paths] entries to absolute paths.
    Relative paths are interpreted relative to the project root.
    """
    cfg = _load_config(config_name)
    _normalize_paths(cfg)
    return cfg

def set_config_value(config_name: str, section: str, key: str, value: str) -> None:
    """
    Update a value in config/<config_name> (creating the section if needed) and
    persist the change to disk.
    """
    cfg = _load_config(config_name)
    if section not in cfg:
        cfg.add_section(section)
    cfg[section][key] = value

    with open(_config_path(config_name), "w", encoding="utf-8") as fp:
        cfg.write(fp)