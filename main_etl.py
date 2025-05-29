"""
main_etl.py

This script runs the complete ETL (Extract, Transform, Load) pipeline to prepare and update the data 
used by the dashboard. It should be executed from the command line using:

    python main_etl.py

This script does NOT launch the Streamlit user interface. It is only responsible for generating 
and refreshing the data sources.
Use this script before starting the dashboard to ensure the data is up to date.

To launch the dashboard, use 'streamlit run main_streamlit.py' or the run_streamlit.py launcher script.

See main_streamlit.py for the Streamlit application code.
"""

import logging

from repository import (
    etl_metadata, etl_benchmark
)

from helpers import (
    helpers_logger, helpers_config
)

config = helpers_config.get_config()

# Logger setup and logger object retrieval
logger = helpers_logger.initLogger("main_logger", config.log_path, "main.log")
logging.getLogger("sqlalchemy.engine.Engine").disabled = True


def main_etl() -> None:
    """
    Orchestrates the end-to-end ETL pipeline, including metadata and benchmark extraction, transformation,
    and loading.

    The function logs each major step of the pipeline for traceability. It instantiates and runs the ETL
    processes for metadata and benchmarks.

    Returns:
        None
    """
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

if __name__ == "__main__":
    main_etl()
