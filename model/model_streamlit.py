from dataclasses import dataclass
from typing import List, Dict, Sequence

@dataclass
class StreamlitExportExcel:
    dir: str
    file: str

@dataclass
class StreamlitExportSQLite:
    dir: str
    file: str

@dataclass
class StreamlitExportConfig:
    excel: StreamlitExportExcel
    sqlite: StreamlitExportSQLite

@dataclass
class StreamlitPortfolioConfig:
    max_nb_tickers: int
    default_tickers: Sequence[str]
    default_weights: Dict[str, float]
    allowed_range: Sequence[float]
    enforce_100_percent: bool

@dataclass
class StreamlitPerformanceConfig:
    risk_free_rate: float
    trading_days_per_year: int
    metrics: Sequence[str]

@dataclass
class StreamlitLogger:
    logname: str
    filename: str

@dataclass
class StreamlitConfig:
    export: StreamlitExportConfig
    portfolio: StreamlitPortfolioConfig
    performance: StreamlitPerformanceConfig
    logger: StreamlitLogger



