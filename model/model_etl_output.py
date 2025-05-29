"""
model_etl_output.py

This module defines dataclasses representing the output configuration for the ETL (Extract, Transform, Load) pipeline
in the portfolio analytics application. It specifies how and where the transformed data should be exported,
including details for Excel file outputs.

These classes are typically instantiated from configuration files and used by the ETL process to determine
output paths, filenames, and sheet names.

Do not execute this file directly; it is intended to be imported and used by ETL and configuration modules.
"""

from dataclasses import dataclass
from typing import List, Dict, Sequence

@dataclass
class ExcelOutputConfig:
    """
    Configuration for exporting ETL output to an Excel file.

    Attributes:
        dir (str): Directory where the Excel file will be saved.
        file (str): Name of the Excel file.
        benchmark_sheet (str): Sheet name for benchmark data.
        metadata_sheet (str): Sheet name for metadata.
    """
    dir: str
    file: str
    benchmark_sheet: str
    metadata_sheet: str

@dataclass
class EtlOutputConfig:
    """
    Configuration for ETL output, currently supporting Excel file output.

    Attributes:
        excel (ExcelOutputConfig): The Excel export configuration.
    """
    excel: ExcelOutputConfig
