# validate.py
import json
from jsonschema import Draft202012Validator

with open("schema.json") as f:
    schema = json.load(f)

validator = Draft202012Validator(schema)

def check(path):
    with open(path) as f:
        data = json.load(f)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if not errors:
        print(f"{path}: valid")
    else:
        print(f"{path}: invalid")
        for e in errors:
            print(f" - at /{'/'.join(map(str,e.path))}: {e.message}")


check("valid.json")
check("invalid.json")
