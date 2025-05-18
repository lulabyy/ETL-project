from dataclasses import dataclass
from typing import List, Dict, Sequence

@dataclass
class ExcelOutputConfig:
    dir: str
    file: str
    portfolio_sheet: str
    benchmark_sheet: str
    metadata_sheet: str

@dataclass
class EtlOutputConfig:
    excel: ExcelOutputConfig
