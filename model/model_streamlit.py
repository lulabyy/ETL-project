"""
model_streamlit.py

This module defines dataclasses representing the Streamlit dashboard configuration for the portfolio analytics application.
It covers export options (Excel/SQLite), portfolio settings, performance metrics, and logging configuration.
These classes are typically instantiated from configuration files and used throughout the dashboard logic.

Do not execute this file directly; it is intended to be imported and used by Streamlit and configuration modules.
"""

from dataclasses import dataclass
from typing import List, Dict, Sequence

@dataclass
class StreamlitExportExcel:
    """
    Configuration for exporting Streamlit dashboard data to an Excel file.

    Attributes:
        dir (str): Directory where the Excel file will be saved.
        file (str): Name of the Excel file.
    """
    dir: str
    file: str

@dataclass
class StreamlitExportSQLite:
    """
    Configuration for exporting Streamlit dashboard data to a SQLite database.

    Attributes:
        dir (str): Directory where the SQLite database file will be saved.
        file (str): Name of the SQLite database file.
    """
    dir: str
    file: str

@dataclass
class StreamlitExportConfig:
    """
    Aggregates export configurations for the Streamlit dashboard.

    Attributes:
        excel (StreamlitExportExcel): Excel export configuration.
        sqlite (StreamlitExportSQLite): SQLite export configuration.
    """
    excel: StreamlitExportExcel
    sqlite: StreamlitExportSQLite

@dataclass
class StreamlitPortfolioConfig:
    """
    Portfolio settings for the Streamlit dashboard.

    Attributes:
        max_nb_tickers (int): Maximum number of tickers allowed in a portfolio.
        default_tickers (Sequence[str]): List of default ticker symbols.
    """
    max_nb_tickers: int
    default_tickers: Sequence[str]

@dataclass
class StreamlitPerformanceConfig:
    """
    Performance metrics configuration for the Streamlit dashboard.

    Attributes:
        risk_free_rate (float): Annualized risk-free rate used in performance calculations.
        trading_days_per_year (int): Number of trading days per year (typically 252).
        metrics (Sequence[str]): List of performance metric names to be calculated/displayed.
    """
    risk_free_rate: float
    trading_days_per_year: int
    metrics: Sequence[str]

@dataclass
class StreamlitLogger:
    """
    Logger configuration parameters for Streamlit dashboard operations.

    Attributes:
        logname (str): Logger name.
        filename (str): Log file name.
    """
    logname: str
    filename: str

@dataclass
class StreamlitConfig:
    """
    Complete Streamlit dashboard configuration, including export, portfolio, performance, and logging options.

    Attributes:
        export (StreamlitExportConfig): Export (Excel/SQLite) settings.
        portfolio (StreamlitPortfolioConfig): Portfolio settings for the dashboard.
        performance (StreamlitPerformanceConfig): Performance metric settings.
        logger (StreamlitLogger): Logger configuration.
    """
    export: StreamlitExportConfig
    portfolio: StreamlitPortfolioConfig
    performance: StreamlitPerformanceConfig
    logger: StreamlitLogger
