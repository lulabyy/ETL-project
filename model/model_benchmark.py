from dataclasses import dataclass
from typing import List, Dict, Sequence

@dataclass
class BenchmarkTickersInfo:
    dir: str
    file: str
    column: str

@dataclass
class BenchmarkColumns:
    columns_date: Sequence[str]
    columns_numeric: Sequence[str]
    columns_string: Sequence[str]
    columns_to_drop: Sequence[str]
    columns_new_names: Dict[str, str]

@dataclass
class BenchmarkLogger:
    logname: str
    filename: str

@dataclass
class BenchmarkConfig:
    name: str
    tickers_info: BenchmarkTickersInfo
    columns: BenchmarkColumns
    logger: BenchmarkLogger
