from dataclasses import dataclass
from typing import List, Dict, Sequence

from model.model_benchmark import BenchmarkConfig
from model.model_metadata import MetadataConfig
from model.model_etl_output import EtlOutputConfig
from model.model_streamlit import StreamlitConfig

@dataclass
class MainParameters:
    output_version: str
    to_excel: bool
    to_sqlite: bool
    log_dir: str

@dataclass
class DatabaseConfig:
    dir: str
    file: str
    benchmark_table: str
    metadata_table: str

@dataclass
class Config:
    root_path: str
    log_path: str
    db_path: str
    main_parameters: MainParameters
    database: DatabaseConfig
    etl_output: EtlOutputConfig
    benchmark: BenchmarkConfig
    metadata: MetadataConfig
    streamlit: StreamlitConfig
