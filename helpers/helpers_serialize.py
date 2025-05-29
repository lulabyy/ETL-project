"""
helpers_serialize.py

This module provides utility functions for serializing and deserializing data to and from common configuration file formats,
including YAML, JSON, and TOML. It enables easy reading and writing of structured configuration or data files used throughout
the portfolio analytics application.

Functions:
- get_serialized_data: Reads and deserializes data from a file (YAML, JSON, or TOML) into a Python dictionary or list.
- dict_to_serialized_file: Serializes a Python dictionary and writes it to a file in the specified format, based on the file extension.

These helpers are intended to be imported and used within other modules. This file should not be executed directly.

See main_etl.py for data pipeline orchestration and main_streamlit.py for the Streamlit dashboard entry point.
"""

import os.path

from typing import Dict

import json
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

    Args:
        path (str): The file path of the serialized data to be loaded. Must be a valid path to a file with a supported extension (.yaml, .json, .toml).

    Returns:
        dict or list: A Python dictionary or list containing the deserialized data. The return type depends on the content of the file.

    Raises:
        ValueError: If the file extension is not supported or the file cannot be opened.
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

    Args:
        data (dict): The Python dictionary to be serialized and written to the file.
        path (str): The file path where the serialized data will be saved. The file extension determines the format (.yaml, .json, .toml).

    Returns:
        None

    Raises:
        ValueError: If the file extension is not supported.
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
