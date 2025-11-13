from program_files import config,data_conversion #,data_generator
from pathlib import Path



def print_new_section(title:str):
    print(f"\n"
          f"==================\n"
          f"{title}\n"
          f"==================\n"
          )

def get_files_in_directory(relative_path: str) -> list[str]:
    """
    Return a list of file names inside a directory.
    The directory path is interpreted relative to the project root
    (i.e., the directory where main.py lives).
    """
    # Project root is the directory containing THIS file (main.py)
    project_root = Path(__file__).resolve().parent

    target_dir = (project_root / relative_path).resolve()

    if not target_dir.exists():
        raise FileNotFoundError(f"Directory does not exist: {target_dir}")

    if not target_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {target_dir}")

    return [f.name for f in target_dir.iterdir() if f.is_file()]

def test_config():
    print_new_section("Config")

    print("Choose a method to test\n"
          "0 - get_config()\n"
          "1 - set_config_value()\n"
    )
    method = input()

    files = get_files_in_directory("./config")
    print("Choose a config file to test\n")
    for i in range(len(files)):
        print(f"{i} - {files[i]}")

    file = input()
    cfg = config.get_config(files[int(file)])

    if method == "0":
        for section in cfg.sections():
            print(f"[{section}]")
            for key, value in cfg[section].items():
                print(f"{key} = {value}")


    elif method == "1":

        raw = input(
            "Enter section, key, and new value\n"
            "(separated by spaces; value may contain spaces):\n"
        ).strip()

        parts = raw.split(maxsplit=2)
        if len(parts) < 3:
            print("You must enter section, key, and value.")
            return

        section, key, value = parts

        config.set_config_value(files[int(file)], section, key, value)
        print(f"Edit applied - exit program and see {files[int(file)]} to view change")

    else:
        print("Invalid Input")

    input("press enter to continue")



def test_data_conversion():
    print_new_section("Data Conversion")

def test_data_generator():
    print_new_section("Data Generator")

def main():
    print_new_section("IBM Stress Testing")

    while True:
        inp = input("Enter a number to test a file:\n"
                    "0: exit program\n"
                    "1: config.py\n"
                    "2: data_conversion.py\n"
                    "3: data_generator.py\n"
                    )

        if inp == "1":
            test_config()
        elif inp == "2":
            test_data_conversion()
        elif inp == "3":
            test_data_generator()
        elif inp == "0":
            print_new_section("Exiting Program")
            break

if __name__ == '__main__':
    main()