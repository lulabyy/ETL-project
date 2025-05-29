"""
helpers_config.py

This module provides a helper function to load and construct the centralized configuration object
(`Config`) for the portfolio analytics application.

Key functionality:
- get_config: Loads application settings from the YAML configuration file, constructs instances of all
  data classes for benchmarks, metadata, ETL output, database, and Streamlit dashboard settings,
  and returns a fully-populated `Config` object.

Typical usage:
- Use this at the start of scripts or modules (such as main_streamlit.py, main_etl.py, or ETL modules)
  to access all application-wide parameters and paths in a type-safe, structured manner.

This module should be imported and used, not executed directly.

See main_etl.py for data pipeline orchestration and main_streamlit.py for the Streamlit dashboard entry point.
"""

import os

from model.model_config import (
    Config, 
    MainParameters, 
    DatabaseConfig
)
from model.model_benchmark import (
    BenchmarkConfig,
    BenchmarkTickersInfo,
    BenchmarkColumns,
    BenchmarkLogger
)
from model.model_metadata import (
    MetadataConfig,
    MetadataColumns,
    MetadataLogger
)
from model.model_etl_output import (
    EtlOutputConfig, 
    ExcelOutputConfig
)
from model.model_streamlit import (
    StreamlitConfig,
    StreamlitExportConfig,
    StreamlitExportExcel,
    StreamlitExportSQLite,
    StreamlitPortfolioConfig,
    StreamlitPerformanceConfig,
    StreamlitLogger
)

from helpers.helpers_serialize import get_serialized_data

def get_config() -> Config:
    """
    Load and construct the main Config object for the application from the YAML settings file.

    Args:
        None

    Returns:
        Config: The fully constructed configuration object containing all application settings.
    """
    # Récupérer le path absolute du root
    absolute_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Chargement de la config
    relative_config_path = "config/settings.yaml"

    path = os.path.join(absolute_root_path, relative_config_path)
    config = get_serialized_data(path)
    return Config(
        root_path = absolute_root_path,
        log_path =  os.path.join(absolute_root_path, config["main_parameters"]["log_dir"]),
        db_path = os.path.join(absolute_root_path, config["database"]["dir"]),

        main_parameters = MainParameters(**config["main_parameters"]),

        benchmark = BenchmarkConfig(
            name = config["benchmark"]["name"],
            tickers_info = BenchmarkTickersInfo(**config["benchmark"]["tickers_info"]),
            columns = BenchmarkColumns(**config["benchmark"]["columns"]),
            logger = BenchmarkLogger(**config["benchmark"]["logger"])
        ),

        database = DatabaseConfig(**config["database"]),

        metadata = MetadataConfig(
            dir = config["metadata"]["dir"],
            file = config["metadata"]["file"],
            columns = MetadataColumns(**config["metadata"]["columns"]),
            logger = MetadataLogger(**config["metadata"]["logger"])
        ),

        etl_output = EtlOutputConfig(
            excel = ExcelOutputConfig(**config["etl_output"]["excel"])
        ),
        streamlit = StreamlitConfig(
            export = StreamlitExportConfig(
                excel = StreamlitExportExcel(**config["streamlit"]["export"]["excel"]),
                sqlite = StreamlitExportSQLite(**config["streamlit"]["export"]["sqlite"])
            ),
            portfolio = StreamlitPortfolioConfig(**config["streamlit"]["portfolio"]),
            performance = StreamlitPerformanceConfig(**config["streamlit"]["performance"]),
            logger = StreamlitLogger(**config["streamlit"]["logger"])
        )
    )
