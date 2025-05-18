import os

from repository import etl_metadata

from helpers import (
    helpers_logger, helpers_config
)

# Setup du logger et récupération de l'objet logger
logger = helpers_logger.initLogger()

# Récupérer le path absolute du root
absolute_root_path = os.path.dirname(os.path.abspath(__file__))

# Chargement de la config
relative_config_path = "config/settings.yaml"
config = helpers_config.get_config(absolute_root_path, relative_config_path)

def main():
    logger.info("Démarrage du pipeline ETL")
    # tu pourras mettre ici l'appel aux ETL market/benchmark/metadata
    logger.debug(f"Tickers chargés : {config.portfolio.tickers}")

    metadata_etl = etl_metadata.MetadataETL(config)
    metadata_etl.extract()
    metadata_etl.transform()
    metadata_etl.load()

if __name__ == "__main__":
    main()
