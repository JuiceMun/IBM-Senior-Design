from program_files import config,data_conversion,user_input #,data_generator
from pathlib import Path

def print_new_section(title:str):
    print(f"\n\n"
          f"==================\n"
          f"{title}\n"
          f"==================\n"
          f"\n"
          )

def files_in_directory(relative_path: str) -> list[str]:
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

def test_validate_schema():
    print_new_section("Validate Schema")


    return None

def test_user_input():
    print_new_section("System Description")
    user_config_settings = user_input.ask_user()
    if user_config_settings is not None:
        config.set_user_config("user_config.ini", user_config_settings)
    return None

def main():
    print_new_section("IBM Stress Testing")
    print(files_in_directory("./data/queueing-network"))
    while True:
        inp = input("Enter a number to test a file:\n"
                    "1: config.py\n"
                    "2: data_conversion.py\n"
                    "3: data-generator.py\n"
                    "4: user_input.py\n"
                    "0: exit program\n")

        if inp == "1":
            test_validate_schema()
        elif inp == "2":
            print("2")
        elif inp == "3":
            print("3")
        elif inp == "4":
            test_user_input()
        elif inp == "0":
            print("exiting program")
            break

if __name__ == '__main__':
    main()