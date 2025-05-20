import os

from model.model_config import (
    EtlConfig, 
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
    StreamlitPerformanceConfig
)

from helpers.helpers_serialize import get_serialized_data

def get_config(root_path: str, relative_config_path) -> EtlConfig:
    path = os.path.join(root_path, relative_config_path)
    config = get_serialized_data(path)
    return EtlConfig(
        root_path=root_path,
        
        main_parameters = MainParameters(**config["main_parameters"]),

        benchmark = BenchmarkConfig(
            ticker = config["benchmark"]["ticker"],
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
            performance = StreamlitPerformanceConfig(**config["streamlit"]["performance"])
        )
    )
