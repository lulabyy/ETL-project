import logging
from helpers import helpers_config
from helpers import helpers_logger

from view.streamlit_view import PortfolioDashboard, Data

config = helpers_config.get_config()

# Setup du logger et récupération de l'objet logger
logger = helpers_logger.initLogger("main_streamlit_logger", config.log_path, "main_streamlit.log")
logging.getLogger("sqlalchemy.engine.Engine").disabled = True

def main_streamlit():
    logger.info("Démarrage de streamlit")

    data = Data(config)
    dashboard = PortfolioDashboard(config, data)
    dashboard.display()

if __name__ == "__main__":
    main_streamlit()
