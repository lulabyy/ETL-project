import numpy as np
import pandas as pd

def compute_cumulative_return(close: pd.Series) -> float:
    """
    Calculate the cumulative return of a price series (e.g., portfolio or benchmark).
    - close must be a series (index = date)
    """
    return close.iloc[-1] / close.iloc[0] - 1

def compute_daily_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().dropna()


def compute_annualized_volatility(returns: pd.Series, trading_days_per_year:int) -> float:
    """
    Calculate the annualized volatility of a daily returns series.

    Args:
        returns (pd.Series): daily returns.
        trading_days_per_year (int): number of trading days per year (252 by default).

    Returns:
        float: Annualized volatility.
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
    """
    mean_return = returns.mean() * trading_days_per_year
    vol = returns.std(ddof=1) * np.sqrt(trading_days_per_year)
    if vol == 0:
        raise ValueError("Volatility is zero, Sharpe ratio cannot be calculated.")
    return (mean_return - risk_free_rate) / vol


def compute_max_drawdown(close: pd.Series) -> float:
    """
    Calculate the maximum drawdown of a price series (portfolio close prices).
    Args:
        close (pd.Series): price series (index = date)
    Returns:
        float: maximum drawdown
    """
    peak = close.cummax()
    drawdown = (close - peak) / peak
    return drawdown.min()

def compute_indicators(prices, config):
    returns = compute_daily_returns(prices)
    perf = compute_cumulative_return(prices)
    vol = compute_annualized_volatility(returns, config.streamlit.performance.trading_days_per_year)
    sharpe = compute_sharpe(returns, config.streamlit.performance.risk_free_rate, config.streamlit.performance.trading_days_per_year)
    max_dd = compute_max_drawdown(prices)
    return {
        "Cumulative Performance": perf,
        "Annualized Volatility": vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd
    }

