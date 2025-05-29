"""
model_config.py

This module defines the main configuration dataclasses for the portfolio analytics application. 
It aggregates and structures all high-level settings, including main parameters, database configuration, 
ETL output configuration, benchmark setup, metadata, and Streamlit dashboard configuration.

These classes are typically instantiated by helpers_config.py from a YAML configuration file and provide 
type-safe access to all application settings across modules.

Do not execute this file directly; it is intended to be imported and used by configuration and application modules.
"""

from dataclasses import dataclass
from typing import List, Dict, Sequence

from model.model_benchmark import BenchmarkConfig
from model.model_metadata import MetadataConfig
from model.model_etl_output import EtlOutputConfig
from model.model_streamlit import StreamlitConfig

@dataclass
class MainParameters:
    """
    Main control parameters for the application.

    Attributes:
        output_version (str): Version identifier for output files.
        to_excel (bool): Whether to export results to Excel.
        to_sqlite (bool): Whether to export results to SQLite.
        log_dir (str): Directory for log file output.
    """
    output_version: str
    to_excel: bool
    to_sqlite: bool
    log_dir: str

@dataclass
class DatabaseConfig:
    """
    Database configuration parameters.

    Attributes:
        dir (str): Directory where the database file is stored.
        file (str): Name of the database file.
        benchmark_table (str): Table name for benchmark data.
        metadata_table (str): Table name for metadata.
    """
    dir: str
    file: str
    benchmark_table: str
    metadata_table: str

@dataclass
class Config:
    """
    Main configuration object aggregating all application settings.

    Attributes:
        root_path (str): Absolute root path of the application.
        log_path (str): Path where logs are stored.
        db_path (str): Path to the database directory.
        main_parameters (MainParameters): Main application parameters.
        database (DatabaseConfig): Database configuration.
        etl_output (EtlOutputConfig): ETL output configuration.
        benchmark (BenchmarkConfig): Benchmark configuration.
        metadata (MetadataConfig): Metadata configuration.
        streamlit (StreamlitConfig): Streamlit dashboard configuration.
    """
    root_path: str
    log_path: str
    db_path: str
    main_parameters: MainParameters
    database: DatabaseConfig
    etl_output: EtlOutputConfig
    benchmark: BenchmarkConfig
    metadata: MetadataConfig
    streamlit: StreamlitConfig
