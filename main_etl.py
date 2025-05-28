import os
import logging

from repository import (
    etl_metadata, etl_benchmark
)

from helpers import (
    helpers_logger, helpers_config
)

from view.streamlit_view import (
    PortfolioDashboard, Data
)

config = helpers_config.get_config()

# Logger setup and logger object retrieval
logger = helpers_logger.initLogger("main_logger", config.log_path, "main.log")
logging.getLogger("sqlalchemy.engine.Engine").disabled = True


def main_etl():
    logger.info("Starting the ETL pipeline")

    logger.info(f"Starting the Metadata ETL (see {config.metadata.logger.logname})")
    metadata_etl = etl_metadata.MetadataETL(config)
    metadata_etl.extract()
    metadata_etl.transform()
    metadata_etl.load()

    logger.info(f"Starting the Benchmark ETL (see {config.benchmark.logger.logname})")
    benchmark_etl = etl_benchmark.BenchmarkETL(config)
    benchmark_etl.extract()
    benchmark_etl.transform()
    benchmark_etl.load()

    logger.info("ETL pipeline completed")

    # -------------------------------------------------------------------------------------------

    logger.info("Starting Streamlit")

    data = Data(config)
    dashboard = PortfolioDashboard(config, data)
    dashboard.display()

    logger.info("Shutting down Streamlit")


if __name__ == "__main__":
    main_etl()