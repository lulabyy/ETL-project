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
class MetadataLogger:
    logname: str
    filename: str

@dataclass
class MetadataConfig:
    dir: str
    file : str
    columns: MetadataColumns
    logger: MetadataLogger
