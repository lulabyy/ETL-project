import numpy as np
import pandas as pd

def compute_cumulative_return(close: pd.Series) -> float:
    """
    Calcule la performance cumulée d'une série de prix (ex: portefeuille ou benchmark)
    - close doit être une série (index = date)
    """
    return close.iloc[-1] / close.iloc[0] - 1

def compute_daily_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().dropna()


def compute_annualized_volatility(returns: pd.Series, trading_days_per_year) -> float:
    """
    Calcule la volatilité annualisée d'une série de rendements journaliers.

    Args:
        returns (pd.Series): rendements journaliers.
        trading_days_per_year (int): nombre de jours de bourse par an (252 par défaut).

    Returns:
        float: Volatilité annualisée.
    """
    sigma = returns.std(ddof=1)
    volatility_annualized = sigma * np.sqrt(trading_days_per_year)
    return volatility_annualized

def compute_sharpe(returns: pd.Series, risk_free_rate: float = 0.0, trading_days_per_year) -> float:
    """
    Calcule le ratio de Sharpe annualisé.
    Args:
        returns (pd.Series): rendements journaliers.
        risk_free_rate (float): taux sans risque annualisé (ex: 0.0).
        trading_days_per_year (int): nombre de jours de bourse/an (252 par défaut).
    Returns:
        float: Sharpe ratio annualisé.
    """
    mean_return = returns.mean() * trading_days_per_year
    vol = returns.std(ddof=1) * np.sqrt(trading_days_per_year)
    if vol == 0:
        raise ValueError("La volatilité est nulle, le ratio de Sharpe ne peut pas être calculé.")
    return (mean_return - risk_free_rate) / vol

import pandas as pd

def compute_max_drawdown(close: pd.Series) -> float:
    """
    Calcule le maximum drawdown d'une série de prix (close d'un portefeuille).
    Args:
        close (pd.Series): série des prix (index = date)
    Returns:
        float: maximum drawdown
    """
    peak = close.cummax()
    drawdown = (close - peak) / peak
    return drawdown.min()