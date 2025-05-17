import os

from model.model_config import (
    EtlConfig, MainParameters, MarketDataConfig, BenchmarkConfig,
    DatabaseConfig, MetadataConfig, MetadataColumns, ExportConfig
)
from helpers.helpers_serialize import get_serialized_data

def get_config_path(path: str) -> str:
    """
    This function returns the config file path
    :return: a full path as string
    """
    return os.path.join(os.getcwd(), path)

def get_config(path: str) -> EtlConfig:
    full_path = get_config_path(path)
    config = get_serialized_data(full_path)
    return EtlConfig(
        main_parameters=MainParameters(**config["main_parameters"]),
        market_data=MarketDataConfig(**config["market_data"]),
        benchmark=BenchmarkConfig(**config["benchmark"]),
        database=DatabaseConfig(**config["database"]),
        metadata=MetadataConfig(
            file_path=config["metadata"]["file_path"],
            columns=MetadataColumns(**config["metadata"]["columns"])
        ),
        export=ExportConfig(**config["export"])
    )
