from dataclasses import dataclass
from typing import List, Dict, Sequence

@dataclass
class PortfolioConfig:
    tickers: List[str]
    start_date: str
    end_date: str
