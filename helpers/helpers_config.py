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
    StreamlitPerformanceConfig,
    StreamlitLogger
)

from helpers.helpers_serialize import get_serialized_data

def get_config() -> EtlConfig:
    # Récupérer le path absolute du root
    absolute_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Chargement de la config
    relative_config_path = "config/settings.yaml"

    path = os.path.join(absolute_root_path, relative_config_path)
    config = get_serialized_data(path)
    return EtlConfig(
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
