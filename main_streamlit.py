"""
main_streamlit.py

This script launches the Streamlit user interface for portfolio analytics and visualization.
It must be started via the command:
    streamlit run main_streamlit.py
or by running the provided run_streamlit.py launcher.

------------------------------------------------------------------------------------------
Do NOT run this script directly with: python main_streamlit.py
If you do so, the user interface will not start properly.
------------------------------------------------------------------------------------------

See main_etl.py to generate and update the necessary data for the dashboard.
"""

import os
import sys
import logging
from helpers import helpers_config
from helpers import helpers_logger

from view.streamlit_view import PortfolioDashboard, Data

config = helpers_config.get_config()

# Logger setup
logger = helpers_logger.initLogger("main_logger", config.log_path, "main.log")
logging.getLogger("sqlalchemy.engine.Engine").disabled = True

def main_streamlit() -> None:
    """
    Launch the Streamlit dashboard application.

    This function initializes the data and dashboard components, and displays the interactive 
    Streamlit dashboard for portfolio analysis. It also logs the start of the Streamlit process.

    Returns:
        None
    """
    logger.info("Starting Streamlit")

    data = Data(config)
    dashboard = PortfolioDashboard(data.df_merged, config)
    dashboard.display()

main_streamlit()
