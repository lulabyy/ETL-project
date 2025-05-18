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
class StreamlitConfig:
    export: StreamlitExportConfig
