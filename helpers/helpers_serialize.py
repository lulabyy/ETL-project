import json
import os.path
from typing import Dict

import sqlite3

import tomli
import toml
import yaml


def get_serialized_data(path: str) -> Dict:
    """
    Reads and deserializes data from a file based on its extension. Supported formats are YAML, JSON, and TOML.

    This function opens the file at the specified path, identifies its extension, and deserializes its content
    into a Python dictionary or list (depending on the format). The following file extensions are supported:
    - `.yaml` or `.yml` (YAML format)
    - `.json` (JSON format)
    - `.toml` (TOML format)

    If the file extension is unsupported, a `ValueError` is raised.

    :param path: The file path of the serialized data to be loaded.
                  This must be a valid path to a file with a supported extension (.yaml, .json, or .toml).
    :return: A Python dictionary or list containing the deserialized data.
             The return type depends on the content of the file (e.g., a dictionary for JSON and TOML, a list or dictionary for YAML).
    :raises ValueError: If the file extension is not supported or the file cannot be opened.
    """
    _, extension = os.path.splitext(path)

    with open(path, mode="r") as file:
        if extension == ".yaml":
            return yaml.load(file, Loader=yaml.FullLoader)
        elif extension == ".json":
            return json.load(file)
        elif extension == ".toml":
            return tomli.load(file)

        raise ValueError(f"Unsupported file extension {extension} | file={path}")


def dict_to_serialized_file(data: Dict, path: str) -> None:
    """
    Serializes a Python dictionary and writes it to a file in a specified format.

    This function takes a dictionary and writes it to a file at the given path. The file's extension determines
    the format of the serialized data. Supported formats include:
    - YAML (.yaml or .yml)
    - JSON (.json)
    - TOML (.toml)

    The function will raise a `ValueError` if the file extension is unsupported.

    :param data: The Python dictionary to be serialized and written to the file.
    :param path: The file path where the serialized data will be saved.
                  The file extension determines the format of the serialized data.
                  Supported extensions: .yaml, .json, .toml.
    :raises ValueError: If the file extension is not supported.
    """
    _, extension = os.path.splitext(path)

    with open(path, mode="w") as file:
        if extension == ".yaml":
            yaml.dump(data, file)
        elif extension == ".json":
            json.dump(data, file, indent=4)
        elif extension == ".toml":
            toml.dump(data, file)

        raise ValueError(f"Unsupported file extension {extension} | file={path}")

