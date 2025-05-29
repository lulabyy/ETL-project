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

# Prevent direct execution
def is_streamlit():
    # Streamlit sets this variable when running the script
    return any(
        key.startswith('STREAMLIT_') and 'RUN' in key
        for key in os.environ
    )

if __name__ == "__main__" and not is_streamlit():
    print(
        "This script is not intended to be run directly.\n"
        "Please use the following command to launch the dashboard:\n"
        "    streamlit run main_streamlit.py\n"
        "Or use the run_streamlit.py launcher provided."
    )
    sys.exit(1)

main_streamlit()
