import os
import logging

from repository import (
    etl_metadata, etl_benchmark
)

from helpers import (
    helpers_logger, helpers_config
)

# Setup du logger et récupération de l'objet logger
logger = helpers_logger.initLogger()
logging.getLogger("sqlalchemy.engine.Engine").disabled = True

# Récupérer le path absolute du root
absolute_root_path = os.path.dirname(os.path.abspath(__file__))

# Chargement de la config
relative_config_path = "config/settings.yaml"
config = helpers_config.get_config(absolute_root_path, relative_config_path)

def main():
    logger.info("Démarrage du pipeline ETL")

    metadata_etl = etl_metadata.MetadataETL(config)
    metadata_etl.extract()
    metadata_etl.transform()
    metadata_etl.load()
    
    benchmark_etl = etl_benchmark.BenchmarkETL(config)
    benchmark_etl.extract()
    benchmark_etl.transform()
    benchmark_etl.load()

if __name__ == "__main__":
    main()
