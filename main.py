from pathlib import Path
import os

from helpers import helpers_logger
from helpers import helpers_config

# Setup du logger et récupération de l'objet logger
logger = helpers_logger.setupLogger()

# Chargement de la config
config_path = "config/settings.yaml"
config = helpers_config.get_config(config_path)

def main():
    logger.info("Démarrage du pipeline ETL")
    # tu pourras mettre ici l'appel aux ETL market/benchmark/metadata
    logger.debug(f"Tickers chargés : {config.market_data.tickers}")

if __name__ == "__main__":
    main()