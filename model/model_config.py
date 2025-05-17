from dataclasses import dataclass
from typing import List, Dict, Sequence

@dataclass
class MetadataColumns:
    columns_date: Sequence[str]
    columns_numeric: Sequence[str]
    columns_string: Sequence[str]
    columns_to_drop: Sequence[str]
    columns_new_names: Dict[str, str]

@dataclass
class MetadataConfig:
    file_path: str
    columns: MetadataColumns

@dataclass
class MarketDataConfig:
    tickers: List[str]
    start_date: str
    end_date: str

@dataclass
class BenchmarkConfig:
    ticker: str

@dataclass
class DatabaseConfig:
    path: str
    market_table: str
    benchmark_table: str
    metadata_table: str
    output_dir: str

@dataclass
class ExportConfig:
    export_excel_enabled: bool
    export_csv_enabled: bool
    file_excel_path: str
    file_csv_path: str

@dataclass
class MainParameters:
    output_version: str
    to_excel: bool
    to_sqlite: bool

@dataclass
class EtlConfig:
    main_parameters: MainParameters
    market_data: MarketDataConfig
    benchmark: BenchmarkConfig
    database: DatabaseConfig
    metadata: MetadataConfig
    export: ExportConfig
