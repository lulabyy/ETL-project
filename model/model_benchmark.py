"""
model_benchmark.py

This module defines the dataclasses representing the complete configuration for benchmarks used in the portfolio analytics application.
It structures information about tickers, data columns, and logger configuration for benchmarks.
These classes are typically instantiated from YAML configuration files by helpers_config.py, and then used in ETL modules and the global configuration.

Do not execute this file directly; it is intended to be imported.
"""

from dataclasses import dataclass
from typing import List, Dict, Sequence

@dataclass
class BenchmarkTickersInfo:
    """
    Contains information related to the location and column for benchmark tickers.

    Attributes:
        dir (str): Directory path containing the tickers files.
        file (str): Name of the tickers file.
        column (str): Name of the column containing tickers in the file.
    """
    dir: str
    file: str
    column: str

@dataclass
class BenchmarkColumns:
    """
    Defines the column groups to process in the benchmark: date columns, numeric columns, string columns, columns to drop, and column renaming.

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
class BenchmarkLogger:
    """
    Logger configuration parameters for benchmark processing.

    Attributes:
        logname (str): Logger name.
        filename (str): Log file name.
    """
    logname: str
    filename: str

@dataclass
class BenchmarkConfig:
    """
    Complete configuration for a benchmark, including the name, tickers information,
    column structure, and logger configuration.

    Attributes:
        name (str): Name of the benchmark.
        tickers_info (BenchmarkTickersInfo): Information about the tickers to load.
        columns (BenchmarkColumns): Data column structure.
        logger (BenchmarkLogger): Logging parameters for this benchmark.
    """
    name: str
    tickers_info: BenchmarkTickersInfo
    columns: BenchmarkColumns
    logger: BenchmarkLogger
