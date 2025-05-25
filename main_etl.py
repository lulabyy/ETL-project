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

# Setup du logger et récupération de l'objet logger
logger = helpers_logger.initLogger("main_logger", config.log_path, "main.log")
logging.getLogger("sqlalchemy.engine.Engine").disabled = True

def main_etl():
    logger.info("Démarrage du pipeline ETL")

    logger.info(f"Démarrage du ETL Metadata (voir {config.metadata.logger.logname})")
    metadata_etl = etl_metadata.MetadataETL(config)
    metadata_etl.extract()
    metadata_etl.transform()
    metadata_etl.load()
    
    logger.info(f"Démarrage du ETL Benchmark (voir {config.benchmark.logger.logname})")
    benchmark_etl = etl_benchmark.BenchmarkETL(config)
    benchmark_etl.extract()
    benchmark_etl.transform()
    benchmark_etl.load()

    logger.info("Pipeline ETL terminé")

    #-------------------------------------------------------------------------------------------

    logger.info("Démarrage de streamlit")

    data = Data(config)
    dashboard = PortfolioDashboard(config, data)
    dashboard.display()

    logger.info("Fermeture de streamlit")


if __name__ == "__main__":
    main_etl()
