from typing import Dict

import numpy as np
import pandas as pd

from model.model_config import Config

def compute_cumulative_return(close: pd.Series) -> float:
    """
    Calculate the cumulative return of a price series (e.g., portfolio or benchmark).
    - close must be a series (index = date)
    Args:
        close (pd.Series): price series (index = date).
    Returns:
        float: Cumulative return as a decimal (e.g., 0.12 for +12%).
    """
    return close.iloc[-1] / close.iloc[0] - 1

def compute_daily_returns(close: pd.Series) -> pd.Series:
    """
    Compute the daily returns of a price series.
    Args:
        close (pd.Series): price series (index = date).
    Returns:
        pd.Series: Daily returns (index = date).
    """
    return close.pct_change().dropna()


def compute_annualized_volatility(returns: pd.Series, trading_days_per_year:int) -> float:
    """
    Calculate the annualized volatility of a daily returns series.
    Args:
        returns (pd.Series): daily returns.
        trading_days_per_year (int): number of trading days per year (252 by default).
    Returns:
        float: Annualized volatility as a decimal (e.g., 0.15 for 15%).
    """
    sigma = returns.std(ddof=1)
    volatility_annualized = sigma * np.sqrt(trading_days_per_year)
    return volatility_annualized

def compute_sharpe(returns: pd.Series, risk_free_rate: float, trading_days_per_year) -> float:
    """
    Calculate the annualized Sharpe ratio.
    Args:
        returns (pd.Series): daily returns.
        risk_free_rate (float): annualized risk-free rate (e.g., 0.0).
        trading_days_per_year (int): number of trading days per year (252 by default).
    Returns:
        float: Annualized Sharpe ratio.
    Raises:
        ValueError: If volatility is zero (cannot compute Sharpe ratio).
    """
    mean_return = returns.mean() * trading_days_per_year
    vol = returns.std(ddof=1) * np.sqrt(trading_days_per_year)
    if vol == 0:
        raise ValueError("Volatility is zero, Sharpe ratio cannot be calculated.")
    return (mean_return - risk_free_rate) / vol


def compute_max_drawdown(close: pd.Series) -> float:
    """
    Calculate the maximum drawdown of a price series.
    Args:
        close (pd.Series): price series (index = date).
    Returns:
        float: Maximum drawdown as a decimal (e.g., -0.25 for -25%).
    """
    peak = close.cummax()
    drawdown = (close - peak) / peak
    return drawdown.min()

def percent(val: float) -> float:
    """
    Format a decimal value as a percentage with 2 decimals.
    Args:
        val (float): Value to format (e.g., 0.12 for 12%).
    Returns:
        float: Value in percent with 2 decimals (e.g., 12.34 for 0.1234).
    """
    return float(f"{val*100:.2f}")

def compute_indicators(prices: pd.Series, config: Config) -> Dict[str,float]:
    """
    Compute standard performance indicators for a price series.
    Args:
        prices (pd.Series): price series (index = date).
        config (Config): configuration object containing parameters.
    Returns:
        Dict[str, float]: Dictionary with indicator names as keys and values as floats.
    """
    returns = compute_daily_returns(prices)
    perf = compute_cumulative_return(prices)
    vol = compute_annualized_volatility(returns, config.streamlit.performance.trading_days_per_year)
    sharpe = compute_sharpe(returns, config.streamlit.performance.risk_free_rate, config.streamlit.performance.trading_days_per_year)
    max_dd = compute_max_drawdown(prices)
    return {
        "Cumulative Performance (%)": percent(perf),
        "Annualized Volatility (%)": percent(vol),
        "Max Drawdown (%)": percent(max_dd),
        "Sharpe Ratio": sharpe
    }
