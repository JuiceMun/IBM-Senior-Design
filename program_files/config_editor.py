from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path
from config_loader import get_config

def set_config_value(section: str, key: str, value: str):
    """
    When describing system description, the user will be able to
    set certain values in the config.ini file through the Chat UI.

    E.g. set_config_value('constraints', 'target_utilization', '0.6') 
         => sets target_utilization to 0.6 in the [constraints] section.
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    config_path = project_root / "config" / "config.ini"

    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    read_files = cfg.read(config_path)
    if not read_files:
        raise FileNotFoundError(f"config.ini not found at {config_path}")

    if section not in cfg:
        cfg.add_section(section)
    cfg[section][key] = value

    with open(config_path, 'w') as configfile:
        cfg.write(configfile)

if __name__ == "__main__":
    # Example usage
    config = get_config()
    print("Loaded Current Configuration:\n")
    for section in config.sections():
        print(f"[{section}]")
        for key, val in config[section].items():
            print(f"{key} = {val}")
        print('\n') 
    print('--------------------------------\n')

    # Example of setting a config value
    set_config_value('constraints', 'target_utilization', '0.6')
    config = get_config()
    print("Loaded Updated Configuration:\n")
    for section in config.sections():
        print(f"[{section}]")
        for key, val in config[section].items():
            print(f"{key} = {val}")
        print('\n')

    # Reset example value to original
    set_config_value('constraints', 'target_utilization', '0.5')