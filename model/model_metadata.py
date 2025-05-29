"""
model_metadata.py

This module defines dataclasses for the configuration of metadata used in the portfolio analytics application.
It structures information about the metadata columns and logger, and specifies where the metadata files are located.
These classes are typically instantiated from configuration files and used in ETL processes and application configuration.

Do not execute this file directly; it is intended to be imported.
"""

from dataclasses import dataclass
from typing import List, Dict, Sequence

@dataclass
class MetadataColumns:
    """
    Defines the groups of columns to be processed in the metadata: date columns, numeric columns,
    string columns, columns to drop, and any column renaming.

    Attributes:
        columns_date (Sequence[str]): Names of date columns.
        columns_numeric (Sequence[str]): Names of numeric columns.
        columns_string (Sequence[str]): Names of string columns.
        columns_to_drop (Sequence[str]): Columns to ignore or drop during processing.
        columns_new_names (Dict[str, str]): Mapping for column renaming (old name -> new name).
    """
    columns_date: Sequence[str]
    columns_numeric: Sequence[str]
    columns_string: Sequence[str]
    columns_to_drop: Sequence[str]
    columns_new_names: Dict[str, str]

@dataclass
class MetadataLogger:
    """
    Logger configuration parameters for metadata processing.

    Attributes:
        logname (str): Logger name.
        filename (str): Log file name.
    """
    logname: str
    filename: str

@dataclass
class MetadataConfig:
    """
    Complete configuration for metadata usage, including directory, filename,
    column structure, and logger configuration.

    Attributes:
        dir (str): Directory where the metadata file is located.
        file (str): Name of the metadata file.
        columns (MetadataColumns): Data column structure for metadata.
        logger (MetadataLogger): Logging parameters for metadata.
    """
    dir: str
    file: str
    columns: MetadataColumns
    logger: MetadataLogger
