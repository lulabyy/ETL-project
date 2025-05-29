"""
run_streamlit.py

This script is a launcher for the Streamlit dashboard. It ensures that the Streamlit user interface
is started properly, even if the user is not familiar with the Streamlit CLI.

When you execute this script with:
    python run_streamlit.py
it will automatically run:
    streamlit run main_streamlit.py

This avoids errors that can occur if you try to launch the dashboard with:
    python main_streamlit.py

You should use this launcher or the Streamlit command directly to start the dashboard.

See main_streamlit.py for the Streamlit application code,
and main_etl.py to generate or refresh the dashboard data.
"""

import os

APP_ENTRY_POINT = 'main_streamlit.py'

dir_path = os.path.dirname(__file__)
path = os.path.join(dir_path, APP_ENTRY_POINT)

os.system('streamlit run "{}"'.format(path))
